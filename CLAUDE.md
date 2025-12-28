# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Gemini 3 Pro Image MCP Server** - A production-ready FastMCP server for Google's Gemini 3 Pro Image, featuring state-of-the-art image generation with advanced reasoning, high-resolution output (1K-4K), reference images (up to 14), Google Search grounding, and thinking mode.

**Uses Official Google GenAI SDK** - Built on `google-genai` package for clean, maintainable code with automatic handling of thought signatures and response parsing.

## Development Commands

### Setup and Installation
```bash
# Install dependencies (required before development)
uv sync --all-extras

# Install from source
uv sync

# Run locally with dev mode (hot-reload enabled)
fastmcp dev src.server:create_app

# Or run directly
python -m src.server
```

### Testing and Quality
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Type checking
mypy src/

# Linting (check only)
ruff check src/

# Auto-format code
ruff format src/

# Run all quality checks
ruff check src/ && ruff format src/ && mypy src/ && pytest
```

### Environment Setup
```bash
# Required: Set API key
export GEMINI_API_KEY=your_key_here

# Optional: Enable debug logging
export LOG_LEVEL=DEBUG

# Optional: Change output directory
export OUTPUT_DIR=/path/to/output

# Optional: Default image size
export DEFAULT_IMAGE_SIZE=4K

# Optional: Enable Google Search by default
export ENABLE_GOOGLE_SEARCH=true
```

## Architecture

### Core Design Pattern: Gemini 3 Pro Image with Official SDK

The server uses the **official Google GenAI SDK** for clean, type-safe image generation:

```python
from google import genai
from google.genai import types

# Initialize client
client = genai.Client(api_key=api_key)

# Generate with reference images
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=[image1, image2, prompt],
    config=types.GenerateContentConfig(
        response_modalities=["TEXT", "IMAGE"],
        image_config=types.ImageConfig(
            aspect_ratio="16:9",
            image_size="4K"
        ),
        tools=[{"google_search": {}}]
    )
)

# Extract images using SDK methods
image = response.parts[0].as_image()
```

**Key insight:** The SDK handles thought signatures automatically, provides built-in image conversion methods, and manages API authentication/errors cleanly.

### Module Responsibilities

**`config/`** - Settings and constants
- `constants.py`: Model names, limits, aspect ratios (single source of truth)
- `settings.py`: Pydantic settings with environment variable binding

**`core/`** - Framework-agnostic utilities
- `exceptions.py`: Custom exception hierarchy for error categorization
- `validation.py`: Input validation functions (called before API requests)

**`services/`** - Business logic layer
- `gemini_client.py`: Gemini API using official `google-genai` SDK
- `prompt_enhancer.py`: Uses Gemini Flash to enhance prompts
- `image_service.py`: High-level orchestrator for image generation

**`tools/`** - MCP tool definitions
- `generate_image.py`: Main tool, handles all Gemini 3 parameters
- `batch_generate.py`: Parallel processing wrapper

**`server.py`** - FastMCP initialization
- Creates app via `create_app()` factory function
- Registers tools and resources
- Entry point for both `python -m src.server` and `uvx`

### Data Flow for Image Generation

1. **MCP Tool** (`generate_image`) receives user request with parameters
2. **Validation** (`core/validation.py`) checks all inputs
3. **(Optional) PromptEnhancer** improves prompt using Gemini Flash
4. **ImageService** orchestrates generation flow
5. **GeminiClient** calls Google API using official SDK
   - Converts reference images from base64 to PIL Images
   - Builds typed config objects (`GenerateContentConfig`, `ImageConfig`)
   - Handles async execution via `run_in_executor` (SDK is sync)
6. **Response Processing** extracts images, text, and thoughts
   - Uses SDK's `.as_image()` method for automatic PIL conversion
   - Separates thought parts from final output
   - Extracts grounding metadata if Google Search was used
7. **ImageResult** objects created with metadata
8. Images saved to disk with descriptive filenames
9. JSON response returned to MCP client

### Gemini 3 Pro Image Features

**Resolution Options:**
- 1K: Fast generation
- 2K (default): High quality for professional use
- 4K: Maximum resolution for production assets

**Reference Images (up to 14 total):**
- Up to 6 object images for high-fidelity inclusion
- Up to 5 human images for character consistency
- Passed as PIL Image objects to SDK

**Google Search Grounding:**
```python
config_args["tools"] = [{"google_search": {}}]
```
- Real-time weather, stocks, events, maps
- Returns `grounding_metadata` with search sources

**Thinking Mode:**
- Enabled by default for Gemini 3 Pro Image
- Model generates interim thought images to refine composition
- Thoughts extracted via `part.thought` attribute
- Final image is highest quality after reasoning

**Response Modalities:**
- `["TEXT", "IMAGE"]` (default): Get both explanation and image
- `["IMAGE"]`: Image only
- `["TEXT"]`: Text only

## Key Implementation Details

### Using Official Google GenAI SDK

**Initialize Client (services/gemini_client.py:37):**
```python
from google import genai

