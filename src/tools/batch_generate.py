"""
Batch image generation tool for processing multiple prompts efficiently.
"""

import asyncio
import json
import logging
from typing import Any

from ..config import MAX_BATCH_SIZE, get_settings
from ..core import validate_batch_size, validate_prompts_list
from .generate_image import generate_image_tool

logger = logging.getLogger(__name__)


async def batch_generate_images(
    prompts: list[str],
    model: str | None = None,
    enhance_prompt: bool = True,
    aspect_ratio: str = "1:1",
    output_format: str = "png",
    batch_size: int | None = None,
    **shared_params: Any,
) -> dict[str, Any]:
    """
    Generate multiple images from a list of prompts.

    Args:
        prompts: List of text prompts
        model: Model to use for all images
        enhance_prompt: Enhance all prompts
        aspect_ratio: Aspect ratio for all images
        output_format: Output format for all images
        batch_size: Number of images to process in parallel (default: from config)
        **shared_params: Additional parameters shared across all generations

    Returns:
        Dict with batch results
    """
    # Validate inputs
    validate_prompts_list(prompts)

    settings = get_settings()
    if batch_size is None:
        batch_size = settings.api.max_batch_size

    validate_batch_size(batch_size, MAX_BATCH_SIZE)

    # Prepare results
    results: dict[str, Any] = {
        "success": True,
        "total_prompts": len(prompts),
        "batch_size": batch_size,
        "completed": 0,
        "failed": 0,
        "results": [],
    }

    # Process prompts in batches
    for i in range(0, len(prompts), batch_size):
        batch = prompts[i : i + batch_size]
        logger.info(f"Processing batch {i // batch_size + 1}: {len(batch)} prompts")

        # Create tasks for parallel processing
        tasks = [
            generate_image_tool(
                prompt=prompt,
                model=model,
                enhance_prompt=enhance_prompt,
                aspect_ratio=aspect_ratio,
                output_format=output_format,
                **shared_params,
            )
            for prompt in batch
        ]

        # Execute batch
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for j, result in enumerate(batch_results):
            prompt_index = i + j

            if isinstance(result, Exception):
                logger.error(f"Failed to generate image for prompt {prompt_index}: {result}")
                results["failed"] += 1
                results["results"].append(
                    {
                        "prompt_index": prompt_index,
                        "prompt": batch[j],
                        "success": False,
                        "error": str(result),
                    }
                )
            else:
                # result is dict[str, Any] here (not an Exception)
                if not isinstance(result, dict):
                    logger.error(f"Unexpected result type: {type(result)}")
                    results["failed"] += 1
                    results["results"].append(
                        {
                            "prompt_index": prompt_index,
                            "prompt": batch[j],
                            "success": False,
                            "error": "Unexpected result type",
                        }
                    )
                else:
                    results["completed"] += 1
                    results["results"].append(
                        {"prompt_index": prompt_index, "prompt": batch[j], **result}
                    )

    return results


def register_batch_generate_tool(mcp_server: Any) -> None:
    """Register batch_generate tool with MCP server."""

    @mcp_server.tool()
    async def batch_generate(
        prompts: list[str],
        model: str | None = None,
        enhance_prompt: bool = True,
        aspect_ratio: str = "1:1",
        output_format: str = "png",
        batch_size: int | None = None,
        negative_prompt: str | None = None,
    ) -> str:
        """
        Generate multiple images from a list of prompts efficiently.

        Processes prompts in parallel batches for optimal performance.
        All images share the same generation settings.

        Args:
            prompts: List of text descriptions for image generation
            model: Model to use for all images (default: gemini-3-pro-image-preview)
            enhance_prompt: Enhance all prompts automatically (default: True)
            aspect_ratio: Aspect ratio for all images (default: 1:1)
            output_format: Image format for all images (default: png)
            batch_size: Parallel batch size (default: from config)
            negative_prompt: Negative prompt for Imagen models (optional)

        Returns:
            JSON string with batch results including individual image paths

        IMPORTANT - AI Assistant Instructions:
        After batch generation completes, you MUST:
        1. Parse the JSON response to extract file paths from result["results"][i]["images"][0]["path"]
        2. Show the user a summary of all generated images with their file paths
        3. Open one or more images in the native OS picture viewer using Bash (DO NOT use Read tool):
           - macOS: `open "/path/to/image.png"`
           - Linux: `xdg-open "/path/to/image.png"`
           - Windows: `start "" "/path/to/image.png"`
        4. Let the user know the total count of successful vs failed generations

        Example response to user:
        "Successfully generated 3 images:
        1. /path/to/image1.png - [description]
        2. /path/to/image2.png - [description]
        3. /path/to/image3.png - [description]"

        DO NOT just say "batch generation completed" without listing the file paths!
        DO NOT use the Read tool to display images - use native OS viewer instead!
        """
        try:
            result = await batch_generate_images(
                prompts=prompts,
                model=model,
                enhance_prompt=enhance_prompt,
                aspect_ratio=aspect_ratio,
                output_format=output_format,
                batch_size=batch_size,
                negative_prompt=negative_prompt,
            )

            return json.dumps(result, indent=2)

        except Exception as e:
            logger.error(f"Batch generation error: {e}")
            return json.dumps(
                {"success": False, "error": str(e), "error_type": type(e).__name__}, indent=2
            )
