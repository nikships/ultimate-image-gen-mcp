"""
Image generation tool supporting both Gemini and Imagen models.
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
    # Reference images (up to 14)
    reference_image_paths: list[str] | None = None,
    # Google Search grounding
    enable_google_search: bool = False,
    # Response modalities
    response_modalities: list[str] | None = None,
    # Output options
    save_to_disk: bool = True,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Generate images using Gemini 3 Pro Image.

    Args:
        prompt: Text description for image generation
        model: Model to use (default: gemini-3-pro-image-preview)
        enhance_prompt: Automatically enhance prompt for better results (default: False)
        aspect_ratio: Image aspect ratio (1:1, 16:9, 9:16, etc.)
        image_size: Image resolution: 1K, 2K, or 4K (default: 2K)
        output_format: Image format (png, jpeg, webp)
        reference_image_paths: Paths to reference images (up to 14)
        enable_google_search: Use Google Search for real-time data grounding
        response_modalities: Response types (TEXT, IMAGE - default: both)
        save_to_disk: Save images to output directory

    Returns:
        Dict with generated images and metadata
    """
    # Validate inputs
    validate_prompt(prompt)
    if model:
        validate_model(model)
    validate_aspect_ratio(aspect_ratio)
    validate_image_format(output_format)

    # Get settings
    settings = get_settings()

    # Determine model
    if model is None:
        model = settings.api.default_model

    # Initialize image service
    image_service = ImageService(
        api_key=settings.api.gemini_api_key,
        enable_enhancement=settings.api.enable_prompt_enhancement,
        timeout=settings.api.request_timeout,
    )

    try:
        # Prepare parameters for Gemini 3 Pro Image
        params: dict[str, Any] = {
            "aspect_ratio": aspect_ratio,
            "image_size": image_size,
        }

        # Add reference images if provided (up to 14)
        if reference_image_paths:
            reference_images = []
            for img_path in reference_image_paths[:14]:  # Limit to max 14
                image_path = Path(img_path)
                if image_path.exists():
                    image_data = base64.b64encode(image_path.read_bytes()).decode()
                    reference_images.append(image_data)
                else:
                    logger.warning(f"Reference image not found: {img_path}")

            if reference_images:
                params["reference_images"] = reference_images

        # Add Google Search grounding if enabled
        if enable_google_search:
            params["enable_google_search"] = True

        # Add response modalities
        if response_modalities:
            params["response_modalities"] = response_modalities

        # Generate images
        results = await image_service.generate(
            prompt=prompt,
            model=model,
            enhance_prompt=enhance_prompt and settings.api.enable_prompt_enhancement,
            **params,
        )

        # Prepare response
        response: dict[str, Any] = {
            "success": True,
            "model": model,
            "prompt": prompt,
            "images_generated": len(results),
            "images": [],
            "metadata": {
                "enhance_prompt": enhance_prompt,
                "aspect_ratio": aspect_ratio,
            },
        }

        # Save images and prepare for MCP response
        for result in results:
            image_info = {
                "index": result.index,
                "size": result.get_size(),
                "timestamp": result.timestamp.isoformat(),
            }

            if save_to_disk:
                # Save to output directory
                file_path = result.save(settings.output_dir)
                image_info["path"] = str(file_path)
                image_info["filename"] = file_path.name

            # Add enhanced prompt info
            if "enhanced_prompt" in result.metadata:
                image_info["enhanced_prompt"] = result.metadata["enhanced_prompt"]

            response["images"].append(image_info)

        return response

    finally:
        await image_service.close()


def register_generate_image_tool(mcp_server: Any) -> None:
    """Register generate_image tool with MCP server."""

    @mcp_server.tool()
    async def generate_image(
        prompt: str,
        model: str | None = None,
        enhance_prompt: bool = False,
        aspect_ratio: str = "1:1",
        image_size: str = "2K",
        output_format: str = "png",
        reference_image_paths: list[str] | None = None,
        enable_google_search: bool = False,
        response_modalities: list[str] | None = None,
    ) -> str:
        """
        Generate images using Gemini 3 Pro Image - a state-of-the-art image generation model
        optimized for professional asset production with advanced reasoning capabilities.

        Features:
        - High-resolution output: 1K, 2K, and 4K visuals
        - Advanced text rendering for infographics, menus, diagrams
        - Up to 14 reference images for consistent style/characters
        - Google Search grounding for real-time data (weather, stocks, events)
        - Thinking mode: Uses reasoning to refine composition

        Args:
            prompt: Text description of the image to generate
            model: Model to use (default: gemini-3-pro-image-preview)
            enhance_prompt: Automatically enhance prompt using AI (default: False)
            aspect_ratio: Image aspect ratio like 1:1, 16:9, 9:16, 3:2, 4:5, etc. (default: 1:1)
            image_size: Image resolution: 1K, 2K, or 4K (default: 2K)
            output_format: Image format: png, jpeg, webp (default: png)
            reference_image_paths: Paths to reference images (up to 14 total, max 6 objects, max 5 humans)
            enable_google_search: Enable Google Search grounding for real-time data
            response_modalities: Response types like ["TEXT", "IMAGE"] (default: both)

        Available models:
        - gemini-3-pro-image-preview (default and only model)

        Returns:
            JSON string with generation results, file paths, thoughts, and grounding metadata

        IMPORTANT - AI Assistant Instructions:

        PROMPT ENHANCEMENT GUIDANCE:
        - enhance_prompt is OFF by default (False) to preserve user intent
        - ONLY set enhance_prompt=True when:
          1. User explicitly requests prompt enhancement
          2. You determine your prompt is too simple/vague (e.g., "a cat" or "sunset")
          3. User wants more creative/detailed interpretation
        - DO NOT enable for:
          - Well-detailed prompts with specific requirements
          - Technical/precise image requests (diagrams, infographics, UI mockups)
          - When user wants exact control over composition
        - Enhancement adds 2-5 seconds latency and uses Gemini Flash

        AFTER IMAGE GENERATION:
        You MUST:
        1. Parse the JSON response to extract the file path from result["images"][0]["path"]
        2. Inform the user of the EXACT file path where the image was saved
        3. Use the Read tool to load and display the image to the user
        4. If thoughts were generated, show the thinking process to the user
        5. Optionally: Use bash to open the image in the default viewer:
           - macOS: `open /path/to/image.png`
           - Linux: `xdg-open /path/to/image.png`
           - Windows: `start /path/to/image.png`

        Example workflow:
        ```
        1. Call generate_image tool
        2. Parse response JSON to get file_path and thoughts
        3. Tell user: "Image saved to: /Users/name/gemini_images/image.png"
        4. Show thinking process if present
        5. Call Read tool with the file_path to display the image
        6. Optionally call Bash with `open /path/to/image.png` to open in Preview
        ```

        DO NOT just say "image generated successfully" without showing the path and image!
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
                response_modalities=response_modalities,
            )

            return json.dumps(result, indent=2)

        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return json.dumps(
                {"success": False, "error": str(e), "error_type": type(e).__name__}, indent=2
            )
