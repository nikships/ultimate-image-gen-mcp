"""Core modules for Ultimate Gemini MCP."""

from .exceptions import (
    APIError,
    AuthenticationError,
    ConfigurationError,
    ContentPolicyError,
    FileOperationError,
    ImageProcessingError,
    RateLimitError,
    UltimateGeminiError,
    ValidationError,
)
from .validation import (
    coerce_image_paths,
    sanitize_filename,
    validate_aspect_ratio,
    validate_base64_image,
    validate_batch_size,
    validate_file_path,
    validate_image_format,
    validate_image_size,
    validate_model,
    validate_prompt,
    validate_prompts_list,
    validate_reference_image,
    validate_reference_images_count,
)

__all__ = [
    # Exceptions
    "UltimateGeminiError",
    "ConfigurationError",
    "ValidationError",
    "APIError",
    "AuthenticationError",
    "RateLimitError",
    "ContentPolicyError",
    "ImageProcessingError",
    "FileOperationError",
    # Validation
    "coerce_image_paths",
    "validate_prompt",
    "validate_model",
    "validate_aspect_ratio",
    "validate_image_format",
    "validate_image_size",
    "validate_file_path",
    "validate_base64_image",
    "validate_prompts_list",
    "validate_batch_size",
    "validate_reference_image",
    "validate_reference_images_count",
    "sanitize_filename",
]