self.client = genai.Client(api_key=api_key)
```

**Build Typed Config (services/gemini_client.py:95-112):**
```python
from google.genai import types

image_config = types.ImageConfig(
    image_size=image_size,  # "1K", "2K", "4K"
    aspect_ratio=aspect_ratio  # "16:9", "1:1", etc.
)

config = types.GenerateContentConfig(
    response_modalities=["TEXT", "IMAGE"],
    image_config=image_config,
    tools=[{"google_search": {}}]  # Optional
)
```

**Handle Async Execution (services/gemini_client.py:119-128):**
```python
# SDK is synchronous, run in executor for async context
loop = asyncio.get_event_loop()
response = await loop.run_in_executor(
    None,
    partial(
        self.client.models.generate_content,
        model=model_id,
        contents=contents,
        config=config
    )
)
```

**Extract Content (services/gemini_client.py:207-254):**
```python
for part in response.parts:
    is_thought = getattr(part, 'thought', False)

    # Use SDK's built-in method
    if hasattr(part, 'inline_data'):
        image = part.as_image()  # Returns PIL Image
        # Convert to base64 for storage
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        image_b64 = base64.b64encode(buffer.getvalue()).decode()
```

### Prompt Enhancement Flow

- Uses `gemini-flash-latest` (non-image model) for text generation
- Enhancement is **optional** and **gracefully degrades** on failure
- Context includes: aspect_ratio, has_reference_images, use_google_search
- Original prompt preserved in ImageResult.metadata

### Reference Image Handling

**Convert Base64 to PIL Images (tools/generate_image.py:89-100):**
```python
reference_images = []
for img_path in reference_image_paths[:14]:
    image_path = Path(img_path)
    if image_path.exists():
        image_data = base64.b64encode(image_path.read_bytes()).decode()
        reference_images.append(image_data)
```

**SDK Handles PIL Conversion (services/gemini_client.py:82-87):**
```python
for ref_image_b64 in reference_images:
    image_bytes = base64.b64decode(ref_image_b64)
    image = Image.open(io.BytesIO(image_bytes))
    contents.append(image)  # SDK accepts PIL Images
```

### Filename Generation Strategy

Format: `{model}_{timestamp}_{prompt_snippet}_{index}.png`
- Timestamp: `%Y%m%d_%H%M%S`
- Model: Shortened (e.g., `gemini3` for `gemini-3-pro-image-preview`)
- Prompt snippet: First 30 chars, sanitized (alphanumeric only)
- Index: Only added for multi-image generations (if SDK returns multiple)

## Common Development Tasks

### Adding a New Gemini Model

```python
# 1. Add to constants.py
GEMINI_MODELS = {
    "gemini-3-pro-image-preview": "gemini-3-pro-image-preview",
    "gemini-4-image": "gemini-4-image",  # Example new model
}

# That's it! SDK and service layer handle automatically.
```

### Adding a New Tool Parameter

**Add to tool signature and validation:**
```python
# In tools/generate_image.py
async def generate_image_tool(
    prompt: str,
    model: str | None = None,
    new_param: str | None = None,  # Add here
    ...
):
    # Add validation
    if new_param:
        validate_new_param(new_param)  # Create in core/validation.py

    # Add to params passed to ImageService
    params["new_param"] = new_param
```

**Update SDK config if needed:**
```python
# In services/gemini_client.py
config_args: dict[str, Any] = {
    "response_modalities": response_modalities,
    "image_config": image_config,
}

