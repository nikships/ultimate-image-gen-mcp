"""Two-pass difference-matting for high-quality transparent backgrounds.

Gemini cannot emit a real alpha channel, so transparency is recovered as a
post-processing step. This module implements the **two-pass difference matte**,
which produces materially better edges than single-pass chromakey for glow,
glass, soft shadows, and anti-aliased detail — at the cost of a second model
call (≈2x tokens/latency).

The technique
-------------
1. **Pass 1 — generate on white.** The subject is rendered on a pure white
   (``#FFFFFF``) background.
2. **Pass 2 — edit to black.** That image is fed back to the model with an edit
   instruction that changes *only* the background to pure black (``#000000``)
   and preserves the subject pixel-for-pixel.
3. **Difference matte.** With the subject identical in both frames, alpha is
   recovered analytically. For a pixel composited over a background ``B`` with
   foreground ``FG`` and opacity ``α``::

       obs_white = α·FG + (1−α)·255
       obs_black = α·FG + (1−α)·0   = α·FG

   Subtracting cancels ``FG`` regardless of subject colour::

       obs_white − obs_black = (1−α)·255   (identical on every channel)

   Because that difference is *identical on every channel* for a clean
   composite, the per-channel value alone gives alpha — the Euclidean norm
   across channels reduces to ``√3·d`` over a ``√3·255`` span, i.e. the same
   ``d/255``. So we use the channel mean (robust to minor sensor noise)::

       α = 1 − mean(obs_white − obs_black) / 255

   Any genuine cross-channel disagreement means the subject drifted between
   passes; that is captured separately by the alignment metric below rather
   than corrupting the alpha estimate.

   The foreground colour is then un-premultiplied from the black frame
   (``B = 0`` ⇒ ``obs_black = α·FG``)::

       FG = obs_black / α

Why it beats chromakey: there is no colour key, so no green spill/halo; alpha is
fractional (true soft edges, glass, glow); and faint shadows survive as
low-alpha dark pixels.

Alignment caveat
----------------
The maths assumes the edit changed **only** the background. If the model drifts
(moves/relights/recolours the subject), the matte degrades. Two channel-spread
signals detect this — see :func:`extract_alpha_two_pass`, which always returns a
result but flags ``aligned=False`` with loud warnings when the passes disagree.

Implementation is Pillow-only (``ImageChops``/``ImageMath``/``ImageStat`` — all
C-level, no Python per-pixel loop, no numpy), consistent with the rest of the
package.
"""

from __future__ import annotations

import base64
import io
import logging
from dataclasses import dataclass, field

from PIL import Image, ImageChops, ImageMath, ImageStat

logger = logging.getLogger(__name__)

# --- Constants ---------------------------------------------------------------

WHITE_HEX = "#FFFFFF"
BLACK_HEX = "#000000"

#: Alpha values (0-1) below this are snapped to fully transparent to kill faint
#: background haze from a not-perfectly-uniform generated backdrop.
DEFAULT_ALPHA_FLOOR = 0.02

#: Combined channel-spread error (0-1) above which the two passes are treated as
#: misaligned (subject drifted/relit between passes).
DEFAULT_ALIGNMENT_WARN_THRESHOLD = 0.06

# Pillow renamed the evaluator; prefer the non-deprecated entry point.
_img_eval = getattr(ImageMath, "unsafe_eval", None) or ImageMath.eval


@dataclass
class DifferenceMattingResult:
    """Outcome of a two-pass difference-matte extraction."""

    image: Image.Image
    """The recovered RGBA image with a true (fractional) alpha channel."""

    alignment_error: float
    """Combined channel-spread error (0-1). 0 == passes agree perfectly."""

    aligned: bool
    """Whether the two passes agree well enough to trust the matte."""

    transparent_ratio: float
    """Fraction of pixels (0-1) that ended up at least partly transparent."""

    warnings: list[str] = field(default_factory=list)
    """Best-effort human-readable warnings (misalignment, etc.)."""


