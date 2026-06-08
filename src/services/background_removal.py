"""Transparent-background output helpers.

Gemini does not emit true alpha-channel / transparent pixels directly, so
transparent-background output is implemented as a post-processing step that
runs *after* generation (see :mod:`services.difference_matting` for the matte
extraction). This module handles saving the resulting RGBA image to disk in an
alpha-capable format.
"""

from __future__ import annotations

import logging
from pathlib import Path

from PIL import Image

logger = logging.getLogger(__name__)


def save_transparent_image(image: Image.Image, output_path: Path, alpha_output_format: str) -> Path:
    """Save an RGBA image to disk in an alpha-capable format.

    Args:
        image: The RGBA image to save.
        output_path: Destination path (its suffix is normalised to the format).
        alpha_output_format: ``"png"`` or ``"webp"``.

    Returns:
        The path the image was written to.

    Raises:
        ValueError: If ``alpha_output_format`` does not support alpha.
    """
    fmt = alpha_output_format.lower()
    if fmt not in ("png", "webp"):
        raise ValueError(
            f"alpha_output_format '{alpha_output_format}' does not support transparency; "
            "use 'png' or 'webp'."
        )

    rgba = image if image.mode == "RGBA" else image.convert("RGBA")
    save_format = "PNG" if fmt == "png" else "WEBP"
    output_path = output_path.with_suffix(f".{fmt}")
    # The destination dir may not exist yet (e.g. preserve_original=False, so the
    # original save that would have created it was skipped).
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rgba.save(output_path, format=save_format)
    logger.info("Saved transparent image to %s", output_path)
    return output_path