# Add new config option
if kwargs.get("new_param"):
    config_args["new_param"] = kwargs["new_param"]
```

### Adding Validation

```python
# In core/validation.py
def validate_new_feature(value: str) -> None:
    """Validate new feature input."""
    if not value:
        raise ValidationError("Value cannot be empty")
    if len(value) > 100:
        raise ValidationError("Value too long (max 100 chars)")
```

**Pattern:** All validation functions raise `ValidationError` with user-friendly messages. Never return booleans.

### Handling New API Errors

```python
# In services/gemini_client.py _handle_exception()
def _handle_exception(self, error: Exception) -> None:
    error_msg = str(error)

    if "authentication" in error_msg.lower():
        raise AuthenticationError("API key invalid")
    elif "rate limit" in error_msg.lower():
        raise RateLimitError("Rate limit exceeded")
    elif "safety" in error_msg.lower():
        raise ContentPolicyError("Content blocked")
```

**Pattern:** Use specific exception types from `core/exceptions.py` for proper error categorization.

## Testing Strategy

### Unit Tests (markers: `@pytest.mark.unit`)
- Validation functions
- Filename sanitization
- Settings loading
- Exception hierarchy

### Integration Tests (markers: `@pytest.mark.integration`)
- GeminiClient methods (with mocked SDK)
- ImageService orchestration
- Tool functions end-to-end

### Network Tests (markers: `@pytest.mark.network`)
- Real API calls (requires `GEMINI_API_KEY`)
- Mark with `@pytest.mark.skipif(not os.getenv("GEMINI_API_KEY"))`

### Run Specific Test Markers
```bash
pytest -m unit              # Fast, no network
pytest -m integration       # Medium speed
pytest -m network           # Slow, needs API key
```

## Configuration Loading Priority

1. **Environment variables** (highest priority)
2. **`.env` file** in working directory
3. **Default values** in `config/settings.py`

Example:
```python
# settings.py (simplified)
class APIConfig(BaseSettings):
    gemini_api_key: str = Field(default="")  # Step 3: default
    default_image_size: str = Field(default="2K")

    model_config = SettingsConfigDict(
        env_file=".env",  # Step 2: .env file
    )

# Step 1: export GEMINI_API_KEY=... (highest priority)
```

## Error Handling Philosophy

**Fail fast with clear messages** - Invalid inputs should raise `ValidationError` before making API calls.

**Graceful degradation** - Prompt enhancement failures don't stop image generation:
```python
try:
    prompt = await enhancer.enhance(prompt)
except Exception as e:
    logger.warning(f"Enhancement failed: {e}")
    # Continue with original prompt
```

**User-friendly error messages** - API errors are categorized (Auth, RateLimit, ContentPolicy) so tools can provide actionable feedback.

**SDK Error Handling** - The genai SDK raises exceptions that we catch and re-raise as our custom types for consistency.

## Performance Characteristics

- **Prompt Enhancement:** Adds 2-5 seconds latency (optional, disabled by default)
- **Batch Processing:** Default 8 concurrent requests (`MAX_BATCH_SIZE`)
- **Timeouts:** 60s for generation (SDK default), 30s for enhancement
- **Image Size:**
  - 1K: ~1-2MB
  - 2K: ~3-5MB
  - 4K: ~8-15MB
- **Reference Images:** Up to 14 images processed before generation
- **Google Search:** Adds 1-3 seconds for grounding queries

**Optimization tips:**
- Enable enhancement for simple/vague prompts: `enhance_prompt=True`
- Use 1K for development/testing, 2K for balanced quality (default), 4K for production
- Limit reference images to what's actually needed

## Deployment Considerations

### Production Checklist
- Set `LOG_LEVEL=INFO` (default DEBUG is too verbose)
- Configure `OUTPUT_DIR` to persistent storage (not temp directory)
- Monitor API quota (enhancement uses 2 requests per generation)
- Set `DEFAULT_IMAGE_SIZE` based on use case (1K/2K/4K)
- Consider disabling Google Search grounding to reduce latency unless needed
- Set `REQUEST_TIMEOUT` based on expected image complexity (default 60s)

### Running as MCP Server

**Via Claude Desktop config (claude_desktop_config.json):**
```json
{
  "mcpServers": {
    "gemini-3-pro-image": {
      "command": "uvx",
      "args": ["ultimate-gemini-mcp"],
      "env": {
        "GEMINI_API_KEY": "your-key",
        "OUTPUT_DIR": "/path/to/images",
        "DEFAULT_IMAGE_SIZE": "2K"
      }
    }
  }
}
```

**Via Claude Code:**
```bash
claude mcp add gemini-3-image \
  --env GEMINI_API_KEY=key \
  --env OUTPUT_DIR=/path/to/images \
  -- uvx ultimate-gemini-mcp
