"""Best-effort transparent-background post-processing.

Gemini does not emit true alpha-channel / transparent pixels directly, so
transparent-background output is implemented entirely as a post-processing step
that runs *after* generation. The default (and currently only) strategy is a
**chromakey** pipeline:

1. The image is generated on a solid chromakey-green (``#00FF00``) background
   with crisp opaque subject edges and explicitly NO outline, ring, halo, bezel
   or frame around the subject (see :func:`build_chromakey_prompt`). This makes
   the matting problem easier without inducing the model to bake a visible
   white halo or chrome bezel into the result — it is not "prompting for
   transparency".
2. The green background is detected in **HSV** colour space (which separates
   hue from saturation/brightness) and removed, keying on a tight hue band that
   is *also* highly saturated and bright. This preserves subject greens such as
   logo or foliage greens, which are less saturated / darker than the
   chromakey.
3. The resulting matte is grown by a few pixels (morphological dilation) to
   swallow the anti-aliased green halo around the subject edges.
4. The result is returned as an RGBA image that can be saved as a PNG or WebP
   with a real alpha channel.

The implementation depends only on Pillow (already a core dependency), so no
heavy ML models or extra downloads are required. Background removal is
deliberately treated as *best-effort*: callers receive warnings (e.g. when
almost nothing or almost everything was removed) instead of silent failures.

This module is intentionally self-contained (standard library + Pillow only,
with ``from __future__ import annotations``) so it can be imported and unit
tested in isolation.
"""

from __future__ import annotations

import base64
import io
import logging
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageChops, ImageFilter

logger = logging.getLogger(__name__)

# --- Chromakey constants -----------------------------------------------------

#: Hex colour the model is asked to paint the background with.
CHROMAKEY_GREEN_HEX = "#00FF00"
#: Same colour as an RGB tuple.
CHROMAKEY_GREEN_RGB = (0, 255, 0)

# HSV thresholds expressed in Pillow's 0-255 per-channel space.
# Pillow maps hue 0-360deg -> 0-255, so pure green (120deg) lands on ~85.
#: Hue centre for pure green (120deg) in Pillow's 0-255 scale.
DEFAULT_HUE_CENTER = 85
#: Half-width of the accepted hue band (~25deg) in Pillow's 0-255 scale.
DEFAULT_HUE_TOLERANCE = 18
#: Minimum saturation (~75%) for a pixel to count as chromakey green.
DEFAULT_MIN_SATURATION = 191
#: Minimum value/brightness (~70%) for a pixel to count as chromakey green.
DEFAULT_MIN_VALUE = 179

#: Maps the user-facing matting-quality level to a dilation pass count. More
#: dilation removes green fringing more aggressively at the cost of eating
#: slightly into the subject edge.
MATTING_QUALITY_DILATION = {"fast": 1, "balanced": 2, "best": 3}

# Sanity thresholds used to flag low-confidence results.
_MIN_REMOVED_RATIO = 0.02
_MAX_REMOVED_RATIO = 0.98


@dataclass
class BackgroundRemovalResult:
    """Outcome of a background-removal pass."""

    image: Image.Image
    """The processed RGBA image with the background made transparent."""

    removed_ratio: float
    """Fraction of pixels (0.0-1.0) that were made transparent."""

    background_removed: bool
    """Whether a plausible background was detected and removed."""

    mode: str = "chroma"
    """The removal strategy that produced this result."""

    warnings: list[str] = field(default_factory=list)
    """Human-readable best-effort warnings (low/high confidence, etc.)."""


