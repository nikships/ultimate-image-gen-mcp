"""Unit tests for the chromakey transparent-background pipeline.

These tests verify real pixel-level behaviour, so they need the genuine Pillow
package. The repo-wide ``conftest.py`` mocks ``PIL`` so that PIL-free imports of
``src.core.validation`` work without the dependency installed; here we drop that
mock and load the real library (skipping the module if Pillow is unavailable).

The module under test is intentionally self-contained (Pillow + stdlib only), so
we load it directly by file path to avoid importing the heavier ``src.services``
package (which pulls in google-genai / pydantic).
"""

import base64
import importlib.util
import io
import pathlib
import sys

import pytest

# --- Load the REAL Pillow, bypassing the conftest mock -----------------------
_pil_mods = {k: v for k, v in sys.modules.items() if k == "PIL" or k.startswith("PIL.")}
for _key in _pil_mods:
    del sys.modules[_key]
try:
    from PIL import Image, ImageDraw  # noqa: E402  (genuine Pillow)
except Exception:  # pragma: no cover - exercised only without Pillow installed
    sys.modules.update(_pil_mods)
    pytest.skip("Pillow not installed; skipping background-removal tests", allow_module_level=True)

# --- Load the module under test by path (no package side effects) ------------
_MODULE_PATH = (
    pathlib.Path(__file__).resolve().parent.parent / "src" / "services" / "background_removal.py"
)
_spec = importlib.util.spec_from_file_location("background_removal_under_test", _MODULE_PATH)
assert _spec and _spec.loader
bg = importlib.util.module_from_spec(_spec)
# Register before exec so dataclass annotation resolution can find the module.
sys.modules[_spec.name] = bg
_spec.loader.exec_module(bg)


# --- Helpers -----------------------------------------------------------------
def _chromakey_image(size: int = 100, *, with_subject_green: bool = False) -> "Image.Image":
    """Build a chromakey-green image with a red disc subject in the centre."""
    img = Image.new("RGB", (size, size), bg.CHROMAKEY_GREEN_RGB)
    draw = ImageDraw.Draw(img)
    draw.ellipse([size * 0.3, size * 0.3, size * 0.7, size * 0.7], fill=(220, 30, 30))
    if with_subject_green:
        # A desaturated/dark "forest" green detail that must be preserved.
        draw.rectangle([size * 0.45, size * 0.45, size * 0.55, size * 0.55], fill=(34, 139, 34))
    return img


def _png_base64(img: "Image.Image") -> str:
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()


# --- build_chromakey_prompt --------------------------------------------------
@pytest.mark.unit
class TestBuildChromakeyPrompt:
    def test_includes_subject_and_chromakey_instructions(self):
        result = bg.build_chromakey_prompt("a cute robot")
        assert "a cute robot" in result
        assert bg.CHROMAKEY_GREEN_HEX in result
        # The prompt must actively forbid outer outlines/bezels — that
        # instruction was previously inducing chrome rings on app icons.
        assert "NO OUTLINE" in result
        assert "bezel" in result.lower()
        assert "CHROMAKEY" in result.upper()

    def test_strips_whitespace(self):
        result = bg.build_chromakey_prompt("   panda   ")
        assert result.startswith("panda")