def build_white_background_prompt(prompt: str) -> str:
    """Wrap a user prompt with pass-1 (white background) instructions.

    Args:
        prompt: The original subject description.

    Returns:
        Prompt asking for the subject on a pure white background with crisp,
        opaque edges and no baked-in outline/halo/bezel/shadow.
    """
    subject = prompt.strip()
    return (
        f"{subject}\n\n"
        "BACKGROUND REQUIREMENTS (the background will be removed afterwards via "
        "a two-pass difference matte):\n"
        f"1. Render the subject on a solid, flat, perfectly uniform pure WHITE "
        f"background — EXACTLY hex {WHITE_HEX} (RGB 255, 255, 255). No gradient, "
        "no vignette, no texture, no scenery.\n"
        "2. Do NOT draw any outline, ring, halo, stroke, bezel, frame, or drop "
        "shadow around the subject's outer silhouette.\n"
        "3. Keep the subject's own colours distinct from the pure-white "
        "backdrop so its edges read clearly."
    )


def build_to_black_edit_prompt() -> str:
    """Return the pass-2 edit instruction (recolour the background to black).

    The wording is deliberately emphatic about preserving the subject, because
    the entire difference-matte technique depends on the subject being identical
    between the two passes.
    """
    return (
        f"Change ONLY the background from white to solid pure black — EXACTLY hex "
        f"{BLACK_HEX} (RGB 0, 0, 0). Keep EVERYTHING else pixel-for-pixel "
        "identical: the subject's exact shape, position, scale, rotation, "
        "colours, lighting, glow, shadows, and every fine detail must not change "
        "at all. Do not move, resize, recolour, restyle, redraw, or re-light the "
        "subject. Only the background colour changes; the subject is untouched."
    )


def _alignment_signals(white_rgb: Image.Image, black_rgb: Image.Image) -> tuple[float, float]:
    """Return ``(negative_mean, channel_spread_mean)`` drift signals, each 0-255.

    Under the ideal model ``obs_white − obs_black = (1−α)·(255,255,255)``, which
    is (a) non-negative on every channel and (b) identical across channels for
    any subject colour/opacity. So two cheap, subject-independent drift signals:

    * **negative_mean** — mean of ``max(black − white, 0)`` across channels.
      Light should never *increase* going from white to black bg; nonzero here
      means the subject changed.
    * **channel_spread_mean** — mean per-pixel ``max_c − min_c`` of
      ``max(white − black, 0)``. Should be ~0 for a clean composite; nonzero
      means the subject's colour changed between passes.
    """
    pos = ImageChops.subtract(white_rgb, black_rgb)  # max(white-black, 0) per channel
    neg = ImageChops.subtract(black_rgb, white_rgb)  # max(black-white, 0) per channel

    nr, ng, nb = neg.split()
    neg_max = ImageChops.lighter(ImageChops.lighter(nr, ng), nb)
    negative_mean = ImageStat.Stat(neg_max).mean[0]

    pr, pg, pb = pos.split()
    pos_max = ImageChops.lighter(ImageChops.lighter(pr, pg), pb)
    pos_min = ImageChops.darker(ImageChops.darker(pr, pg), pb)
    spread = ImageChops.subtract(pos_max, pos_min)
    channel_spread_mean = ImageStat.Stat(spread).mean[0]

    return negative_mean, channel_spread_mean


