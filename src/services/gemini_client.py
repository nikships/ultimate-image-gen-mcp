"""Gemini API client using the official Google GenAI SDK."""

import asyncio
import base64
import io
import logging
from typing import Any

from google import genai
from google.genai import types
from PIL import Image

from ..config.constants import DEFAULT_THINKING_LEVEL, GEMINI_MODELS
from ..core.exceptions import (
    APIError,
    AuthenticationError,
    ContentPolicyError,
    RateLimitError,
)

logger = logging.getLogger(__name__)


class GeminiClient:
    """Client for Gemini 3.1 Flash Image API using the official Google GenAI SDK."""

    def __init__(self, api_key: str, timeout: int = 60) -> None:
        self.api_key = api_key
        self.timeout = timeout
        self.client = genai.Client(api_key=api_key)

    async def generate_image(
        self,
        prompt: str,
        *,
        model: str = "gemini-3.1-flash-image-preview",
        reference_images: list[str] | None = None,
        aspect_ratio: str | None = None,
        image_size: str = "2K",
        response_modalities: list[str] | None = None,
        enable_google_search: bool = False,
        enable_image_search: bool = False,
        thinking_level: str = DEFAULT_THINKING_LEVEL,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Generate an image using Gemini 3.1 Flash Image.

        Args:
            prompt: Text prompt for image generation
            model: Model to use (default: gemini-3.1-flash-image-preview)
            reference_images: Base64-encoded reference images (up to 14)
            aspect_ratio: Desired aspect ratio
            image_size: Image resolution - 512px, 1K, 2K, or 4K (default: 2K)
            response_modalities: Response types (default: ["TEXT", "IMAGE"])
            enable_google_search: Enable Google Search grounding for real-time data
            enable_image_search: Enable Google Image Search for visual context
            thinking_level: Thinking level - "minimal" or "high" (default: minimal)
            **kwargs: Additional parameters

        Returns:
            Dict with 'images', 'thoughts', 'text', and 'model' keys

        Raises:
            APIError: If the API request fails
        """
        model_id = GEMINI_MODELS.get(model, model)

        try:
            contents: list[Any] = []

            if reference_images:
                for ref_image_b64 in reference_images[:14]:
                    image_bytes = base64.b64decode(ref_image_b64)
                    contents.append(Image.open(io.BytesIO(image_bytes)))

            contents.append(prompt)

            if response_modalities is None:
                response_modalities = ["TEXT", "IMAGE"]

            image_config = types.ImageConfig(
                aspect_ratio=aspect_ratio,
                image_size=image_size if image_size else None,
            )

            config_args: dict[str, Any] = {
                "response_modalities": response_modalities,
                "image_config": image_config,
            }

            # Search Tools
            # NOTE: When using search tools with thinking mode, there's a known issue
            # where the model needs thought_signature in function calls. To work around
            # this, we force minimal thinking when search is enabled.
            effective_thinking_level = thinking_level
            if enable_google_search or enable_image_search:
                config_args["tools"] = [
                    types.Tool(
                        google_search=types.GoogleSearch(
                            search_types=types.SearchTypes(
                                web_search=types.WebSearch() if enable_google_search else None,
                                image_search=types.ImageSearch() if enable_image_search else None,
                            )
                        )
                    )
                ]
                # Force minimal thinking when search is enabled to avoid thought_signature errors
                if thinking_level.lower() != "minimal":
                    effective_thinking_level = "minimal"
                    logger.info("Forcing minimal thinking due to search tool usage")

            # Thinking Config - minimal or high
            thinking_level_map = {
                "minimal": types.ThinkingLevel.MINIMAL,
                "high": types.ThinkingLevel.HIGH,
            }
            config_args["thinking_config"] = types.ThinkingConfig(
                thinking_level=thinking_level_map.get(
                    effective_thinking_level.lower(), types.ThinkingLevel.MINIMAL
                ),
            )

            config = types.GenerateContentConfig(**config_args)

            logger.info(
                f"Generating image: model={model_id}, size={image_size}, "
                f"aspect_ratio={aspect_ratio}, items={len(contents)}"
            )

            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=model_id,
                contents=contents,
                config=config,
            )

            extraction = self._extract_content_from_response(response)
            images = extraction["images"]
            thoughts = extraction["thoughts"]
            text_parts = extraction["text"]

            if not images and "IMAGE" in response_modalities:
                parts = response.parts or []
                logger.error(
                    f"No images extracted. Parts={len(parts)}, "
                    f"thoughts={len(thoughts)}, text={len(text_parts)}, "
                    f"modalities={response_modalities}"
                )
                for idx, part in enumerate(parts):
                    logger.error(
                        f"  Part {idx}: has_inline_data={hasattr(part, 'inline_data')}, "
                        f"has_text={hasattr(part, 'text')}, "
                        f"thought={getattr(part, 'thought', None)}, "
                        f"thought_sig={hasattr(part, 'thought_signature')}"
                    )
                raise APIError("No image data found in Gemini API response")

            result: dict[str, Any] = {
                "images": images,
                "text": text_parts,
                "thoughts": thoughts,
                "model": model,
            }

            if (enable_google_search or enable_image_search) and hasattr(
                response, "grounding_metadata"
            ):
                result["grounding_metadata"] = response.grounding_metadata

            return result

        except Exception as e:
            logger.error(f"Gemini API request failed: {e}")
            self._handle_exception(e)
            raise APIError(f"Gemini API request failed: {e}") from e

    async def generate_text(
        self,
        prompt: str,
        *,
        model: str = "gemini-flash-latest",
        system_instruction: str | None = None,
    ) -> str:
        """
        Generate text using Gemini (used for prompt enhancement).

        Args:
            prompt: Text prompt
            model: Model to use
            system_instruction: Optional system instruction

        Returns:
            Generated text response
        """
        model_id = GEMINI_MODELS.get(model, model)

        try:
            config = (
                types.GenerateContentConfig(system_instruction=system_instruction)
                if system_instruction
                else None
            )

            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=model_id,
                contents=prompt,
                config=config,
            )

            return response.text or ""

        except Exception as e:
            logger.error(f"Gemini text generation failed: {e}")
            raise APIError(f"Gemini text generation failed: {e}") from e

    def _extract_content_from_response(self, response: Any) -> dict[str, Any]:
        """
        Extract images, text, and thoughts from a Gemini SDK response.

        Returns:
            Dict with 'images' (base64 strings), 'text' (strings), and
            'thoughts' (dicts with type/data/index keys)
        """
        images: list[str] = []
        text_parts: list[str] = []
        thoughts: list[dict[str, Any]] = []

        try:
            logger.info(f"Extracting content from {len(response.parts)} response parts")

            for idx, part in enumerate(response.parts):
                is_thought = getattr(part, "thought", False)

                if hasattr(part, "inline_data") and part.inline_data:
                    try:
                        pil_image = Image.open(io.BytesIO(part.inline_data.data))
                        buffer = io.BytesIO()
                        pil_image.save(buffer, format="PNG")
                        image_b64 = base64.b64encode(buffer.getvalue()).decode()

                        if is_thought:
                            thoughts.append(
                                {"type": "image", "data": image_b64, "index": len(thoughts)}
                            )
                        else:
                            images.append(image_b64)
                    except Exception as e:
                        logger.error(f"Could not extract image from part {idx}: {e}", exc_info=True)

                if hasattr(part, "text") and part.text:
                    if is_thought:
                        thoughts.append({"type": "text", "data": part.text, "index": len(thoughts)})
                    else:
                        text_parts.append(part.text)

        except Exception as e:
            logger.error(f"Error extracting content from response: {e}", exc_info=True)

        logger.info(
            f"Extracted {len(images)} images, {len(text_parts)} text parts, {len(thoughts)} thoughts"
        )
        return {"images": images, "text": text_parts, "thoughts": thoughts}

    def _handle_exception(self, error: Exception) -> None:
        """Categorize and re-raise SDK exceptions as typed errors."""
        error_msg = str(error).lower()

        if "authentication" in error_msg or "api key" in error_msg:
            raise AuthenticationError("Authentication failed. Please check your Gemini API key.")
        elif "rate limit" in error_msg or "quota" in error_msg:
            raise RateLimitError("Rate limit exceeded. Please try again later.")
        elif "safety" in error_msg or "blocked" in error_msg:
            raise ContentPolicyError(
                "Content was blocked by safety filters. Please modify your prompt."
            )

    async def close(self) -> None:
        """No-op: the GenAI SDK handles cleanup automatically."""