def build_chromakey_prompt(prompt: str) -> str:
    """Wrap a user prompt with chromakey-green generation instructions.

    The returned prompt asks the model to render the subject on a solid
    ``#00FF00`` background with razor-sharp opaque edges and **no outline,
    halo, bezel or frame** around the subject. Anti-aliased green fringing is
    handled by the post-processing dilation step, so we no longer ask the model
    to bake in a white outline — that instruction was being interpreted as a
    visible chrome/metallic ring around app icons and badged subjects.

    Args:
        prompt: The original user prompt describing the subject.

    Returns:
        An augmented prompt string optimised for chromakey extraction.
    """
    subject = prompt.strip()
    return (
        f"{subject}\n\n"
        "CRITICAL CHROMAKEY REQUIREMENTS (the background will be removed "
        "programmatically after generation):\n"
        f"1. BACKGROUND: Render the subject on a solid, flat, uniform chromakey "
        f"green background. Use EXACTLY hex color {CHROMAKEY_GREEN_HEX} "
        "(RGB 0, 255, 0). The entire background must be this single pure green "
        "with NO gradients, NO shadows, and NO lighting effects.\n"
        "2. CRISP OPAQUE EDGES — NO OUTLINE: The subject must meet the green "
        "background with razor-sharp, fully opaque edges. Do NOT draw any "
        "outline, ring, halo, stroke, bezel, frame, glass trim, metallic "
        "border, drop shadow, or glow around the subject's outer silhouette. "
        "The post-process keys out anti-aliased green fringing automatically.\n"
        "3. NO GREEN ON SUBJECT: The subject itself should avoid pure chromakey "
        "green. If green is needed, use a clearly different shade such as dark "
        "forest green or teal.\n"
        "4. PLACEMENT: Center the subject unless the user prompt explicitly "
        "asks for full-bleed framing (e.g. an app-icon squircle whose rounded "
        "corners touch the canvas edges)."
    )


def remove_green_screen(
    image: Image.Image,
    *,
    hue_center: int = DEFAULT_HUE_CENTER,
    hue_tolerance: int = DEFAULT_HUE_TOLERANCE,
    min_saturation: int = DEFAULT_MIN_SATURATION,
    min_value: int = DEFAULT_MIN_VALUE,
    dilation_iterations: int = 2,
) -> BackgroundRemovalResult:
    """Remove a chromakey-green background from an image using HSV detection.

    A pixel is treated as background when its hue is within ``hue_tolerance`` of
    ``hue_center`` *and* it is highly saturated (``>= min_saturation``) *and*
    bright (``>= min_value``). The combined gate is what lets subject greens
    (logos, foliage), which are typically less saturated or darker, survive.

    Args:
        image: The source image (any mode; converted to RGB internally).
        hue_center: Target hue in Pillow's 0-255 scale (85 == pure green).
        hue_tolerance: Half-width of the accepted hue band (0-255 scale).
        min_saturation: Minimum saturation (0-255) to count as background.
        min_value: Minimum brightness (0-255) to count as background.
        dilation_iterations: Number of 3x3 dilation passes applied to the
            background mask to remove anti-aliased green fringing.

    Returns:
        A :class:`BackgroundRemovalResult` carrying the RGBA image, the removed
        ratio, a ``background_removed`` flag, and any best-effort warnings.
    """
    rgb = image.convert("RGB")
    hue, sat, val = rgb.convert("HSV").split()

    low = hue_center - hue_tolerance
    high = hue_center + hue_tolerance
    # Modulo arithmetic accepts the hue band and transparently handles the
    # 0/255 hue wraparound (e.g. reds) in a single branchless expression.
    hue_mask = hue.point(lambda p: 255 if (p - low) % 256 <= high - low else 0)

    sat_mask = sat.point(lambda p: 255 if p >= min_saturation else 0)
    val_mask = val.point(lambda p: 255 if p >= min_value else 0)

    # ImageChops.multiply on 0/255 masks behaves like a logical AND.
    background_mask = ImageChops.multiply(ImageChops.multiply(hue_mask, sat_mask), val_mask)

    for _ in range(max(0, dilation_iterations)):
        background_mask = background_mask.filter(ImageFilter.MaxFilter(3))

    alpha = ImageChops.invert(background_mask)
    result = rgb.convert("RGBA")
    result.putalpha(alpha)

    total_pixels = rgb.width * rgb.height
    # The mask is a binary single-channel image, so histogram()[255] counts the
    # background pixels in C — far faster/lighter than getdata() at 2K/4K.
    removed_pixels = background_mask.histogram()[255]
    removed_ratio = (removed_pixels / total_pixels) if total_pixels else 0.0

    warnings: list[str] = []
    background_removed = removed_ratio >= _MIN_REMOVED_RATIO
    if not background_removed:
        warnings.append(
            "Little or no chromakey-green background was detected "
            f"({removed_ratio:.1%} removed); the output may be effectively opaque."
        )
    elif removed_ratio >= _MAX_REMOVED_RATIO:
        warnings.append(
            f"Almost the entire image was removed ({removed_ratio:.1%}); the "
            "subject may contain chromakey green or be too small."
        )

    return BackgroundRemovalResult(
        image=result,
        removed_ratio=removed_ratio,
        background_removed=background_removed,
        mode="chroma",
        warnings=warnings,
    )


