"""Tests for the generate_app_icon prompt-framing guard.

The guard (``_reject_icon_framing``) is pure stdlib (``re``) and has no Pillow /
google-genai dependency, but importing it via the ``src.tools`` package would
pull in ``generate_image`` → ``services.background_removal`` → the real Pillow,
which the repo-wide ``conftest.py`` deliberately mocks down to ``PIL.Image``.
So we load the module directly by file path, stubbing only its one internal
import, to test the guard in isolation.
"""

import importlib.util
import pathlib
import sys
import types

import pytest

# Stub the relative ``from .generate_image import generate_image_tool`` import so
# loading the module by path doesn't drag in Pillow/google-genai.
_stub_pkg = types.ModuleType("_app_icon_stub_pkg")
_stub_pkg.__path__ = []  # mark as package so submodule import resolves
_stub_gen = types.ModuleType("_app_icon_stub_pkg.generate_image")
_stub_gen.generate_image_tool = lambda *a, **k: None
sys.modules.setdefault("_app_icon_stub_pkg", _stub_pkg)
sys.modules.setdefault("_app_icon_stub_pkg.generate_image", _stub_gen)

_MODULE_PATH = (
    pathlib.Path(__file__).resolve().parent.parent / "src" / "tools" / "generate_app_icon.py"
)
_spec = importlib.util.spec_from_file_location("_app_icon_stub_pkg.generate_app_icon", _MODULE_PATH)
assert _spec and _spec.loader
_mod = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _mod
_spec.loader.exec_module(_mod)
_reject_icon_framing = _mod._reject_icon_framing


@pytest.mark.unit
class TestRejectIconFraming:
    @pytest.mark.parametrize(
        "prompt",
        [
            "an app icon of a blue magnifying glass",
            "App Icon for my K8s tool",
            "make an app-icon of a fox",
            "a cute appicon",
            "application icon of a rocket",
            "a clean logo for tracerr",
            "company LOGOS, flat style",
            "a favicon of a terminal prompt",
            "render a squircle with a gradient",
        ],
    )
    def test_rejects_deliverable_framing(self, prompt):
        with pytest.raises(ValueError) as excinfo:
            _reject_icon_framing(prompt)
        # The scolding must point the model back at the tool definition.
        assert "READ IT AGAIN" in str(excinfo.value)

    @pytest.mark.parametrize(
        "prompt",
        [
            "a glowing electric-blue magnifying glass over a network graph",
            "a folded origami fox in teal paper",
            "an analogous color study of autumn leaves",  # 'analogous' must NOT trip 'logo'
            "a friendly robot waving",
        ],
    )
    def test_allows_pure_subject_prompts(self, prompt):
        # Should not raise.
        _reject_icon_framing(prompt)

    def test_bypass_allows_icon_words_when_part_of_subject(self):
        # The escape hatch lets genuinely subject-embedded words through.
        _reject_icon_framing(
            "a neon sign that reads LOGO above a diner",
            allow_icon_words_in_prompt=True,
        )

    def test_bypass_disabled_by_default_still_rejects(self):
        with pytest.raises(ValueError):
            _reject_icon_framing("a neon sign that reads LOGO above a diner")
