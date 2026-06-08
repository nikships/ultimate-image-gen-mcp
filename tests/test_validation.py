import pytest

from src.config.constants import (
    ALL_MODELS,
    ASPECT_RATIOS,
    IMAGE_FORMATS,
    MAX_PROMPT_LENGTH,
)
from src.core.exceptions import ValidationError
from src.core.validation import (
    validate_alpha_output_format,
    validate_aspect_ratio,
    validate_batch_size,
    validate_image_format,
    validate_image_size,
    validate_model,
    validate_prompt,
)


@pytest.mark.unit
class TestValidation:
    """Tests for validation functions in src/core/validation.py."""

    @pytest.mark.parametrize("aspect_ratio", ASPECT_RATIOS)
    def test_validate_aspect_ratio_valid(self, aspect_ratio):
        """Test that valid aspect ratios do not raise ValidationError."""
        validate_aspect_ratio(aspect_ratio)

    @pytest.mark.parametrize("invalid_ratio", ["1:2", "2:1", "invalid", "", "1.1", "1:1:1"])
    def test_validate_aspect_ratio_invalid(self, invalid_ratio):
        """Test that invalid aspect ratios raise ValidationError."""
        with pytest.raises(ValidationError) as excinfo:
            validate_aspect_ratio(invalid_ratio)
        assert f"Invalid aspect ratio '{invalid_ratio}'" in str(excinfo.value)
        assert "Available:" in str(excinfo.value)

    @pytest.mark.parametrize("prompt", ["Valid prompt", "A" * MAX_PROMPT_LENGTH])
    def test_validate_prompt_valid(self, prompt):
        """Test that valid prompts do not raise ValidationError."""
        validate_prompt(prompt)

    @pytest.mark.parametrize(
        "invalid_prompt,expected_err",
        [
            ("", "Prompt cannot be empty"),
            ("   ", "Prompt cannot be empty"),
            ("A" * (MAX_PROMPT_LENGTH + 1), "Prompt too long"),
        ],
    )
    def test_validate_prompt_invalid(self, invalid_prompt, expected_err):
        """Test that invalid prompts raise ValidationError."""
        with pytest.raises(ValidationError) as excinfo:
            validate_prompt(invalid_prompt)
        assert expected_err in str(excinfo.value)

    @pytest.mark.parametrize("model", ALL_MODELS.keys())
    def test_validate_model_valid(self, model):
        """Test that valid models do not raise ValidationError."""
        validate_model(model)

    def test_validate_model_invalid(self):
        """Test that invalid model raises ValidationError."""
        invalid_model = "non-existent-model"
        with pytest.raises(ValidationError) as excinfo:
            validate_model(invalid_model)
        assert f"Invalid model '{invalid_model}'" in str(excinfo.value)
        assert "Available models:" in str(excinfo.value)

    @pytest.mark.parametrize(
        "fmt", list(IMAGE_FORMATS.keys()) + [f.upper() for f in IMAGE_FORMATS.keys()]
    )
    def test_validate_image_format_valid(self, fmt):
        """Test that valid image formats do not raise ValidationError."""
        validate_image_format(fmt)

    def test_validate_image_format_invalid(self):
        """Test that invalid image format raises ValidationError."""
        invalid_fmt = "gif"
        with pytest.raises(ValidationError) as excinfo:
            validate_image_format(invalid_fmt)
        assert f"Invalid image format '{invalid_fmt}'" in str(excinfo.value)
        assert "Available:" in str(excinfo.value)

    @pytest.mark.parametrize("size,max_size", [(1, 8), (4, 8), (8, 8)])
    def test_validate_batch_size_valid(self, size, max_size):
        """Test that valid batch sizes do not raise ValidationError."""
        validate_batch_size(size, max_size)

    @pytest.mark.parametrize(
        "size,max_size,expected_err",
        [
            (0, 8, "Batch size must be at least 1"),
            (-1, 8, "Batch size must be at least 1"),
            (9, 8, "Batch size exceeds maximum"),
            (
                "1",
                8,
                "Batch size must be at least 1",
            ),  # Pydantic might handle conversion, but our function checks isinstance(size, int)
        ],
    )
    def test_validate_batch_size_invalid(self, size, max_size, expected_err):
        """Test that invalid batch sizes raise ValidationError."""
        with pytest.raises(ValidationError) as excinfo:
            validate_batch_size(size, max_size)
        assert expected_err in str(excinfo.value)

    @pytest.mark.parametrize(
        "size,expected",
        [
            ("1k", "1K"),
            ("2K", "2K"),
            ("4k", "4K"),
            ("512px", "512px"),
            ("512PX", "512px"),
        ],
    )
    def test_validate_image_size_valid(self, size, expected):
        """Test that valid image sizes are normalized and do not raise ValidationError."""
        assert validate_image_size(size) == expected

    def test_validate_image_size_invalid(self):
        """Test that invalid image size raises ValidationError."""
        invalid_size = "8K"
        with pytest.raises(ValidationError) as excinfo:
            validate_image_size(invalid_size)
        assert f"Invalid image size '{invalid_size}'" in str(excinfo.value)
        assert "Must be one of:" in str(excinfo.value)


@pytest.mark.unit
class TestTransparentBackgroundValidation:
    """Tests for the transparent-background option validators."""

    @pytest.mark.parametrize("fmt,expected", [("png", "png"), ("WEBP", "webp")])
    def test_alpha_output_format_valid(self, fmt, expected):
        assert validate_alpha_output_format(fmt) == expected

    @pytest.mark.parametrize("fmt", ["jpeg", "jpg", "gif"])
    def test_alpha_output_format_invalid(self, fmt):
        with pytest.raises(ValidationError) as excinfo:
            validate_alpha_output_format(fmt)
        assert "support transparency" in str(excinfo.value)


@pytest.mark.unit
class TestCoerceImagePaths:
    """Tests for coerce_image_paths (handles clients that send a str)."""

    def test_none_and_empty(self):
        from src.core.validation import coerce_image_paths

        assert coerce_image_paths(None) is None
        assert coerce_image_paths("") is None
        assert coerce_image_paths("   ") is None

    def test_single_path_string(self):
        from src.core.validation import coerce_image_paths

        assert coerce_image_paths("/a.png") == ["/a.png"]
        assert coerce_image_paths("  /x y.png  ") == ["/x y.png"]

    def test_json_encoded_list_string(self):
        from src.core.validation import coerce_image_paths

        assert coerce_image_paths('["/a.png", "/b.png"]') == ["/a.png", "/b.png"]

    def test_malformed_json_treated_as_path(self):
        from src.core.validation import coerce_image_paths

        assert coerce_image_paths("[not json") == ["[not json"]

    def test_existing_list_passthrough(self):
        from src.core.validation import coerce_image_paths

        assert coerce_image_paths(["/a.png", "/b.png"]) == ["/a.png", "/b.png"]