```

## Troubleshooting Guide

**"No image data found in response"**
- Debug: Set `LOG_LEVEL=DEBUG` and check logs for SDK response
- Check: Model name matches constants.py exactly (`gemini-3-pro-image-preview`)
- Check: Prompt not blocked (look for safety filter messages)
- Check: `response_modalities` includes "IMAGE"

**"Prompt enhancement failed, using original"**
- This is expected behavior when enhancement service is unavailable
- Verify: API key has quota for `gemini-flash-latest` model
- Not critical: Image generation continues with original prompt

**"Could not extract image from part"**
- SDK's `as_image()` method may fail on malformed data
- Check: Response parts have `inline_data` attribute
- Verify: Image data is valid PNG/JPEG format

**Import errors after changes**
- Run `uv sync` to refresh dependencies
- Ensure Python >= 3.11 (`python --version`)
- Check for circular imports between services
- Verify `google-genai` package installed: `pip list | grep google-genai`

**Type errors from mypy**
- Most common: Missing type annotations on new functions
- Fix: Add `-> None` or `-> dict[str, Any]` return types
- SDK types: Import from `google.genai.types`
- Settings: See `pyproject.toml` [tool.mypy] for enabled checks

**Async/await issues**
- SDK is synchronous, must use `run_in_executor`
- Pattern in `gemini_client.py:119-128`
- Don't call SDK methods directly in async functions

## Code Style Guidelines

**Enforced by ruff:**
- Line length: 100 characters
- Import sorting: isort style
- Type hints: Required for all public functions

**Run before committing:**
```bash
ruff format src/ && ruff check src/ && mypy src/
```

**Settings:** See `pyproject.toml` [tool.ruff] and [tool.mypy] sections

## Dependencies

**Core:**
- `fastmcp>=2.11.0` - MCP server framework
- `google-genai>=0.3.0` - Official Google GenAI SDK
- `pillow>=10.4.0` - Image processing (required by SDK)
- `pydantic>=2.0.0` - Settings and validation
- `pydantic-settings>=2.0.0` - Environment variable binding

**No longer used:**
- ~~`httpx`~~ - Removed, using SDK instead
- ~~`aiohttp`~~ - Removed, not needed with SDK

## Resources

- **API Keys:** [Google AI Studio](https://makersuite.google.com/app/apikey)
- **Gemini 3 Docs:** [ai.google.dev/gemini-api/docs/thinking](https://ai.google.dev/gemini-api/docs/thinking)
- **Google GenAI SDK:** [github.com/googleapis/python-genai](https://github.com/googleapis/python-genai)
- **FastMCP:** [github.com/jlowin/fastmcp](https://github.com/jlowin/fastmcp)
- **MCP Spec:** [modelcontextprotocol.io](https://modelcontextprotocol.io/)

## Migration Notes (v2.0.0)

**Breaking Changes from v1.x:**
- Removed all Imagen model support (imagen-4, imagen-4-fast, imagen-4-ultra)
- Removed Imagen-specific parameters (negative_prompt, seed, number_of_images)
- Switched from direct HTTP (`httpx`) to official `google-genai` SDK
- Changed `default_gemini_model` to `default_model` in settings

**New Features:**
- Gemini 3 Pro Image with thinking mode
- Up to 14 reference images (6 objects + 5 humans)
- Google Search grounding for real-time data
- 4K resolution support
- Response modalities (TEXT + IMAGE)
- Automatic thought signature handling

**Simplified Architecture:**
- Single API client (GeminiClient) instead of dual backends
- Cleaner code with SDK's built-in methods
- Fewer dependencies (removed httpx, aiohttp)