def make_transparent(
    image: Image.Image,
    *,
    mode: str = "chroma",
    matting_quality: str = "balanced",
) -> BackgroundRemovalResult:
    """Produce a transparent-background RGBA image using the requested strategy.

    Args:
        image: The source PIL image.
        mode: Removal strategy. ``"chroma"`` (or ``"auto"``) uses the chromakey
            HSV pipeline. Other modes are reserved for future work.
        matting_quality: ``"fast"``, ``"balanced"`` or ``"best"`` — controls how
            aggressively edge fringing is removed via dilation.

    Returns:
        A :class:`BackgroundRemovalResult`.

    Raises:
        ValueError: If an unsupported ``mode`` is requested.
    """
    resolved_mode = "chroma" if mode in ("auto", "chroma") else mode
    if resolved_mode != "chroma":
        raise ValueError(
            f"Unsupported background_removal_mode '{mode}'. "
            "Only 'chroma' (or 'auto') is currently implemented."
        )

    dilation = MATTING_QUALITY_DILATION.get(matting_quality, MATTING_QUALITY_DILATION["balanced"])
    return remove_green_screen(image, dilation_iterations=dilation)


def remove_background_from_base64(
    image_data: str,
    *,
    mode: str = "chroma",
    matting_quality: str = "balanced",
) -> BackgroundRemovalResult:
    """Decode base64 image data and run :func:`make_transparent` on it.

    Args:
        image_data: Base64-encoded image bytes (as produced by the generator).
        mode: Removal strategy (see :func:`make_transparent`).
        matting_quality: Matting quality level (see :func:`make_transparent`).

    Returns:
        A :class:`BackgroundRemovalResult`.
    """
    raw = base64.b64decode(image_data)
    with Image.open(io.BytesIO(raw)) as img:
        img.load()
        return make_transparent(img, mode=mode, matting_quality=matting_quality)


def save_transparent_image(image: Image.Image, output_path: Path, alpha_output_format: str) -> Path:
    """Save an RGBA image to disk in an alpha-capable format.

    Args:
        image: The RGBA image to save.
        output_path: Destination path (its suffix is normalised to the format).
        alpha_output_format: ``"png"`` or ``"webp"``.

    Returns:
        The path the image was written to.

    Raises:
        ValueError: If ``alpha_output_format`` does not support alpha.
    """
    fmt = alpha_output_format.lower()
    if fmt not in ("png", "webp"):
        raise ValueError(
            f"alpha_output_format '{alpha_output_format}' does not support transparency; "
            "use 'png' or 'webp'."
        )

    rgba = image if image.mode == "RGBA" else image.convert("RGBA")
    save_format = "PNG" if fmt == "png" else "WEBP"
    output_path = output_path.with_suffix(f".{fmt}")
    # The destination dir may not exist yet (e.g. preserve_original=False, so the
    # original save that would have created it was skipped).
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rgba.save(output_path, format=save_format)
    logger.info("Saved transparent image to %s", output_path)
    return output_path
