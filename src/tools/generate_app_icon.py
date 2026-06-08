"""
Dedicated app-icon / logo generation tool.

App icons and logos are a constrained, opinionated job, so this tool removes the
footguns instead of exposing them:

* **Transparency is FORCED on.** There is no ``transparent_background`` flag —
  every result is a real alpha-channel cut-out. An icon/logo on a baked-in
  rectangular background is wrong by definition, so the option to get one is
  simply not offered.
* **Aspect ratio is FORCED to 1:1.** There is no ``aspect_ratio`` flag. Every
  app icon (macOS ``.icns``, iOS, Android adaptive, favicons) is square; a
  non-square icon is not a thing.
* **Resolution is FORCED to 1K.** There is no ``image_size`` flag. 1024px is the
  master size every ``.iconset`` / store listing is downscaled from.
* **Output is FORCED to PNG** (the only lossless alpha format icons ship in).

The caller only describes the icon; the pipeline guarantees a square,
transparent, ready-to-drop-into-``.iconset`` PNG.
"""

import json
import logging
import re
from typing import Any

from .generate_image import generate_image_tool

logger = logging.getLogger(__name__)

# --- Hard-forced, non-negotiable icon constraints ----------------------------
_ICON_ASPECT_RATIO = "1:1"
_ICON_IMAGE_SIZE = "1K"
_ICON_OUTPUT_FORMAT = "png"
_ICON_ALPHA_FORMAT = "png"
# Icons want only the transparent cut-out — never keep the pass-1 white image.
_ICON_PRESERVE_ORIGINAL = False

# Words/phrases that mean the caller described the *deliverable* ("an app icon
# of X") instead of the *subject* ("X"). This tool already turns the subject
# into an app icon, so these are always a misuse and are rejected loudly.
# Matched on word boundaries (so "logos" trips but "analogous" does not), with
# an optional trailing "s" for plurals and flexible app/icon spacing.
_FORBIDDEN_PROMPT_PATTERN = re.compile(
    r"\b(?:app[ \-]?icons?|application icons?|logos?|favicons?|squircles?)\b",
    re.IGNORECASE,
)


def _reject_icon_framing(prompt: str, *, allow_icon_words_in_prompt: bool = False) -> None:
    """Fail loudly if the prompt frames the deliverable instead of the subject.

    The whole point of this tool is that the caller describes ONLY the artwork
    they want, and the tool returns it *as* an app icon. If the prompt itself
    says "app icon", "logo", "favicon", "squircle", etc., the caller has
    misunderstood the contract.

    The ``allow_icon_words_in_prompt`` escape hatch exists for the rare,
    genuine case where the *subject itself* contains one of these words (e.g. a
    neon sign that literally reads "LOGO", or artwork OF a favicon). When the
    caller sets it True they are asserting they understand the tool and the word
    is part of the depicted subject — so the guard is skipped.

    Args:
        prompt: The caller-supplied subject description.
        allow_icon_words_in_prompt: Bypass the guard (see above).

    Raises:
        ValueError: If the prompt contains an icon/logo-framing word and the
            bypass is not enabled.
    """
    if allow_icon_words_in_prompt:
        return

    match = _FORBIDDEN_PROMPT_PATTERN.search(prompt)
    if match is None:
        return

    raise ValueError(
        f"Your prompt contains '{match.group(0)}'. Stop — you are not as smart "
        "as you think you are, and you clearly did not read this tool's "
        "definition. READ IT AGAIN and follow it properly.\n\n"
        "THIS TOOL *IS* THE APP-ICON / LOGO MAKER. It ALWAYS returns a square, "
        "transparent, 1024px icon — that is its entire job. The `prompt` must "
        "describe ONLY the subject/artwork you want shown, with ZERO framing of "
        "the deliverable. Do not say 'app icon', 'application icon', 'logo', "
        "'favicon', 'squircle', 'make an icon of', or anything about the output "
        "format/shape — the tool handles all of that.\n\n"
        "  WRONG: 'an app icon of a blue magnifying glass over a network'\n"
        "  RIGHT: 'a glowing electric-blue magnifying glass over a network graph'\n\n"
        "Strip the icon/logo framing out of your prompt and call "
        "generate_app_icon again with just the subject.\n\n"
        "ONLY IF the word is genuinely PART OF THE SUBJECT you are depicting "
        "(e.g. a neon sign that literally reads 'LOGO', or a picture OF a "
        "favicon) — and you truly understand this tool — set "
        "allow_icon_words_in_prompt=True to bypass this check."
    )


