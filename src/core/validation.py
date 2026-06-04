"""Input validation utilities."""

import base64
import io
import json
import re
from pathlib import Path

from PIL import Image

from ..config.constants import (
    ALL_MODELS,
    ASPECT_RATIOS,
    IMAGE_FORMATS,
    IMAGE_SIZES,
    MAX_IMAGE_SIZE_BYTES,
    MAX_PROMPT_LENGTH,
    MAX_REFERENCE_IMAGES,
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


def validate_reference_image(path: str | Path) -> tuple[Path, bytes]:
    """
    Validate a reference image file comprehensively.

    Checks:
    - File exists and is readable
    - File size is within MAX_IMAGE_SIZE_BYTES limit
    - File is a valid image format (using PIL)

    Returns:
        Tuple of (resolved_path, file_bytes)

    Raises:
        ValidationError: If any validation check fails
    """
    file_path = validate_file_path(str(path))

    # Check file size
    file_size = file_path.stat().st_size
    if file_size > MAX_IMAGE_SIZE_BYTES:
        raise ValidationError(
            f"Reference image too large: {file_size / (1024 * 1024):.1f}MB "
            f"(max {MAX_IMAGE_SIZE_BYTES / (1024 * 1024):.0f}MB): {file_path}"
        )

    if file_size == 0:
        raise ValidationError(f"Reference image is empty: {file_path}")

    # Read and validate it's a proper image
    try:
        image_bytes = file_path.read_bytes()
        with Image.open(io.BytesIO(image_bytes)) as img:
            # Verify it's a valid image by loading metadata
            img.verify()
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f"Invalid image file {file_path}: {e}") from e

    return file_path, image_bytes


def coerce_image_paths(value: "str | list[str] | None") -> "list[str] | None":
    """Normalize a reference-image-paths argument into a list of paths.

    Some MCP clients serialize a ``list[str]`` argument whose JSON schema lacks
    a top-level ``type`` (as produced by the ``list[str] | None`` annotation)
    into a plain string before sending it. Accepting ``str`` here and coercing
    it back to a list keeps those clients working. Handles:

    - ``None`` / empty string -> ``None``
    - a JSON-encoded list string (e.g. ``'["/a.png", "/b.png"]'``) -> parsed list
    - a single path string -> ``[path]``
    - an existing list -> returned unchanged
    """
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        if stripped.startswith("["):
            try:
                parsed = json.loads(stripped)
            except json.JSONDecodeError:
                return [stripped]
            if isinstance(parsed, list):
                return [str(item) for item in parsed]
            return [str(parsed)]
        return [stripped]
    return list(value)


def validate_reference_images_count(image_paths: list[str]) -> None:
    """Validate the number of reference images doesn't exceed the maximum."""
    if len(image_paths) > MAX_REFERENCE_IMAGES:
        raise ValidationError(
            f"Too many reference images: {len(image_paths)} (max {MAX_REFERENCE_IMAGES})"
        )


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
    if size.lower() == "512px":
        return "512px"
    normalized = size.upper()
    if normalized not in IMAGE_SIZES:
        available = ", ".join(IMAGE_SIZES)
        raise ValidationError(f"Invalid image size '{size}'. Must be one of: {available}")
    return normalized
