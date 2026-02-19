"""Image service for Gemini 3 Pro Image generation."""

import base64
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from ..config.constants import GEMINI_MODELS
from ..core.exceptions import ImageProcessingError
from .gemini_client import GeminiClient
from .prompt_enhancer import PromptEnhancer

logger = logging.getLogger(__name__)


class ImageResult:
    """Container for a generated image and its metadata."""

    def __init__(
        self,
        image_data: str,
        prompt: str,
        model: str,
        index: int = 0,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.image_data = image_data  # Base64-encoded PNG
        self.prompt = prompt
        self.model = model
        self.index = index
        self.metadata = metadata or {}
        self.timestamp = datetime.now()

    def save(self, output_dir: Path, filename: str | None = None) -> Path:
        """Decode and save the image to disk, returning the output path."""
        output_path = output_dir / (filename or self._generate_filename())
        try:
            output_path.write_bytes(base64.b64decode(self.image_data))
            logger.info(f"Saved image to {output_path}")
            return output_path
        except Exception as e:
            raise ImageProcessingError(f"Failed to save image: {e}") from e

    def _generate_filename(self) -> str:
        """Generate a readable filename from the prompt and a short timestamp."""
        import re

        slug = re.sub(r"[^a-z0-9]+", "-", self.prompt[:60].lower()).strip("-")
        time_suffix = self.timestamp.strftime("%H%M%S")
        index_str = f"-{self.index + 1}" if self.index > 0 else ""
        return f"{slug}{index_str}-{time_suffix}.png"

    def get_size(self) -> int:
        """Return the image size in bytes."""
        return len(base64.b64decode(self.image_data))


class ImageService:
    """Orchestrates image generation using Gemini 3 Pro Image."""

    def __init__(self, api_key: str, *, enable_enhancement: bool = True, timeout: int = 60) -> None:
        self.enable_enhancement = enable_enhancement
        self.gemini_client = GeminiClient(api_key, timeout)
        self.prompt_enhancer: PromptEnhancer | None = (
            PromptEnhancer(self.gemini_client) if enable_enhancement else None
        )

    async def generate(
        self, prompt: str, *, model: str | None = None, enhance_prompt: bool = True, **kwargs: Any
    ) -> list[ImageResult]:
        """
        Generate images using Gemini 3 Pro Image.

        Args:
            prompt: Text prompt for image generation
            model: Model to use (default: gemini-3-pro-image-preview)
            enhance_prompt: Whether to enhance the prompt before generation
            **kwargs: Additional parameters (aspect_ratio, reference_images, etc.)

        Returns:
            List of ImageResult objects
        """
        if model is None:
            model = "gemini-3-pro-image-preview"

        if model not in GEMINI_MODELS:
            raise ValueError(f"Unknown model: {model}. Only Gemini 3 Pro Image is supported.")

        original_prompt = prompt

        if enhance_prompt and self.prompt_enhancer:
            try:
                result = await self.prompt_enhancer.enhance_prompt(
                    prompt, context=self._build_enhancement_context(kwargs)
                )
                prompt = result["enhanced_prompt"]
                logger.info(f"Prompt enhanced: {len(original_prompt)} -> {len(prompt)} chars")
            except Exception as e:
                logger.warning(f"Prompt enhancement failed, using original: {e}")

        response = await self.gemini_client.generate_image(prompt=prompt, model=model, **kwargs)

        return [
            ImageResult(
                image_data=image_data,
                prompt=original_prompt,
                model=model,
                index=i,
                metadata={"enhanced_prompt": prompt, **kwargs},
            )
            for i, image_data in enumerate(response["images"])
        ]

    def _build_enhancement_context(self, params: dict[str, Any]) -> dict[str, Any]:
        """Extract prompt enhancement hints from generation parameters."""
        context: dict[str, Any] = {}

        if params.get("reference_images"):
            context["has_reference_images"] = True
            context["num_reference_images"] = len(params["reference_images"])

        if "aspect_ratio" in params:
            context["aspect_ratio"] = params["aspect_ratio"]

        if params.get("enable_google_search"):
            context["use_google_search"] = True

        return context

    async def close(self) -> None:
        """Close the underlying Gemini client."""
        await self.gemini_client.close()
