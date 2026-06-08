"""Tests for the two-pass difference-matting pipeline.

Like ``test_background_removal``, these exercise real pixel maths, so they need
genuine Pillow. The repo-wide ``conftest.py`` mocks ``PIL`` down to ``PIL.Image``
for PIL-free imports; here we drop that mock and load the module by file path so
we don't drag in the heavier ``src.services`` package (google-genai / pydantic).
"""

import base64
import importlib.util
import io
import pathlib
import sys

import pytest

# --- Load the REAL Pillow, bypassing the conftest mock -----------------------
# Only swap out the mock if the currently-loaded ``PIL`` is the conftest
# MagicMock; if a sibling test already restored the genuine package, reuse it.
# Blindly deleting + re-importing PIL would create a *second* real PIL module
# instance with its own (empty) save registry, corrupting the PIL that other
# test modules already bound to (observed as ``KeyError: 'PNG'`` on save).
_loaded_pil = sys.modules.get("PIL")
_pil_is_mock = (
    _loaded_pil is not None and "mock" in type(getattr(_loaded_pil, "Image", object)).__module__
)
if _pil_is_mock:
    for _key in [k for k in sys.modules if k == "PIL" or k.startswith("PIL.")]:
        del sys.modules[_key]
try:
    from PIL import Image  # noqa: E402  (genuine Pillow)

    Image.init()  # populate the codec SAVE/OPEN registries (lazy otherwise)
except Exception:  # pragma: no cover - only without Pillow installed
    pytest.skip("Pillow not installed; skipping difference-matting tests", allow_module_level=True)

# --- Load the module under test by path (no package side effects) ------------
_MODULE_PATH = (
    pathlib.Path(__file__).resolve().parent.parent / "src" / "services" / "difference_matting.py"
)
_spec = importlib.util.spec_from_file_location("difference_matting_under_test", _MODULE_PATH)
assert _spec and _spec.loader
dm = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = dm
_spec.loader.exec_module(dm)


# --- Helpers -----------------------------------------------------------------
W, H = 128, 128


def _ground_truth() -> tuple["Image.Image", "Image.Image"]:
    """Return (fg_color, gt_alpha) with colour and alpha varying across frame."""
    fg = Image.new("RGB", (W, H))
    alpha = Image.new("L", (W, H))
    fpx, apx = fg.load(), alpha.load()
    for y in range(H):
        for x in range(W):
            fpx[x, y] = ((x * 7) % 256, (y * 5) % 256, (x + y) % 256)
            apx[x, y] = int(x / (W - 1) * 255)  # 0 (transparent) -> 255 (opaque)
    return fg, alpha


def _composite(fg: "Image.Image", alpha: "Image.Image", bg_val: int) -> "Image.Image":
    out = Image.new("RGB", (W, H))
    o, f, a = out.load(), fg.load(), alpha.load()
    for y in range(H):
        for x in range(W):
            al = a[x, y] / 255.0
            fr, fg_, fb = f[x, y]
            o[x, y] = (
                round(al * fr + (1 - al) * bg_val),
                round(al * fg_ + (1 - al) * bg_val),
                round(al * fb + (1 - al) * bg_val),
            )
    return out


def _b64(img: "Image.Image") -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


# --- Prompt builders ---------------------------------------------------------
@pytest.mark.unit
class TestPrompts:
    def test_white_prompt_mentions_white_and_no_outline(self):
        p = dm.build_white_background_prompt("a robot")
        assert "a robot" in p
        assert dm.WHITE_HEX in p
        assert "outline" in p.lower()

    def test_black_edit_prompt_is_preservation_heavy(self):
        p = dm.build_to_black_edit_prompt()
        assert dm.BLACK_HEX in p
        # Must insist the subject is untouched — the matte depends on it.
        assert "identical" in p.lower()
        assert "only" in p.lower()


# --- Alpha + colour recovery -------------------------------------------------
@pytest.mark.unit
class TestExtractAlpha:
    def test_recovers_alpha_exactly_on_clean_composite(self):
        fg, gt = _ground_truth()
        res = dm.extract_alpha_two_pass(
            _composite(fg, gt, 255), _composite(fg, gt, 0), alpha_floor=0.0
        )
        assert res.aligned
        assert res.alignment_error < 1e-6
        # Alpha must match ground truth within rounding.
        rec, g = res.image.load(), gt.load()
        max_err = max(abs(rec[x, y][3] - g[x, y]) for y in range(H) for x in range(W))
        assert max_err <= 1

    def test_recovers_foreground_colour_where_opaque(self):
        fg, gt = _ground_truth()
        res = dm.extract_alpha_two_pass(
            _composite(fg, gt, 255), _composite(fg, gt, 0), alpha_floor=0.0
        )
        rec, f = res.image.load(), fg.load()
        # Sample the fully-opaque right edge; colour should be faithful.
        errs = []
        for y in range(0, H, 16):
            rr, rgc, rb, _ = rec[W - 1, y]
            tr, tg, tb = f[W - 1, y]
            errs.append((abs(rr - tr) + abs(rgc - tg) + abs(rb - tb)) / 3)
        assert max(errs) <= 2

    def test_fully_opaque_subject_makes_nothing_transparent(self):
        # Identical frames (subject fully opaque everywhere) => alpha 255 all.
        solid = Image.new("RGB", (W, H), (180, 40, 90))
        res = dm.extract_alpha_two_pass(solid, solid, alpha_floor=0.0)
        assert res.transparent_ratio == 0.0
        assert res.aligned


# --- Misalignment detection (warn-but-return contract) -----------------------
@pytest.mark.unit
class TestAlignment:
    def test_subject_drift_flags_misaligned_but_still_returns(self):
        fg, gt = _ground_truth()
        on_white = _composite(fg, gt, 255)
        on_black = _composite(fg, gt, 0)
        # Shift the black pass: simulates the edit moving the subject.
        drifted = on_black.transform(
            (W, H), Image.AFFINE, (1, 0, 4, 0, 1, 0), resample=Image.BILINEAR
        )
        res = dm.extract_alpha_two_pass(on_white, drifted, alpha_floor=0.0)
        assert res.aligned is False
        assert res.image is not None  # still returned
        assert any("alignment is LOW" in w for w in res.warnings)

    def test_dimension_mismatch_is_handled_and_warned(self):
        fg, gt = _ground_truth()
        on_white = _composite(fg, gt, 255)
        on_black = _composite(fg, gt, 0).resize((W // 2, H // 2))
        res = dm.extract_alpha_two_pass(on_white, on_black, alpha_floor=0.0)
        assert res.image.size == (W, H)
        assert any("dimensions differed" in w.lower() for w in res.warnings)


# --- base64 convenience wrapper ----------------------------------------------
@pytest.mark.unit
class TestFromBase64:
    def test_extract_from_base64_matches_direct(self):
        fg, gt = _ground_truth()
        on_white, on_black = _composite(fg, gt, 255), _composite(fg, gt, 0)
        res = dm.extract_alpha_from_base64(_b64(on_white), _b64(on_black), alpha_floor=0.0)
        assert res.image.mode == "RGBA"
        assert res.aligned
        assert res.image.size == (W, H)
