"""
Constants and model definitions for Gemini 3 Pro Image API.

This MCP server exclusively supports Gemini 3 Pro Image Preview (aka "Nano Banana Pro"),
Google's state-of-the-art image generation model optimized for professional asset
production with advanced reasoning capabilities.
"""

from pathlib import Path

# Gemini Models (using official Google GenAI SDK)
# NOTE: This server ONLY supports Gemini 3 Pro Image Preview for image generation
GEMINI_MODELS = {
    "gemini-3-pro-image-preview": "gemini-3-pro-image-preview",  # Primary image model
    "gemini-flash-latest": "gemini-flash-latest",  # For prompt enhancement only (non-image)
}

# All available models
ALL_MODELS = GEMINI_MODELS

# Default models
DEFAULT_MODEL = "gemini-3-pro-image-preview"  # The only supported image generation model
DEFAULT_ENHANCEMENT_MODEL = "gemini-flash-latest"  # Used only for prompt enhancement

# Aspect ratios
ASPECT_RATIOS = [
    "1:1",  # Square
    "2:3",  # Portrait
    "3:2",  # Landscape
    "3:4",  # Portrait
    "4:3",  # Standard landscape
    "4:5",  # Portrait
    "5:4",  # Landscape
    "9:16",  # Vertical mobile
    "16:9",  # Widescreen
    "21:9",  # Ultrawide
]

# Image formats
IMAGE_FORMATS = {
    "png": "image/png",
    "jpeg": "image/jpeg",
    "jpg": "image/jpeg",
    "webp": "image/webp",
}

# Image sizes (Gemini 3 Pro Image)
# CRITICAL: Must use uppercase 'K' (e.g., "2K" not "2k") - lowercase will be rejected by API
IMAGE_SIZES = ["1K", "2K", "4K"]
DEFAULT_IMAGE_SIZE = "2K"

# Reference images limits (Gemini 3 Pro Image)
MAX_REFERENCE_IMAGES = 14
MAX_OBJECT_IMAGES = 6
MAX_HUMAN_IMAGES = 5

# Response modalities
RESPONSE_MODALITIES = ["TEXT", "IMAGE"]

# Generation limits
MAX_BATCH_SIZE = 8
MAX_PROMPT_LENGTH = 8192

# File size limits
MAX_IMAGE_SIZE_MB = 20
MAX_IMAGE_SIZE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024

# Timeout settings (in seconds)
DEFAULT_TIMEOUT = 60
ENHANCEMENT_TIMEOUT = 30
BATCH_TIMEOUT = 120

# Output settings
DEFAULT_OUTPUT_DIR = str(Path.home() / "gemini_images")
