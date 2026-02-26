"""
Image generation tool for Gemini 3.1 Flash Image.

This module provides MCP tools for professional image generation using Google's
Gemini 3.1 Flash Image with advanced reasoning, high-resolution output (512px-4K),
reference image support, Google Search grounding (Web & Image), and thinking mode.
"""

import base64
import json
import logging
from pathlib import Path
from typing import Any

from ..config import get_settings
from ..core import (
    validate_aspect_ratio,
    validate_image_format,
    validate_image_size,
    validate_prompt,
)
from ..services import ImageService

logger = logging.getLogger(__name__)


async def generate_image_tool(
    prompt: str,
    aspect_ratio: str = "1:1",
    image_size: str = "2K",
    output_format: str = "png",
    reference_image_paths: list[str] | None = None,
    enable_google_search: bool = False,
    enable_image_search: bool = False,
    response_modalities: list[str] | None = None,
    thinking_level: str = "minimal",
    save_to_disk: bool = True,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Generate images using Gemini 3.1 Flash Image.

    Args:
        prompt: Text description for image generation
        aspect_ratio: Image aspect ratio (1:1, 16:9, 9:16, etc.)
        image_size: Image resolution: 512px, 1K, 2K, or 4K (default: 2K)
        output_format: Image format (png, jpeg, webp)
        reference_image_paths: Paths to reference images (up to 14)
        enable_google_search: Use Google Web Search for real-time data grounding
        enable_image_search: Use Google Image Search for visual context
        response_modalities: Response types (TEXT, IMAGE - default: both)
        thinking_level: Thinking level - "minimal" or "high" (default: minimal)
        save_to_disk: Save images to output directory

    Returns:
        Dict with generated images and metadata
    """
    validate_prompt(prompt)
    validate_aspect_ratio(aspect_ratio)
    image_size = validate_image_size(image_size)
    validate_image_format(output_format)

    settings = get_settings()
    model = settings.api.default_model

    image_service = ImageService(
        api_key=settings.api.gemini_api_key,
        enable_enhancement=settings.api.enable_prompt_enhancement,
        timeout=settings.api.request_timeout,
    )

    try:
        params: dict[str, Any] = {
            "aspect_ratio": aspect_ratio,
            "image_size": image_size,
        }

        if reference_image_paths:
            reference_images = []
            for img_path in reference_image_paths[:14]:
                image_path = Path(img_path)
                if image_path.exists():
                    reference_images.append(base64.b64encode(image_path.read_bytes()).decode())
                else:
                    logger.warning(f"Reference image not found: {img_path}")
            if reference_images:
                params["reference_images"] = reference_images

        if enable_google_search:
            params["enable_google_search"] = True

        if enable_image_search:
            params["enable_image_search"] = True

        if response_modalities:
            params["response_modalities"] = response_modalities

        params["thinking_level"] = thinking_level

        results = await image_service.generate(
            prompt=prompt,
            model=model,
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
                "thinking_level": thinking_level,
            },
        }

        for result in results:
            image_info: dict[str, Any] = {
                "index": result.index,
                "size": result.get_size(),
                "timestamp": result.timestamp.isoformat(),
            }

            if save_to_disk:
                file_path = result.save(settings.output_dir)
                image_info["path"] = str(file_path)
                image_info["filename"] = file_path.name

            if "enhanced_prompt" in result.metadata:
                image_info["enhanced_prompt"] = result.metadata["enhanced_prompt"]

            response["images"].append(image_info)

        return response

    finally:
        await image_service.close()


def register_generate_image_tool(mcp_server: Any) -> None:
    """Register generate_image tool with MCP server."""

    @mcp_server.tool(timeout=120.0)
    async def generate_image(
        prompt: str,
        aspect_ratio: str = "1:1",
        image_size: str = "2K",
        output_format: str = "png",
        reference_image_paths: list[str] | None = None,
        enable_google_search: bool = False,
        enable_image_search: bool = False,
        response_modalities: list[str] | None = None,
        thinking_level: str = "minimal",
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
        ✓ SynthID Watermarking: Invisible watermark on all images


        📋 PARAMETERS:
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        ► prompt (required, str):
          The text description. Be descriptive and specific.

        ► aspect_ratio (optional, str, default: "1:1"):
          OPTIONS: "1:1", "1:4", "1:8", "2:3", "3:2", "3:4", "4:1", "4:3", "4:5", "5:4",
                   "8:1", "9:16", "16:9", "21:9"

        ► image_size (optional, str, default: "2K"):
          OPTIONS: "512px", "1K", "2K", "4K"
          • "512px": Fastest, lowest cost (0.5K)
          • "2K": Recommended balance

        ► output_format: "png" (default), "jpeg", "webp"

        ► reference_image_paths (optional, list[str]):
          Paths to up to 14 reference images (10 objects + 4 characters).

        ► enable_google_search (optional, bool, default: False):
          Enable Google Web Search for real-time data grounding (weather, stocks, news).

        ► enable_image_search (optional, bool, default: False):
          Enable Google Image Search for visual context.
          Example: "Visualize a butterfly resting on a flower" (model finds real images).

        ► thinking_level (optional, str, default: "minimal"):
          Controls reasoning effort: "minimal" (fast) or "high" (best quality, slower).


        🧠 THINKING MODE:
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        Gemini 3.1 Flash uses reasoning to refine composition before generating.
        Use thinking_level to balance quality vs latency:
        • minimal: Fastest, basic prompts
        • high: Best quality for complex prompts, slower



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
        2. Inform user of the EXACT file path.
        3. Open image in native OS viewer using Bash:
           - macOS: `open "/path/to/image.png"`
           - Linux: `xdg-open "/path/to/image.png"`
           - Windows: `start "" "/path/to/image.png"`
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
            )

            return json.dumps(result, indent=2)

        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return json.dumps(
                {"success": False, "error": str(e), "error_type": type(e).__name__}, indent=2
            )
