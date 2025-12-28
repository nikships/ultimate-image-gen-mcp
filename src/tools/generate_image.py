"""
Image generation tool for Gemini 3 Pro Image (Nano Banana Pro).

This module provides MCP tools for professional image generation using Google's
Gemini 3 Pro Image Preview model with advanced reasoning, high-resolution output
(1K-4K), reference image support (up to 14), Google Search grounding, and thinking mode.
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
    enhance_prompt: bool = True,
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
        enhance_prompt: Automatically enhance prompt for better results
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
    validate_image_size(image_size)  # Critical: ensures uppercase 'K'
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
        enhance_prompt: bool = True,
        aspect_ratio: str = "1:1",
        image_size: str = "2K",
        output_format: str = "png",
        reference_image_paths: list[str] | None = None,
        enable_google_search: bool = False,
        response_modalities: list[str] | None = None,
    ) -> str:
        """
        ═══════════════════════════════════════════════════════════════════════════════
        🎨 GEMINI 3 PRO IMAGE - Professional Image Generation with Advanced Reasoning
        ═══════════════════════════════════════════════════════════════════════════════

        Gemini 3 Pro Image (aka "Nano Banana Pro") is Google's state-of-the-art image
        generation model optimized for professional asset production. It uses advanced
        reasoning through "Thinking Mode" to refine composition before generating the
        final high-quality output.

        🌟 KEY CAPABILITIES:
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        ✓ High-Resolution Output: Built-in 1K, 2K, and 4K generation
        ✓ Advanced Text Rendering: Legible, stylized text in infographics, menus, logos
        ✓ Reference Images: Up to 14 images (6 objects + 5 humans) for consistency
        ✓ Google Search Grounding: Real-time data (weather, stocks, events, maps)
        ✓ Thinking Mode: Generates interim "thought images" to refine composition
        ✓ Multi-turn Editing: Conversational refinement over multiple turns
        ✓ SynthID Watermarking: All images include invisible SynthID watermark


        📋 PARAMETERS:
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        ► prompt (required, str):
          The text description of your desired image. For best results, use descriptive
          narrative paragraphs rather than keyword lists.

          PROMPTING BEST PRACTICES:
          • "Describe the scene, don't just list keywords" - Use full sentences
          • Be hyper-specific about details (lighting, camera angle, materials, mood)
          • For photorealism: Use photography terms (e.g., "85mm portrait lens",
            "soft bokeh", "golden hour lighting")
          • For text in images: Explicitly state the exact text and font style
          • For logos/branding: Describe style, colors, and placement in detail

          Examples:
          ✓ GOOD: "A photorealistic close-up portrait of an elderly Japanese ceramicist
                   with deep wrinkles, inspecting a tea bowl in his rustic workshop.
                   Soft golden hour light streaming through a window, captured with
                   an 85mm lens creating soft bokeh background."
          ✗ POOR: "old man with pottery"

        ► model (optional, str, default: "gemini-3-pro-image-preview"):
          Model to use. Currently only "gemini-3-pro-image-preview" is supported.
          This is the default and recommended model for all image generation tasks.

        ► enhance_prompt (optional, bool, default: True):
          Automatically enhance your prompt using Gemini Flash for superior results.

          WHEN TO USE:
          • True (recommended): For quick iterations and automatic optimization
          • False: When you have carefully crafted prompts or need exact control

          What it does: Transforms simple prompts into detailed, cinematic descriptions.
          Example: "cat in space helmet" → "A photorealistic portrait of a domestic
          tabby cat wearing a futuristic space helmet, close-up composition, warm
          studio lighting, detailed fur texture, reflective visor..."

        ► aspect_ratio (optional, str, default: "1:1"):
          Image proportions. Choose based on your use case.

          OPTIONS: "1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"

          USAGE GUIDE:
          • "1:1" (Square) - Social media posts, profile pictures, logos
          • "16:9" (Widescreen) - YouTube thumbnails, presentation slides, banners
          • "9:16" (Vertical) - Instagram Stories, mobile wallpapers, TikTok
          • "3:2" or "4:3" - Standard photography, prints
          • "4:5" - Instagram feed posts (portrait)
          • "21:9" (Ultrawide) - Cinematic scenes, panoramic views

        ► image_size (optional, str, default: "2K"):
          Resolution of the generated image. IMPORTANT: Must use uppercase 'K'.

          OPTIONS: "1K", "2K", "4K" (lowercase like "1k" will be REJECTED)

          RESOLUTION GUIDE:
          • "1K" (~1024px) - Fast generation, testing, development iterations
            Token cost: 1120 tokens
            File size: ~1-2MB

          • "2K" (~2048px) - RECOMMENDED for most professional use cases
            Token cost: 1120 tokens
            File size: ~3-5MB
            Best balance of quality and speed

          • "4K" (~4096px) - Maximum quality for production assets, print materials
            Token cost: 2000 tokens (higher cost!)
            File size: ~8-15MB
            Use for: Final deliverables, large format prints, detailed artwork

          PRO TIP: Start with 2K during iteration, then regenerate at 4K for final output.

        ► output_format (optional, str, default: "png"):
          Image file format.

          OPTIONS: "png", "jpeg", "webp"

          • "png" (recommended) - Lossless, supports transparency, best for logos/graphics
          • "jpeg" - Smaller files, good for photos without transparency
          • "webp" - Modern format, good compression

        ► reference_image_paths (optional, list[str]):
          Paths to reference images for style consistency and character preservation.

          LIMITS:
          • Up to 14 total reference images
          • Maximum 6 object images (for high-fidelity inclusion of objects/items)
          • Maximum 5 human images (for character/person consistency)

          USE CASES:
          ✓ Character Consistency: Provide photos of people to maintain their appearance
          ✓ Style Transfer: Reference images to match artistic style or mood
          ✓ Object Inclusion: Include specific products, logos, or items
          ✓ Multi-person Compositions: Generate group photos with consistent faces
          ✓ 360° Character Views: Generate different angles of the same character

          Examples:
          • Group photo: ["person1.jpg", "person2.jpg", "person3.jpg"]
            Prompt: "An office group photo of these people making funny faces"

          • Product mockup: ["product.png", "logo.png"]
            Prompt: "Professional e-commerce photo of this product with the logo"

          • Style reference: ["reference_art.jpg"]
            Prompt: "Create a portrait in the artistic style of this reference image"

        ► enable_google_search (optional, bool, default: False):
          Enable real-time data grounding via Google Search.

          WHEN TO USE:
          ✓ Current events: "Visualize last night's Arsenal game in Champions League"
          ✓ Weather forecasts: "5-day weather forecast for San Francisco as a chart"
          ✓ Stock data: "Create an infographic of today's tech stock performance"
          ✓ Real-time maps: "Show current traffic patterns in downtown Tokyo"
          ✓ Recent news: "Illustrate yesterday's SpaceX launch"

          NOTE: Adds 1-3 seconds latency. Response includes `grounding_metadata` with
          the top 3 web sources used. Image-based search results are excluded.

        ► response_modalities (optional, list[str], default: ["TEXT", "IMAGE"]):
          What the model should return.

          OPTIONS:
          • ["TEXT", "IMAGE"] (default) - Get both explanation and image
          • ["IMAGE"] - Image only, no text description
          • ["TEXT"] - Text only (unusual for image generation)

          Most use cases should use the default for best results.


        🧠 THINKING MODE (Automatic):
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        Gemini 3 Pro Image uses advanced reasoning for complex prompts. The model
        generates up to 2 interim "thought images" to test composition and logic
        before producing the final high-quality output. This feature is ENABLED BY
        DEFAULT and cannot be disabled.

        The thinking process is visible in the response under the "thoughts" field.
        You can show users the model's reasoning process if desired.


        🏷️ SYNTHID WATERMARKING:
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        ALL generated images include an invisible SynthID watermark for authenticity
        and provenance tracking. This is automatic and does not affect visual quality.


        💡 PRACTICAL USE CASE EXAMPLES:
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        1. PROFESSIONAL LOGO DESIGN:
           prompt: "Create a modern, minimalist logo for a coffee shop called 'The
                   Daily Grind'. Clean, bold sans-serif font in black on white.
                   Circular design with a coffee bean integrated cleverly."
           aspect_ratio: "1:1"
           image_size: "4K"

        2. REAL-TIME DATA VISUALIZATION:
           prompt: "Visualize the current weather forecast for the next 5 days in
                   San Francisco as a clean, modern weather chart with clothing
                   recommendations for each day"
           enable_google_search: True
           aspect_ratio: "16:9"
           image_size: "2K"

        3. CHARACTER-CONSISTENT GROUP PHOTO:
           prompt: "An office group photo of these people, they are making funny faces"
           reference_image_paths: ["person1.jpg", "person2.jpg", "person3.jpg"]
           aspect_ratio: "5:4"
           image_size: "2K"

        4. HIGH-FIDELITY TEXT RENDERING:
           prompt: "Create a vibrant infographic explaining photosynthesis as a recipe
                   for a plant's favorite food. Show ingredients (sunlight, water,
                   CO2) and finished dish (sugar). Style like a colorful kids' cookbook
                   for 4th graders."
           aspect_ratio: "16:9"
           image_size: "4K"
           enable_google_search: True

        5. PRODUCT MOCKUP WITH STYLE TRANSFER:
           prompt: "Turn this rough pencil sketch of a futuristic car into a polished
                   photo of the finished concept car in a showroom. Keep the sleek
                   lines but add metallic blue paint and neon rim lighting."
           reference_image_paths: ["car_sketch.png"]
           image_size: "4K"
           aspect_ratio: "16:9"


        📤 RESPONSE FORMAT:
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        Returns JSON with:
        {
          "success": true,
          "model": "gemini-3-pro-image-preview",
          "prompt": "original prompt",
          "images_generated": 1,
          "images": [
            {
              "index": 0,
              "path": "/full/path/to/generated_image.png",
              "filename": "gemini3_20250128_123456_prompt_snippet.png",
              "size": 4567890,  // bytes
              "timestamp": "2025-01-28T12:34:56.789012",
              "enhanced_prompt": "enhanced version if enhancement was used"
            }
          ],
          "metadata": {
            "enhance_prompt": true,
            "aspect_ratio": "16:9",
            "thoughts": [...],  // if thinking mode generated interim images
            "grounding_metadata": {...}  // if Google Search was enabled
          }
        }


        ⚠️ IMPORTANT - AI ASSISTANT INSTRUCTIONS:
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        After generating an image, you MUST:

        1. Parse the JSON response to extract the file path: result["images"][0]["path"]
        2. Inform the user of the EXACT file path where the image was saved
        3. Use the Read tool to load and display the image to the user
        4. If thoughts were generated, show the thinking process to the user
        5. If Google Search was used, mention the grounding sources
        6. Optionally: Use bash to open the image in the default viewer:
           - macOS: `open /path/to/image.png`
           - Linux: `xdg-open /path/to/image.png`
           - Windows: `start /path/to/image.png`

        Complete Workflow Example:
        ```
        1. Call generate_image tool with parameters
        2. Parse response JSON to get file_path, thoughts, grounding_metadata
        3. Tell user: "✓ Image saved to: /Users/name/gemini_images/gemini3_20250128_image.png"
        4. If thoughts exist: "The model used thinking mode and generated 2 interim
           compositions before the final image."
        5. Call Read tool with the file_path to display the image to user
        6. Optionally call Bash: `open /Users/name/gemini_images/gemini3_20250128_image.png`
        ```

        ❌ DO NOT just say "image generated successfully" without showing the path and image!
        ❌ DO NOT skip displaying the image using the Read tool!
        ✓ DO parse and show all relevant metadata to help users understand the generation


        🚀 PERFORMANCE TIPS:
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        • Start with 2K during iteration, use 4K only for final output (saves tokens)
        • Disable prompt enhancement if you have expert-level prompts (saves 2-5s)
        • Use Google Search only when you actually need real-time data (saves 1-3s)
        • Limit reference images to what you actually need (max 14, but fewer is faster)
        • For testing: Use 1K resolution and enhance_prompt=False for fastest results

        ═══════════════════════════════════════════════════════════════════════════════
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