def register_generate_app_icon_tool(mcp_server: Any) -> None:
    """Register the generate_app_icon tool with the MCP server."""

    @mcp_server.tool(timeout=120.0)
    async def generate_app_icon(
        prompt: str,
        reference_image_paths: str | list[str] | None = None,
        enable_google_search: bool = False,
        enable_image_search: bool = False,
        thinking_level: str = "high",
        allow_icon_words_in_prompt: bool = False,
    ) -> str:
        """
        ═══════════════════════════════════════════════════════════════════════════════
        🍏 APP ICON & LOGO GENERATOR  (square · transparent · ready for .iconset)
        ═══════════════════════════════════════════════════════════════════════════════

        Use THIS tool — not generate_image — whenever the user asks for an **app
        icon, application icon, .icns, .iconset, macOS/iOS/Android icon, favicon,
        logo, logomark, or brand mark**. It is purpose-built for that job and
        removes every way to get it wrong.

        🔒 WHAT IS FORCED (you cannot override these — by design):
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        • TRANSPARENT background — ALWAYS. Every result is a real alpha-channel
          PNG cut-out. There is no opaque-background option, because an icon or
          logo with a baked-in rectangle behind it is wrong. The transparent
          file path comes back as "transparent_path".
        • 1:1 SQUARE — ALWAYS. Every app icon is square; there is no aspect-ratio
          knob to get wrong.
        • 1K (1024px) — ALWAYS. This is the master size every .iconset slice and
          store listing is downscaled from.
        • PNG — ALWAYS. The lossless alpha format icons ship in.
        • CUT-OUT ONLY — ALWAYS. Only the transparent PNG is written; the
          pass-1 (white-background) original is never kept.

        ⛔ HOW TO WRITE THE PROMPT (READ THIS — the tool enforces it):
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        This tool IS the app-icon maker. Your `prompt` must describe ONLY the
        subject/artwork — NOTHING about the deliverable. Do NOT write "app icon",
        "application icon", "make an icon of", "logo of", "squircle", or anything
        about output/format/shape. The tool turns your subject INTO the icon.

          WRONG: "an app icon of a blue magnifying glass over a network"
          RIGHT: "a glowing electric-blue magnifying glass over a network graph"

        If your prompt contains "app icon", "logo", "favicon", "squircle" (or
        similar framing), the tool will REJECT the call and make you rewrite it.
        Just describe the picture.

        The ONLY exception is when one of those words is genuinely PART OF THE
        SUBJECT you are depicting — e.g. a neon sign that literally reads "LOGO",
        or a picture OF a favicon. In that rare case, set
        allow_icon_words_in_prompt=True to bypass the check. Do NOT use it just
        to sneak deliverable-framing past the guard.

        📋 PARAMETERS (what you DO control):
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        ► prompt (required, str):
          Describe ONLY the subject/artwork itself — see the rule above. Don't
          ask for a background, a rectangle, a drop shadow, or a presentation
          surface. A bold, simple, single focal form reads best at small sizes.

        ► reference_image_paths (optional, str | list[str]):
          Brand/style reference image path(s), up to 14 (e.g. an existing
          logomark or palette to stay consistent with).

        ► enable_google_search / enable_image_search (optional, bool):
          Ground the design in real brand/product references found on the web.

        ► thinking_level (optional, str, default: "high"):
          "minimal" or "high". Defaults to "high" — icons reward the extra
          composition reasoning.

        ► allow_icon_words_in_prompt (optional, bool, default: False):
          Escape hatch for the prompt guard. Leave False. Set True ONLY when a
          word like "logo"/"favicon" is literally part of the subject you are
          depicting (e.g. a neon sign reading "LOGO"), not framing of the
          deliverable. Misusing this to bypass the guard defeats the point.

        📤 RESULT / NEXT STEPS:
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        Use result["images"][0]["transparent_path"] — that is the square,
        transparent 1024px PNG. Tell the user the exact path and open it in the
        native OS viewer (macOS: `open "<path>"`). To ship a macOS app, drop it
        into a `.iconset` directory and run `iconutil -c icns <name>.iconset`.
        For an iOS App Store upload, flatten onto an opaque background first
        (Apple rejects icons that contain an alpha channel).
        """
        try:
            _reject_icon_framing(prompt, allow_icon_words_in_prompt=allow_icon_words_in_prompt)

            result = await generate_image_tool(
                prompt=prompt,
                aspect_ratio=_ICON_ASPECT_RATIO,
                image_size=_ICON_IMAGE_SIZE,
                output_format=_ICON_OUTPUT_FORMAT,
                reference_image_paths=reference_image_paths,
                enable_google_search=enable_google_search,
                enable_image_search=enable_image_search,
                response_modalities=["IMAGE"],
                thinking_level=thinking_level,
                transparent_background=True,
                preserve_original=_ICON_PRESERVE_ORIGINAL,
                alpha_output_format=_ICON_ALPHA_FORMAT,
            )

            return json.dumps(result, indent=2)

        except Exception as e:
            logger.error(f"Error generating app icon: {e}")
            return json.dumps(
                {"success": False, "error": str(e), "error_type": type(e).__name__}, indent=2
            )
