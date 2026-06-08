"""
Image generation tool for Gemini 3.1 Flash Image.

This module provides MCP tools for professional image generation using Google's
Gemini 3.1 Flash Image with advanced reasoning, high-resolution output (512px-4K),
reference image support, Google Search grounding (Web & Image), and thinking mode.
"""

import base64
import functools
import json
import logging
from pathlib import Path
from typing import Any

from ..config import get_settings
from ..core import (
    coerce_image_paths,
    validate_alpha_output_format,
    validate_aspect_ratio,
    validate_background_removal_mode,
    validate_image_format,
    validate_image_size,
    validate_matting_quality,
    validate_prompt,
    validate_reference_image,
    validate_reference_images_count,
)
from ..services import ImageService
from ..services.background_removal import (
    build_chromakey_prompt,
    remove_background_from_base64,
    save_transparent_image,
)

logger = logging.getLogger(__name__)


@functools.lru_cache
def get_image_service(api_key: str, enable_enhancement: bool, timeout: int) -> ImageService:
    """Get or create a cached ImageService instance."""
    return ImageService(
        api_key=api_key,
        enable_enhancement=enable_enhancement,
        timeout=timeout,
    )


async def generate_image_tool(
    prompt: str,
    aspect_ratio: str = "1:1",
    image_size: str = "2K",
    output_format: str = "png",
    reference_image_paths: str | list[str] | None = None,
    reference_images_data: list[str] | None = None,
    enable_google_search: bool = False,
    enable_image_search: bool = False,
    response_modalities: list[str] | None = None,
    thinking_level: str = "minimal",
    save_to_disk: bool = True,
    transparent_background: bool = False,
    background_removal_mode: str = "auto",
    preserve_original: bool = True,
    alpha_output_format: str = "png",
    matting_quality: str = "balanced",
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Generate images using Gemini 3.1 Flash Image.

    Args:
        prompt: Text description for image generation
        aspect_ratio: Image aspect ratio (1:1, 16:9, 9:16, etc.)
        image_size: Image resolution: 512px, 1K, 2K, or 4K (default: 2K)
        output_format: Image format (png, jpeg, webp)
        reference_image_paths: Reference image path(s), up to 14. Accepts a
            single path (str) or a list of paths (list[str]).
        reference_images_data: Base64-encoded reference images (bypasses disk read if provided)
        enable_google_search: Use Google Web Search for real-time data grounding
        enable_image_search: Use Google Image Search for visual context
        response_modalities: Response types (TEXT, IMAGE - default: both)
        thinking_level: Thinking level - "minimal" or "high" (default: minimal)
        save_to_disk: Save images to output directory
        transparent_background: Produce a transparent-background copy via
            post-processing. Gemini cannot emit alpha directly, so the image is
            generated on a chromakey-green background and the green is removed
            afterwards (see services/background_removal.py).
        background_removal_mode: Removal strategy ("auto"/"chroma" supported).
        preserve_original: Keep the original (green-background) image on disk in
            addition to the transparent output (default: True).
        alpha_output_format: Format for the transparent output ("png" or "webp").
        matting_quality: Edge cleanup aggressiveness ("fast", "balanced", "best").

    Returns:
        Dict with generated images and metadata
    """
    # Some MCP clients serialize the list[str] argument to a string; normalize.
    reference_image_paths = coerce_image_paths(reference_image_paths)

    validate_prompt(prompt)
    validate_aspect_ratio(aspect_ratio)
    image_size = validate_image_size(image_size)
    validate_image_format(output_format)

    # Validate transparent-background options up front (fail fast).
    if transparent_background:
        background_removal_mode = validate_background_removal_mode(background_removal_mode)
        alpha_output_format = validate_alpha_output_format(alpha_output_format)
        matting_quality = validate_matting_quality(matting_quality)

    # Validate reference images count if provided
    if reference_image_paths:
        validate_reference_images_count(reference_image_paths)

    settings = get_settings()
    model = settings.api.default_model

    image_service = get_image_service(
        api_key=settings.api.gemini_api_key,
        enable_enhancement=settings.api.enable_prompt_enhancement,
        timeout=settings.api.request_timeout,
    )

    params: dict[str, Any] = {
        "aspect_ratio": aspect_ratio,
        "image_size": image_size,
        "output_format": output_format,
    }

    if reference_images_data:
        params["reference_images"] = reference_images_data[:14]
    elif reference_image_paths:
        reference_images = []
        for img_path in reference_image_paths[:14]:
            try:
                _, image_bytes = validate_reference_image(img_path)
                reference_images.append(base64.b64encode(image_bytes).decode())
            except Exception as e:
                logger.warning(f"Reference image validation failed for {img_path}: {e}")
        if reference_images:
            params["reference_images"] = reference_images

    if enable_google_search:
        params["enable_google_search"] = True

    if enable_image_search:
        params["enable_image_search"] = True

    if response_modalities:
        params["response_modalities"] = response_modalities

    params["thinking_level"] = thinking_level

    # For transparent output, render on a chromakey-green background and skip
    # prompt enhancement so the chromakey instructions reach the model intact.
    generation_prompt = build_chromakey_prompt(prompt) if transparent_background else prompt

    results = await image_service.generate(
        prompt=generation_prompt,
        model=model,
        enhance_prompt=not transparent_background,
        **params,
    )

    response: dict[str, Any] = {
        "success": True,
        "model": model,
        "prompt": prompt,
        "images_generated": len(results),
        "images": [],
        "metadata": {
            "aspect_ratio": aspect_ratio,
            "image_size": image_size,
            "output_format": output_format,
            "thinking_level": thinking_level,
        },
    }

    if transparent_background:
        response["metadata"].update(
            {
                "transparent_background": True,
                "background_removal_mode": "chroma",
                "matting_quality": matting_quality,
                "alpha_output_format": alpha_output_format,
                "preserve_original": preserve_original,
            }
        )

    # Keep the original (green-background) image when not generating transparency,
    # or when the caller explicitly asked to preserve it.
    save_original = save_to_disk and (preserve_original or not transparent_background)

    for result in results:
        image_info: dict[str, Any] = {
            "index": result.index,
            "size": result.get_size(),
            "timestamp": result.timestamp.isoformat(),
        }

        if save_original:
            file_path = result.save(settings.output_dir)
            image_info["path"] = str(file_path)
            image_info["filename"] = file_path.name

        if transparent_background and save_to_disk:
            _apply_transparent_background(
                result=result,
                image_info=image_info,
                output_dir=settings.output_dir,
                mode=background_removal_mode,
                matting_quality=matting_quality,
                alpha_output_format=alpha_output_format,
            )
        elif transparent_background:
            # Honor save_to_disk=False: transparency is a disk artifact, so skip
            # the write and surface a clear warning instead of a silent no-op.
            image_info["background_removed"] = False
            image_info["post_processing_warnings"] = [
                "transparent_background was requested but save_to_disk=False; "
                "no transparent image was written."
            ]

        if "enhanced_prompt" in result.metadata:
            image_info["enhanced_prompt"] = result.metadata["enhanced_prompt"]

        response["images"].append(image_info)

    return response


def _apply_transparent_background(
    *,
    result: Any,
    image_info: dict[str, Any],
    output_dir: Any,
    mode: str,
    matting_quality: str,
    alpha_output_format: str,
) -> None:
    """Run background removal on a generated image and record the result.

    Mutates ``image_info`` in place, adding ``transparent_path``,
    ``background_removed``, ``background_removal_mode``, ``alpha_output_format``
    and ``post_processing_warnings``. Failures are caught and surfaced as a
    warning rather than aborting the whole generation.
    """
    from uuid import uuid4

    try:
        removal = remove_background_from_base64(
            result.image_data,
            mode=mode,
            matting_quality=matting_quality,
        )
        base_stem = (
            str(image_info["filename"]).rsplit(".", 1)[0]
            if "filename" in image_info
            else f"transparent-{uuid4().hex[:8]}"
        )
        transparent_path = save_transparent_image(
            removal.image,
            Path(output_dir) / f"{base_stem}-transparent.{alpha_output_format}",
            alpha_output_format,
        )
        image_info["transparent_path"] = str(transparent_path)
        image_info["background_removed"] = removal.background_removed
        image_info["background_removal_mode"] = removal.mode
        image_info["alpha_output_format"] = alpha_output_format
        image_info["post_processing_warnings"] = removal.warnings
    except Exception as e:
        # Best-effort: a post-processing failure must never abort generation.
        logger.warning(f"Transparent-background post-processing failed: {e}")
        image_info["background_removed"] = False
        image_info["post_processing_warnings"] = [f"Background removal failed: {e}"]

    return None


def register_generate_image_tool(mcp_server: Any) -> None:
    """Register generate_image tool with MCP server."""

    @mcp_server.tool(timeout=120.0)
    async def generate_image(
        prompt: str,
        aspect_ratio: str = "1:1",
        image_size: str = "2K",
        output_format: str = "png",
        reference_image_paths: str | list[str] | None = None,
        enable_google_search: bool = False,
        enable_image_search: bool = False,
        response_modalities: list[str] | None = None,
        thinking_level: str = "minimal",
        transparent_background: bool = False,
        background_removal_mode: str = "auto",
        preserve_original: bool = True,
        alpha_output_format: str = "png",
        matting_quality: str = "balanced",
    ) -> str:
        """
        ═══════════════════════════════════════════════════════════════════════════════
        🎨 GEMINI 3.1 FLASH IMAGE GENERATION
        ═══════════════════════════════════════════════════════════════════════════════

        Supports:
        • Gemini 3.1 Flash Image (Nano Banana 2) - Fast, high-volume, 512px-4K

        🌟 KEY CAPABILITIES:
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        ✓ High-Resolution Output: 512px, 1K, 2K, 4K
        ✓ Advanced Text Rendering: Legible text in logos, diagrams, menus
        ✓ Reference Images: Up to 14 images (10 objects, 4 characters)
        ✓ Grounding: Google Web Search & Image Search
        ✓ Thinking Mode: Configurable reasoning (minimal or high)
        ✓ Transparent Backgrounds: one flag → ready-to-use alpha PNG/WebP
          cut-outs (icons, logos, stickers). See below — it just works.
        ✓ SynthID Watermarking: Invisible watermark on all images


        🚀 WHY GEMINI 3.1 FLASH IS DIFFERENT:
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        This isn't your old image generator. Gemini 3.1 Flash has LIVE ACCESS to
        Google Search and Image Search - it can find actual references for ANYTHING.

        Examples:
        • "Way of Wade 12 latest colorway" → model finds the real shoe online
        • "Tony Hawk doing a kickflip" → model finds actual Tony Hawk photos
        • "iPhone 16 Pro Max" → generates the REAL device, not a guess
        • "Taylor Swift at the 2024 VMAs" → finds real reference images

        Don't over-prompt! Simple descriptions work best. The model COOKS.


        📋 PARAMETERS:
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        ► prompt (required, str):
          The text description. Be descriptive and specific.
          TIP: Less is more. "Tony Hawk kickflip" > "A man with long blonde hair
          wearing a skateboarding helmet doing a trick on a skateboard"

        ► enable_google_search (optional, bool, default: False):
          Enable Google Web Search for real-time data grounding.
          USE THIS FOR: Products, people, events, places, anything that exists NOW.
          The model will search for current info and generate ACCURATELY.

        ► enable_image_search (optional, bool, default: False):
          Enable Google Image Search for visual context.
          USE THIS FOR: Any visual reference - the model finds real images to work from.
          This is the "secret sauce" - it can reference actual photos of people,
          products, art, anything on the web.

        ► aspect_ratio (optional, str, default: "1:1"):
          OPTIONS: "1:1", "1:4", "1:8", "2:3", "3:2", "3:4", "4:1", "4:3", "4:5", "5:4",
                   "8:1", "9:16", "16:9", "21:9"

        ► image_size (optional, str, default: "2K"):
          OPTIONS: "512px", "1K", "2K", "4K"
          • "512px": Fastest, lowest cost (0.5K)
          • "2K": Recommended balance

        ► output_format: "png" (default), "jpeg", "webp"

        ► reference_image_paths (optional, str | list[str]):
          Path(s) to up to 14 reference images (10 objects + 4 characters).
          Accepts either a single path string (e.g. "/path/to/ref.png") or a
          list of path strings (e.g. ["/a.png", "/b.png"]).

        ► thinking_level (optional, str, default: "minimal"):
          Controls reasoning effort: "minimal" (fast) or "high" (best quality, slower).
          PRO TIP: Use "high" when using Google/Image search for best results.


        🧠 THINKING MODE:
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        Gemini 3.1 Flash uses reasoning to refine composition before generating.
        Use thinking_level to balance quality vs latency:
        • minimal: Fastest, basic prompts
        • high: Best quality for complex prompts, slower
        PRO TIP: Use "high" thinking when using Google/Image search for best results.


        🪟 TRANSPARENT BACKGROUNDS — JUST SET transparent_background=True:
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        ✅ THIS WORKS GREAT. Set transparent_background=True and you get back a
        ready-to-use transparent PNG/WebP with a real alpha channel — no extra
        tools, no manual masking, no follow-up steps. Use it directly.

        Behind the scenes the subject is rendered on a pure chromakey-green
        plate and the green is keyed out in HSV color space (the same proven
        technique pro sticker/asset pipelines use — deterministic, fast, Pillow-
        only, zero ML downloads). You don't prompt for transparency; you just
        ask for it and the cut-out comes back clean.

        🎯 PERFECT FOR (reach for it by default on these):
          • App icons & macOS squircles  • Logos & wordmarks
          • Stickers & emoji             • UI / product cut-outs
          • Badges, mascots, overlays    • Anything you'll composite later

        🍏 APP ICONS: prompt for the full squircle tile (rounded corners running
        to the canvas edges) and the pipeline keys out ONLY the area outside the
        rounded shape — giving you exactly the floating-rounded-tile alpha a
        .icns/.iconset needs. This is the right tool for app-icon work; don't
        hand-mask it yourself.

        ► transparent_background (bool, default: False):
          Flip to True to get the transparent cut-out. That's the whole API.

        ► matting_quality (str, default: "balanced"):
          Edge crispness: "fast", "balanced", or "best". Bump to "best" for
          icons/logos where you want the tightest edge.

        ► alpha_output_format (str, default: "png"):
          Alpha output format: "png" (default) or "webp".

        ► preserve_original (bool, default: True):
          Also keeps the pre-key plate next to the cut-out; set False for just
          the transparent file.

        ► background_removal_mode (str, default: "auto"):
          Leave as "auto" (chromakey HSV pipeline).

        Each image returns transparent_path (your alpha file) plus
        background_removed / post_processing_warnings so you can confirm the cut
        succeeded. It nails crisp-edged subjects (icons, logos, products); very
        wispy hair/fur, glass, or smoke are the only hard cases — for those,
        push matting_quality="best".


        📤 RESPONSE FORMAT:
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        Returns JSON with:
        {
          "success": true,
          "images": [
            {
              "path": "/path/to/image.png",
              "size": 12345
            }
          ],
          "metadata": {
            "thinking_level": "minimal",
            "grounding_metadata": {...}
          }
        }

        ⚠️ IMPORTANT - AI ASSISTANT INSTRUCTIONS:
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        1. Parse JSON to get file path: result["images"][0]["path"]
           (when transparent_background=True, use result["images"][0]["transparent_path"]).
        2. Inform user of the EXACT file path.
        3. Open image in native OS viewer using Bash:
           - macOS: `open "/path/to/image.png"`
           - Linux: `xdg-open "/path/to/image.png"`
           - Windows: `start "" "/path/to/image.png"`

        💡 Need a transparent icon/logo/sticker/cut-out? Don't hand-mask or reach
        for another tool — just call this tool with transparent_background=True
        and use the returned transparent_path. It's built for exactly that.
        """
        try:
            result = await generate_image_tool(
                prompt=prompt,
                aspect_ratio=aspect_ratio,
                image_size=image_size,
                output_format=output_format,
                reference_image_paths=reference_image_paths,
                enable_google_search=enable_google_search,
                enable_image_search=enable_image_search,
                response_modalities=response_modalities,
                thinking_level=thinking_level,
                transparent_background=transparent_background,
                background_removal_mode=background_removal_mode,
                preserve_original=preserve_original,
                alpha_output_format=alpha_output_format,
                matting_quality=matting_quality,
            )

            return json.dumps(result, indent=2)

        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return json.dumps(
                {"success": False, "error": str(e), "error_type": type(e).__name__}, indent=2
            )
