"""Constants for the Gemini 3.1 Flash Image MCP server."""

from pathlib import Path

# Supported models
GEMINI_MODELS = {
    "gemini-3.1-flash-image-preview": "gemini-3.1-flash-image-preview",
    "gemini-flash-latest": "gemini-flash-latest",
}

ALL_MODELS = GEMINI_MODELS

DEFAULT_MODEL = "gemini-3.1-flash-image-preview"
DEFAULT_ENHANCEMENT_MODEL = "gemini-flash-latest"

ASPECT_RATIOS = [
    "1:1",
    "1:4",
    "1:8",
    "2:3",
    "3:2",
    "3:4",
    "4:1",
    "4:3",
    "4:5",
    "5:4",
    "8:1",
    "9:16",
    "16:9",
    "21:9",
]

IMAGE_FORMATS = {
    "png": "image/png",
    "jpeg": "image/jpeg",
    "jpg": "image/jpeg",
    "webp": "image/webp",
}

# API requires uppercase 'K' — validate_image_size normalizes inputs automatically
# 512px is supported by Flash 3.1
IMAGE_SIZES = ["512px", "1K", "2K", "4K"]
DEFAULT_IMAGE_SIZE = "2K"

MAX_REFERENCE_IMAGES = 14
MAX_OBJECT_IMAGES = 10
MAX_HUMAN_IMAGES = 4

RESPONSE_MODALITIES = ["TEXT", "IMAGE"]

# --- Transparent-background (post-processing) options ------------------------
# Gemini cannot emit true alpha directly, so transparency is implemented as a
# post-processing step. "chroma" uses a chromakey-green + HSV removal pipeline
# (pillow only). "local"/"external" are reserved for future ML/provider modes.
BACKGROUND_REMOVAL_MODES = ["auto", "chroma", "local", "external"]
SUPPORTED_BACKGROUND_REMOVAL_MODES = ["auto", "chroma"]
DEFAULT_BACKGROUND_REMOVAL_MODE = "auto"

# Formats that support an alpha channel for transparent output.
ALPHA_OUTPUT_FORMATS = ["png", "webp"]
DEFAULT_ALPHA_OUTPUT_FORMAT = "png"

# Matting quality presets (control edge-fringe dilation aggressiveness).
MATTING_QUALITY_LEVELS = ["fast", "balanced", "best"]
DEFAULT_MATTING_QUALITY = "balanced"

THINKING_LEVELS = ["minimal", "high"]
DEFAULT_THINKING_LEVEL = "minimal"

MAX_BATCH_SIZE = 8
MAX_PROMPT_LENGTH = 8192

MAX_IMAGE_SIZE_MB = 20
MAX_IMAGE_SIZE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024

DEFAULT_TIMEOUT = 60
ENHANCEMENT_TIMEOUT = 30
BATCH_TIMEOUT = 120

DEFAULT_OUTPUT_DIR = str(Path.home() / "gemini_images")