# --- remove_green_screen -----------------------------------------------------
@pytest.mark.unit
class TestRemoveGreenScreen:
    def test_returns_rgba_with_transparent_background(self):
        result = bg.remove_green_screen(_chromakey_image())
        assert result.image.mode == "RGBA"
        # All four corners (background) must be fully transparent.
        w, h = result.image.size
        for xy in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
            assert result.image.getpixel(xy)[3] == 0
        # The subject centre must remain fully opaque and still red.
        r, g, b, a = result.image.getpixel((w // 2, h // 2))
        assert a == 255
        assert r > 150 and g < 100 and b < 100

    def test_reports_removed_ratio_and_flag(self):
        result = bg.remove_green_screen(_chromakey_image())
        assert 0.5 < result.removed_ratio < 1.0
        assert result.background_removed is True
        assert result.mode == "chroma"
        assert result.warnings == []

    def test_preserves_saturated_dark_subject_green(self):
        result = bg.remove_green_screen(_chromakey_image(with_subject_green=True))
        w, h = result.image.size
        # The forest-green detail at the centre must survive (value gate).
        r, g, b, a = result.image.getpixel((w // 2, h // 2))
        assert a == 255
        assert (r, g, b) == (34, 139, 34)

    def test_no_green_background_emits_warning(self):
        solid_blue = Image.new("RGB", (40, 40), (20, 30, 200))
        result = bg.remove_green_screen(solid_blue)
        assert result.background_removed is False
        assert result.removed_ratio < bg._MIN_REMOVED_RATIO
        assert result.warnings  # low-confidence warning present

    def test_hue_wraparound_handles_red(self):
        # Red sits at hue 0; a red-centred key must wrap across the 0/255
        # boundary and still match (exercises the branchless modulo logic).
        red = Image.new("RGB", (30, 30), (255, 0, 0))
        result = bg.remove_green_screen(red, hue_center=0, hue_tolerance=12)
        assert result.image.getpixel((0, 0))[3] == 0
        assert result.removed_ratio > 0.9

    def test_higher_matting_quality_removes_at_least_as_much(self):
        img = _chromakey_image()
        fast = bg.make_transparent(img, matting_quality="fast")
        best = bg.make_transparent(img, matting_quality="best")
        # More dilation eats further into the green fringe around the subject.
        assert best.removed_ratio >= fast.removed_ratio


# --- make_transparent --------------------------------------------------------
@pytest.mark.unit
class TestMakeTransparent:
    @pytest.mark.parametrize("mode", ["auto", "chroma"])
    def test_supported_modes(self, mode):
        result = bg.make_transparent(_chromakey_image(), mode=mode)
        assert result.image.mode == "RGBA"
        assert result.mode == "chroma"

    @pytest.mark.parametrize("mode", ["local", "external", "bogus"])
    def test_unsupported_modes_raise(self, mode):
        with pytest.raises(ValueError):
            bg.make_transparent(_chromakey_image(), mode=mode)


# --- remove_background_from_base64 -------------------------------------------
@pytest.mark.unit
class TestRemoveBackgroundFromBase64:
    def test_decodes_and_removes(self):
        data = _png_base64(_chromakey_image())
        result = bg.remove_background_from_base64(data)
        assert result.image.mode == "RGBA"
        assert result.image.getpixel((0, 0))[3] == 0


# --- save_transparent_image --------------------------------------------------
@pytest.mark.unit
class TestSaveTransparentImage:
    @pytest.mark.parametrize("fmt", ["png", "webp"])
    def test_saves_with_alpha(self, tmp_path, fmt):
        result = bg.remove_green_screen(_chromakey_image())
        out = bg.save_transparent_image(result.image, tmp_path / "sticker.xxx", fmt)
        assert out.suffix == f".{fmt}"
        assert out.exists()
        with Image.open(out) as reopened:
            assert reopened.mode in ("RGBA", "LA", "P")
            assert reopened.convert("RGBA").getpixel((0, 0))[3] == 0

    def test_rejects_non_alpha_format(self, tmp_path):
        result = bg.remove_green_screen(_chromakey_image())
        with pytest.raises(ValueError):
            bg.save_transparent_image(result.image, tmp_path / "x.jpg", "jpeg")

    def test_creates_missing_parent_dirs(self, tmp_path):
        result = bg.remove_green_screen(_chromakey_image())
        nested = tmp_path / "deep" / "nested" / "out.png"
        out = bg.save_transparent_image(result.image, nested, "png")
        assert out.exists()
        assert out.parent == nested.parent
