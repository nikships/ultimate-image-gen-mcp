"""Input validation utilities."""

import base64
import re
from pathlib import Path

from ..config.constants import (
    ALL_MODELS,
    ASPECT_RATIOS,
    IMAGE_FORMATS,
    IMAGE_SIZES,
    MAX_PROMPT_LENGTH,
)
from .exceptions import ValidationError


def validate_prompt(prompt: str) -> None:
    """Validate prompt text."""
    if not prompt or not prompt.strip():
        raise ValidationError("Prompt cannot be empty")
    if len(prompt) > MAX_PROMPT_LENGTH:
        raise ValidationError(
            f"Prompt too long: {len(prompt)} characters (max {MAX_PROMPT_LENGTH})"
        )


def validate_model(model: str) -> None:
    """Validate model name."""
    if model not in ALL_MODELS:
        available = ", ".join(ALL_MODELS.keys())
        raise ValidationError(f"Invalid model '{model}'. Available models: {available}")


def validate_aspect_ratio(aspect_ratio: str) -> None:
    """Validate aspect ratio."""
    if aspect_ratio not in ASPECT_RATIOS:
        available = ", ".join(ASPECT_RATIOS)
        raise ValidationError(f"Invalid aspect ratio '{aspect_ratio}'. Available: {available}")


def validate_image_format(format_str: str) -> None:
    """Validate image format."""
    if format_str.lower() not in IMAGE_FORMATS:
        available = ", ".join(IMAGE_FORMATS.keys())
        raise ValidationError(f"Invalid image format '{format_str}'. Available: {available}")


def validate_file_path(path: str) -> Path:
    """Validate that the path exists and refers to a file."""
    try:
        file_path = Path(path).resolve()
    except Exception as e:
        raise ValidationError(f"Invalid file path '{path}': {e}") from e

    if not file_path.exists():
        raise ValidationError(f"File does not exist: {file_path}")
    if not file_path.is_file():
        raise ValidationError(f"Path is not a file: {file_path}")

    return file_path


def validate_base64_image(data: str) -> None:
    """Validate base64-encoded image data."""
    if not data:
        raise ValidationError("Base64 image data cannot be empty")

    try:
        decoded = base64.b64decode(data, validate=True)
    except Exception as e:
        raise ValidationError(f"Invalid base64 image data: {e}") from e

    if len(decoded) == 0:
        raise ValidationError("Decoded image data is empty")


def validate_prompts_list(prompts: list[str]) -> None:
    """Validate a list of prompts for batch processing."""
    if not isinstance(prompts, list):
        raise ValidationError("Prompts must be a list")
    if not prompts:
        raise ValidationError("Prompts list cannot be empty")

    for i, prompt in enumerate(prompts):
        if not isinstance(prompt, str):
            raise ValidationError(f"Prompt at index {i} must be a string")
        try:
            validate_prompt(prompt)
        except ValidationError as e:
            raise ValidationError(f"Invalid prompt at index {i}: {e}") from e


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename by replacing special characters with underscores."""
    safe_name = re.sub(r"[^a-zA-Z0-9-]", "_", filename)
    safe_name = re.sub(r"_+", "_", safe_name)
    safe_name = safe_name.strip("_")
    return safe_name or "image"


def validate_batch_size(size: int, max_size: int) -> None:
    """Validate that batch size is a positive integer within the allowed maximum."""
    if not isinstance(size, int) or size < 1:
        raise ValidationError(f"Batch size must be at least 1, got {size}")
    if size > max_size:
        raise ValidationError(f"Batch size exceeds maximum: {size} > {max_size}")


def validate_image_size(size: str) -> str:
    """Validate and normalize image size to uppercase (e.g. '2k' -> '2K')."""
    normalized = size.upper()
    if normalized not in IMAGE_SIZES:
        available = ", ".join(IMAGE_SIZES)
        raise ValidationError(f"Invalid image size '{size}'. Must be one of: {available}")
    return normalized
