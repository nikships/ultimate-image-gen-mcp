![Ultimate Gemini MCP Banner](https://raw.githubusercontent.com/anand-92/ultimate-image-gen-mcp/main/showcase/banner.png)

# Ultimate Gemini MCP

> MCP server for Google's **Gemini 3 Pro Image Preview** — state-of-the-art image generation with advanced reasoning, 1K–4K resolution, up to 14 reference images, Google Search grounding, and automatic thinking mode.

**All generated images include invisible SynthID watermarks for authenticity and provenance tracking.**

---

## Features

### Gemini 3 Pro Image
- **High-Resolution Output**: 1K, 2K, and 4K resolution
- **Advanced Text Rendering**: Legible, stylized text in infographics, menus, diagrams, and logos
- **Up to 14 Reference Images**: Up to 6 object images + up to 5 human images for style/character consistency
- **Google Search Grounding**: Real-time data (weather, stocks, events, maps)
- **Thinking Mode**: Model reasons about composition before producing the final image (automatic, always on)

### Server Features
- **AI Prompt Enhancement**: Optionally auto-enhance prompts using Gemini Flash
- **Batch Processing**: Generate multiple images in parallel (up to 8 concurrent)
- **22 Expert Prompt Templates**: MCP slash commands for photography, logos, cinematics, storyboards, and more
- **Flexible Aspect Ratios**: 10 options — 1:1, 16:9, 9:16, 3:2, 4:3, 4:5, 5:4, 2:3, 3:4, 21:9
- **Configurable via Environment Variables**: Output directory, default size, timeouts, and more

---

## Showcase

### Prompt Enhancement

When `enhance_prompt: true`, simple prompts are transformed into detailed, cinematic descriptions.

**Original:** `"A fierce wolf wearing the black symbiote Spider-Man suit, web-slinging through city at night"`

**Enhanced:** `"A powerfully built Alaskan Tundra Wolf, snarling fiercely, wearing the matte black, viscous, wet-looking symbiote suit with exaggerated white spider emblem. Captured mid-air in dramatic web-slinging arc with taut glowing webbing. Extreme low-angle perspective, hyper-realistic neo-noir cityscape at midnight with rain-slicked asphalt. High-contrast cinematic lighting with deep shadows and electric neon rim lighting."`

**Wolf — Black Symbiote Suit**
![Wolf in Black Symbiote Suit](https://raw.githubusercontent.com/anand-92/ultimate-image-gen-mcp/main/showcase/examples/wolf_symbiote.png)

**Lion — Classic Red & Blue Suit**
![Lion in Classic Spider-Man Suit](https://raw.githubusercontent.com/anand-92/ultimate-image-gen-mcp/main/showcase/examples/lion_classic.png)

**Black Panther — Symbiote Suit**
![Panther in Symbiote Suit](https://raw.githubusercontent.com/anand-92/ultimate-image-gen-mcp/main/showcase/examples/panther_symbiote.png)

**Eagle — Classic Suit in Flight**
![Eagle in Spider-Man Suit](https://raw.githubusercontent.com/anand-92/ultimate-image-gen-mcp/main/showcase/examples/eagle_classic.png)

**Grizzly Bear — Symbiote Suit**
![Bear in Symbiote Suit](https://raw.githubusercontent.com/anand-92/ultimate-image-gen-mcp/main/showcase/examples/bear_symbiote.png)

**Fox — Classic Suit at Dusk**
![Fox in Spider-Man Suit](https://raw.githubusercontent.com/anand-92/ultimate-image-gen-mcp/main/showcase/examples/fox_classic.png)

All generated with `enhance_prompt: true`, 2K, 16:9.

---

### Photorealistic Capabilities

**Jensen Huang — GPU Surfing**
![Jensen surfing on GPU through cyberpunk city](https://raw.githubusercontent.com/anand-92/ultimate-image-gen-mcp/main/showcase/examples/jensen_gpu_surfing.png)

**Elon Musk — Mars Chess Match**
![Elon playing chess with robot on Mars](https://raw.githubusercontent.com/anand-92/ultimate-image-gen-mcp/main/showcase/examples/elon_mars_chess.png)

**Jensen Huang — GPU Kitchen**
![Jensen cooking with GPU appliances](https://raw.githubusercontent.com/anand-92/ultimate-image-gen-mcp/main/showcase/examples/jensen_gpu_kitchen.png)

**Elon Musk — Cybertruck Symphony**
![Elon conducting Cybertruck orchestra](https://raw.githubusercontent.com/anand-92/ultimate-image-gen-mcp/main/showcase/examples/elon_cybertruck_symphony.png)

**Jensen Huang — Underwater Data Center**
![Jensen scuba diving in data center](https://raw.githubusercontent.com/anand-92/ultimate-image-gen-mcp/main/showcase/examples/jensen_underwater_datacenter.png)

**Elon Musk — SpaceX Skateboarding**
![Elon skateboarding at SpaceX](https://raw.githubusercontent.com/anand-92/ultimate-image-gen-mcp/main/showcase/examples/elon_spacex_skateboard.png)

---

## Quick Start

### Prerequisites
- Python 3.11+
- [Google Gemini API key](https://makersuite.google.com/app/apikey) (free tier available)

### Installation

**Using uvx (recommended — no install needed):**
```bash
uvx ultimate-gemini-mcp
```

**Using pip:**
```bash
pip install ultimate-gemini-mcp
```

**From source:**
```bash
git clone https://github.com/anand-92/ultimate-image-gen-mcp
cd ultimate-image-gen-mcp
uv sync
```

---

## Setup

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ultimate-gemini": {
      "command": "uvx",
      "args": ["ultimate-gemini-mcp"],
      "env": {
        "GEMINI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

Config file locations:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

> **macOS `spawn uvx ENOENT` error**: Use the full path — find it with `which uvx`, then set `"command": "/Users/you/.local/bin/uvx"`.

### Claude Code

```bash
claude mcp add ultimate-gemini \
  --env GEMINI_API_KEY=your-api-key \
  -- uvx ultimate-gemini-mcp
```

### Cursor

Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "ultimate-gemini": {
      "command": "uvx",
      "args": ["ultimate-gemini-mcp"],
      "env": {
        "GEMINI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

Images are saved to `~/gemini_images` by default. Add `"OUTPUT_DIR": "/your/path"` to customize.

---

## Tools

### `generate_image`

Generate an image with Gemini 3 Pro Image.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | string | required | Text description. Use full sentences, not keyword lists. |
| `model` | string | `gemini-3-pro-image-preview` | Model to use (currently only one supported) |
| `enhance_prompt` | bool | `false` | Auto-enhance prompt using Gemini Flash before generation |
| `aspect_ratio` | string | `1:1` | One of: `1:1` `2:3` `3:2` `3:4` `4:3` `4:5` `5:4` `9:16` `16:9` `21:9` |
| `image_size` | string | `2K` | `1K`, `2K`, or `4K` — **must be uppercase K** |
| `output_format` | string | `png` | `png`, `jpeg`, or `webp` |
| `reference_image_paths` | list | `[]` | Up to 14 local image paths (max 6 objects + max 5 humans) |
| `enable_google_search` | bool | `false` | Ground generation in real-time Google Search data |
| `response_modalities` | list | `["TEXT","IMAGE"]` | `["TEXT","IMAGE"]`, `["IMAGE"]`, or `["TEXT"]` |

**Image size guide:**
- `1K` — fast, good for testing (~1-2 MB)
- `2K` — recommended for most use cases (~3-5 MB)
- `4K` — maximum quality for production assets (~8-15 MB)

---

### `batch_generate`

Generate multiple images in parallel.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompts` | list | required | List of prompt strings (max 8) |
| `model` | string | `gemini-3-pro-image-preview` | Model for all images |
| `enhance_prompt` | bool | `true` | Enhance all prompts before generation |
| `aspect_ratio` | string | `1:1` | Aspect ratio applied to all images |
| `image_size` | string | `2K` | Resolution for all images |
| `output_format` | string | `png` | Format for all images |
| `response_modalities` | list | `["TEXT","IMAGE"]` | Modalities for all images |
| `batch_size` | int | `8` | Max concurrent requests |

---

## MCP Prompt Templates

22 expert prompt templates are available as MCP slash commands in Claude Code (type `/` to browse). Each template returns a crafted prompt and recommended parameters ready to pass directly to `generate_image` or `batch_generate`.

| Command | Description | Default aspect ratio |
|---------|-------------|----------------------|
| `photography_shot` | Photorealistic shot with lens/lighting specs | 16:9 |
| `logo_design` | Professional brand identity | 1:1, 4K, IMAGE only |
| `cinematic_scene` | Film still with cinematography language | 21:9 |
| `product_mockup` | Commercial e-commerce photography | 1:1 or 4:5 |
| `batch_storyboard` | Multi-scene storyboard → calls `batch_generate` | 16:9 |
| `macro_shot` | Extreme macro with micro-snoot lighting | 1:1 |
| `fashion_portrait` | Editorial fashion with gobo shadow patterns | 4:5 |
| `technical_cutaway` | Stephen Biesty-style cutaway diagram | 3:2, 4K, IMAGE only |
| `flat_lay` | Overhead knolling photography | 1:1 |
| `action_freeze` | High-speed strobe with motion blur background | 16:9 |
| `night_street` | Moody night street with practical light sources | 16:9 |
| `drone_aerial` | Straight-down golden hour aerial | 4:5, 4K, IMAGE only |
| `stylized_3d_render` | UE5-style render with subsurface scattering | 1:1, IMAGE only |
| `sem_microscopy` | Scanning electron microscope false-color | 1:1, IMAGE only |
| `double_exposure` | Silhouette-blended double exposure | 2:3, IMAGE only |
| `architectural_viz` | Ray-traced architectural visualization | 3:2, 4K |
| `isometric_illustration` | Orthographic isometric 3D illustration | 1:1, IMAGE only |
| `food_photography` | High-end backlit food photography | 4:5 |
| `motion_blur` | Rear-curtain sync slow shutter sequence | 16:9 |
| `typography_physical` | Text embedded in physical environment | 16:9, 4K, IMAGE only |
| `retro_futurism` | 1970s cassette-futurism analog sci-fi | 4:3, IMAGE only |
| `surreal_dreamscape` | Surrealist impossible physics scene | 1:1, IMAGE only |
| `character_sheet` | Video game character concept art sheet | 3:2, 4K, IMAGE only |
| `pbr_texture` | Seamless PBR texture map with raking light | 1:1, IMAGE only |
| `historical_photo` | Period-accurate photography with film emulation | 4:5 |
| `bioluminescent_nature` | Long-exposure bioluminescence macro | 1:1 |
| `silhouette_shot` | Cinematic pure-black silhouette master shot | 21:9, 4K |

---

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | — | **Required.** Google Gemini API key |
| `OUTPUT_DIR` | `~/gemini_images` | Directory where images are saved |
| `DEFAULT_IMAGE_SIZE` | `2K` | Default resolution (`1K`, `2K`, `4K`) |
| `DEFAULT_MODEL` | `gemini-3-pro-image-preview` | Default model |
| `ENABLE_PROMPT_ENHANCEMENT` | `false` | Auto-enhance prompts by default |
| `ENABLE_GOOGLE_SEARCH` | `false` | Enable Google Search grounding by default |
| `REQUEST_TIMEOUT` | `60` | API timeout in seconds |
| `MAX_BATCH_SIZE` | `8` | Max parallel requests in batch mode |
| `LOG_LEVEL` | `INFO` | Logging level |

---

## Troubleshooting

**`spawn uvx ENOENT`** — Claude Desktop can't find `uvx`. Use the full path:
```json
"command": "/Users/yourusername/.local/bin/uvx"
```
Find it with: `which uvx`

**`GEMINI_API_KEY not found`** — Set the key in your MCP config `env` block or in a `.env` file. Get a free key at [Google AI Studio](https://makersuite.google.com/app/apikey).

**`Content blocked by safety filters`** — Rephrase the prompt to avoid sensitive content.

**`Rate limit exceeded`** — Wait and retry, or upgrade your API quota.

**Images not saving** — Check `OUTPUT_DIR` exists and is writable: `mkdir -p /your/output/path`.

---

## License

MIT — see [LICENSE](LICENSE) for details.

## Links

- [Google AI Studio](https://makersuite.google.com/app/apikey) — Get your API key
- [Gemini API Docs](https://ai.google.dev/gemini-api/docs)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastMCP](https://github.com/jlowin/fastmcp)
