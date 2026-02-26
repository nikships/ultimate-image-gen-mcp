"""
Image generation tool for Gemini 3.1 Flash Image and Gemini 3 Pro Image.

This module provides MCP tools for professional image generation using Google's
Gemini 3 models with advanced reasoning, high-resolution output (512px-4K),
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
    validate_model,
    validate_prompt,
)
from ..services import ImageService

logger = logging.getLogger(__name__)


async def generate_image_tool(
    prompt: str,
    model: str | None = None,
    enhance_prompt: bool = False,
    aspect_ratio: str = "1:1",
    image_size: str = "2K",
    output_format: str = "png",
    reference_image_paths: list[str] | None = None,
    enable_google_search: bool = False,
    enable_image_search: bool = False,
    thinking_level: str | None = None,
    include_thoughts: bool = True,
    response_modalities: list[str] | None = None,
    save_to_disk: bool = True,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Generate images using Gemini 3.1 Flash Image or Gemini 3 Pro Image.

    Args:
        prompt: Text description for image generation
        model: Model to use (default: gemini-3.1-flash-image-preview)
        enhance_prompt: Automatically enhance prompt for better results (default: False)
        aspect_ratio: Image aspect ratio (1:1, 16:9, 9:16, etc.)
        image_size: Image resolution: 512px, 1K, 2K, or 4K (default: 2K)
        output_format: Image format (png, jpeg, webp)
        reference_image_paths: Paths to reference images (up to 14)
        enable_google_search: Use Google Web Search for real-time data grounding
        enable_image_search: Use Google Image Search for visual context (3.1 Flash only)
        thinking_level: "minimal" or "high" (only for Gemini 3.1 Flash)
        include_thoughts: Whether to return thinking process (default: True)
        response_modalities: Response types (TEXT, IMAGE - default: both)
        save_to_disk: Save images to output directory

    Returns:
        Dict with generated images and metadata
    """
    validate_prompt(prompt)
    if model:
        validate_model(model)
    validate_aspect_ratio(aspect_ratio)
    image_size = validate_image_size(image_size)  # Normalizes input
    validate_image_format(output_format)

    settings = get_settings()

    if model is None:
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
            "thinking_level": thinking_level,
            "include_thoughts": include_thoughts,
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

        results = await image_service.generate(
            prompt=prompt,
            model=model,
            enhance_prompt=enhance_prompt and settings.api.enable_prompt_enhancement,
            **params,
        )

        response: dict[str, Any] = {
            "success": True,
            "model": model,
            "prompt": prompt,
            "images_generated": len(results),
            "images": [],
            "metadata": {
                "enhance_prompt": enhance_prompt,
                "aspect_ratio": aspect_ratio,
                "thinking_level": thinking_level,
                "include_thoughts": include_thoughts,
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
        model: str = "gemini-3.1-flash-image-preview",
        enhance_prompt: bool = False,
        aspect_ratio: str = "1:1",
        image_size: str = "2K",
        output_format: str = "png",
        reference_image_paths: list[str] | None = None,
        enable_google_search: bool = False,
        enable_image_search: bool = False,
        thinking_level: str | None = None,
        include_thoughts: bool = True,
        response_modalities: list[str] | None = None,
    ) -> str:
        """
        ═══════════════════════════════════════════════════════════════════════════════
        🎨 GEMINI 3 IMAGE GENERATION (Flash 3.1 & Pro 3)
        ═══════════════════════════════════════════════════════════════════════════════

        Supports:
        • Gemini 3.1 Flash Image (Nano Banana 2) - Fast, high-volume, 512px-4K
        • Gemini 3 Pro Image (Nano Banana Pro) - Professional quality, advanced reasoning

        🌟 KEY CAPABILITIES:
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        ✓ High-Resolution Output: 512px, 1K, 2K, 4K
        ✓ Advanced Text Rendering: Legible text in logos, diagrams, menus
        ✓ Reference Images: Up to 14 images (10 objects, 4 characters)
        ✓ Grounding: Google Web Search & Image Search (3.1 Flash only)
        ✓ Thinking Mode: Reasoning process visible (configurable in 3.1 Flash)
        ✓ SynthID Watermarking: Invisible watermark on all images


        📋 PARAMETERS:
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        ► prompt (required, str):
          The text description. Be descriptive and specific.

        ► model (optional, str, default: "gemini-3.1-flash-image-preview"):
          • "gemini-3.1-flash-image-preview" (Default): Fast, supports Image Search & Thinking control
          • "gemini-3-pro-image-preview": Highest quality, deep reasoning

        ► aspect_ratio (optional, str, default: "1:1"):
          OPTIONS: "1:1", "1:4", "1:8", "2:3", "3:2", "3:4", "4:1", "4:3", "4:5", "5:4",
                   "8:1", "9:16", "16:9", "21:9"

        ► image_size (optional, str, default: "2K"):
          OPTIONS: "512px", "1K", "2K", "4K"
          • "512px": Fastest, lowest cost (0.5K)
          • "2K": Recommended balance

        ► output_format: "png" (default), "jpeg", "webp"

        ► reference_image_paths (optional, list[str]):
          Paths to up to 14 reference images (style, character, object).

        ► enable_google_search (optional, bool, default: False):
          Enable Google Web Search for real-time data grounding (weather, stocks, news).

        ► enable_image_search (optional, bool, default: False):
          Enable Google Image Search for visual context (3.1 Flash only).
          Example: "Visualize a Timareta butterfly resting on a flower" (model finds real images of the butterfly).

        ► thinking_level (optional, str):
          Only for Gemini 3.1 Flash. Control reasoning depth.
          OPTIONS: "minimal" (default), "high"

        ► include_thoughts (optional, bool, default: True):
          Whether to return the model's thinking process in the response.

        ► enhance_prompt (optional, bool, default: False):
          Use Gemini Flash to rewrite simple prompts into detailed descriptions.


        🧠 THINKING MODE:
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        Gemini 3 models "think" before generating to refine composition.
        • Gemini 3 Pro: Thinking is always on.
        • Gemini 3.1 Flash: You can control level ("minimal", "high").


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
            "thoughts": [...],
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
        4. Show thoughts if available.
        """
        try:
            result = await generate_image_tool(
                prompt=prompt,
                model=model,
                enhance_prompt=enhance_prompt,
                aspect_ratio=aspect_ratio,
                image_size=image_size,
                output_format=output_format,
                reference_image_paths=reference_image_paths,
                enable_google_search=enable_google_search,
                enable_image_search=enable_image_search,
                thinking_level=thinking_level,
                include_thoughts=include_thoughts,
                response_modalities=response_modalities,
            )

            return json.dumps(result, indent=2)

        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return json.dumps(
                {"success": False, "error": str(e), "error_type": type(e).__name__}, indent=2
            )