def extract_alpha_two_pass(
    image_on_white: Image.Image,
    image_on_black: Image.Image,
    *,
    alpha_floor: float = DEFAULT_ALPHA_FLOOR,
    alignment_warn_threshold: float = DEFAULT_ALIGNMENT_WARN_THRESHOLD,
) -> DifferenceMattingResult:
    """Recover a transparent RGBA image from white- and black-background passes.

    Args:
        image_on_white: The pass-1 image (subject on white).
        image_on_black: The pass-2 image (same subject on black).
        alpha_floor: Alpha (0-1) below which a pixel is snapped fully
            transparent, to remove faint background haze.
        alignment_warn_threshold: Combined channel-spread error (0-1) above
            which the passes are flagged misaligned.

    Returns:
        A :class:`DifferenceMattingResult`. The image is always returned (even
        when misaligned), per the warn-but-return contract.
    """
    white = image_on_white.convert("RGB")
    black = image_on_black.convert("RGB")

    warnings: list[str] = []
    if white.size != black.size:
        # The edit pass occasionally returns a slightly different resolution;
        # resample the black frame to the white frame's grid so the per-pixel
        # subtraction lines up. Note it — large mismatches imply drift.
        warnings.append(
            f"Pass dimensions differed (white={white.size}, black={black.size}); "
            "resized the black pass to match. Edges may be slightly softer."
        )
        black = black.resize(white.size, Image.Resampling.LANCZOS)

    # --- Alpha from the white↔black difference ------------------------------
    # For a clean composite, white-black = (1-α)·255 on every channel, so the
    # channel mean of the difference gives (1-α)·255 directly (no sqrt needed).
    # Averaging the three channels also suppresses minor per-channel noise.
    dr, dg, db = ImageChops.difference(white, black).split()
    alpha = _img_eval(
        "convert(255 - ((r + g + b) / 3), 'L')",
        r=dr,
        g=dg,
        b=db,
    )

    # Snap sub-floor alpha to 0 to drop faint background haze.
    floor_val = int(max(0.0, min(1.0, alpha_floor)) * 255)
    if floor_val > 0:
        alpha = alpha.point(lambda p, f=floor_val: p if p >= f else 0)

    # --- Un-premultiply foreground colour from the black frame ---------------
    # On black, obs_black = α·FG ⇒ FG = obs_black · 255 / alpha. max(a,1) avoids
    # div-by-0; where α≈0 the black-frame colour is also ≈0, so FG → ~0 anyway.
    bch = black.split()
    recovered = [
        _img_eval(
            "convert(min((c * 255) / max(a, 1), 255), 'L')",
            c=bch[i],
            a=alpha,
        )
        for i in range(3)
    ]
    result_img = Image.merge("RGBA", (recovered[0], recovered[1], recovered[2], alpha))

    # --- Confidence / alignment metrics --------------------------------------
    negative_mean, channel_spread_mean = _alignment_signals(white, black)
    alignment_error = (negative_mean + channel_spread_mean) / 255.0
    aligned = alignment_error <= alignment_warn_threshold

    transparent_pixels = alpha.point(lambda p: 255 if p < 255 else 0).histogram()[255]
    total = white.width * white.height
    transparent_ratio = (transparent_pixels / total) if total else 0.0

    if not aligned:
        warnings.append(
            f"Two-pass alignment is LOW (error={alignment_error:.3f} > "
            f"{alignment_warn_threshold:.3f}): the subject likely shifted, "
            "recoloured, or re-lit between the white and black passes, so the "
            "transparency matte may show ghosting or color fringing. The "
            "difference-matte result is still returned as requested; regenerate "
            "if the edges look wrong."
        )
    if transparent_ratio < 0.01:
        warnings.append(
            f"Almost nothing was made transparent ({transparent_ratio:.1%}); the "
            "background may not have been pure white, or the subject fills the frame."
        )

    return DifferenceMattingResult(
        image=result_img,
        alignment_error=alignment_error,
        aligned=aligned,
        transparent_ratio=transparent_ratio,
        warnings=warnings,
    )


def extract_alpha_from_base64(
    image_on_white_b64: str,
    image_on_black_b64: str,
    *,
    alpha_floor: float = DEFAULT_ALPHA_FLOOR,
    alignment_warn_threshold: float = DEFAULT_ALIGNMENT_WARN_THRESHOLD,
) -> DifferenceMattingResult:
    """Decode two base64 frames and run :func:`extract_alpha_two_pass`.

    Args:
        image_on_white_b64: Base64-encoded pass-1 image (subject on white).
        image_on_black_b64: Base64-encoded pass-2 image (subject on black).
        alpha_floor: See :func:`extract_alpha_two_pass`.
        alignment_warn_threshold: See :func:`extract_alpha_two_pass`.

    Returns:
        A :class:`DifferenceMattingResult`.
    """
    with Image.open(io.BytesIO(base64.b64decode(image_on_white_b64))) as wimg:
        wimg.load()
        white = wimg.convert("RGB")
    with Image.open(io.BytesIO(base64.b64decode(image_on_black_b64))) as bimg:
        bimg.load()
        black = bimg.convert("RGB")
    return extract_alpha_two_pass(
        white,
        black,
        alpha_floor=alpha_floor,
        alignment_warn_threshold=alignment_warn_threshold,
    )
