![Ultimate Gemini MCP Banner](https://raw.githubusercontent.com/anand-92/ultimate-image-gen-mcp/main/showcase/banner.png)

# Ultimate Gemini MCP

> MCP server for Google's **Gemini 3.1 Flash Image** — fast image generation with advanced reasoning, 512px–4K resolution, up to 14 reference images, Google Search grounding, and automatic thinking mode.

---

## Setup

### Claude Desktop

Add to your mcp config (mcp.json / .claude.json):

```json
{
  "mcpServers": {
    "ultimate-gemini": {
      "command": "uvx",
      "args": ["ultimate-gemini-mcp@latest"],
      "env": {
        "GEMINI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```


**All generated images include invisible SynthID watermarks for authenticity and provenance tracking.**

---

## Features

### Gemini 3.1 Flash Image
- **High-Resolution Output**: 512px, 1K, 2K, and 4K resolution
- **Advanced Text Rendering**: Legible, stylized text in infographics, menus, diagrams, and logos
- **Up to 14 Reference Images**: Up to 10 objects + 4 characters for style/character consistency
- **Google Search Grounding**: Real-time data (weather, stocks, events, maps)
- **Google Image Search**: Visual context from web images — the model can FIND real images of anything
- **Thinking Mode**: Configurable reasoning - "minimal" (fast) or "high" (best quality)
- **Transparent Backgrounds**: Flip one flag → ready-to-use transparent PNG/WebP cut-outs with a real alpha channel, recovered by a two-pass difference matte (generate on white → edit to black → solve for alpha). True soft edges/glow/glass, no color halo. Pillow only — no extra dependencies. Costs a second model call (~2x).
- **Dedicated App-Icon / Logo Tool**: `generate_app_icon` forces a square, transparent, 1024px PNG every time — no way to get a non-square or opaque-background icon

> **This model is different.** Unlike traditional image generators that rely solely on training data, Gemini 3.1 Flash has live access to Google Search and Image Search. It can find actual references for products, people, events, or anything that exists online. "Way of Wade 12" → generates the REAL shoe. "Tony Hawk" → finds real photos. Don't over-prompt — let the model cook.

### Server Features
- **Batch Processing**: Generate multiple images in parallel (up to 8 concurrent)
- **26 Expert Prompt Templates**: MCP slash commands for photography, cinematics, storyboards, and more
- **Flexible Aspect Ratios**: 14 options — 1:1, 1:4, 1:8, 2:3, 3:2, 3:4, 4:1, 4:3, 4:5, 5:4, 8:1, 9:16, 16:9, 21:9
- **Configurable via Environment Variables**: Output directory, default size, timeouts, and more

---

## Showcase

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

### Google Search Grounding

**Current Weather in San Francisco**
![Weather search](https://raw.githubusercontent.com/anand-92/ultimate-image-gen-mcp/main/showcase/examples/weather_google_search.png)

### Google Image Search

**Butterfly on Flower**
![Butterfly image search](https://raw.githubusercontent.com/anand-92/ultimate-image-gen-mcp/main/showcase/examples/butterfly_image_search.png)

### Different Resolutions

**512px (fastest)**
![Cat 512px](https://raw.githubusercontent.com/anand-92/ultimate-image-gen-mcp/main/showcase/examples/cat_512px.png)

**1K**
![Rose 1K](https://raw.githubusercontent.com/anand-92/ultimate-image-gen-mcp/main/showcase/examples/rose_1k.png)

**2K**
![Cyberpunk 2K](https://raw.githubusercontent.com/anand-92/ultimate-image-gen-mcp/main/showcase/examples/cyberpunk_2k.png)

---

## Quick Start

### Prerequisites
- Python 3.11+
- [Google Gemini API key](https://makersuite.google.com/app/apikey) (free tier available)

### Installation

**Using uvx (recommended — no install needed):**
```bash
uvx ultimate-gemini-mcp@latest
```

> **Note:** Use `@latest` to ensure uv always fetches the newest version from PyPI. Without it, uv may use a cached environment.

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


Config file locations:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

> **macOS `spawn uvx ENOENT` error**: Use the full path — find it with `which uvx`, then set `"command": "/Users/you/.local/bin/uvx"`.

### Claude Code

```bash
claude mcp add ultimate-gemini \
  --env GEMINI_API_KEY=your-api-key \
  -- uvx ultimate-gemini-mcp@latest
```

### Cursor

Add to `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "ultimate-gemini": {
      "command": "uvx",
      "args": ["ultimate-gemini-mcp@latest"],
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

Generate an image with Gemini 3.1 Flash Image.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | string | required | Text description. Less is more — "Tony Hawk kickflip" beats a long description. The model with search can find references automatically. |
| `aspect_ratio` | string | `1:1` | One of: `1:1` `1:4` `1:8` `2:3` `3:2` `3:4` `4:1` `4:3` `4:5` `5:4` `8:1` `9:16` `16:9` `21:9` |
| `image_size` | string | `2K` | `512px`, `1K`, `2K`, or `4K` |
| `output_format` | string | `png` | `png`, `jpeg`, or `webp` |
| `reference_image_paths` | list | `[]` | Up to 14 local image paths (10 objects + 4 characters) |
| `enable_google_search` | bool | `false` | **USE THIS** for products, people, events — anything that exists now. The model searches Google for real info. |
| `enable_image_search` | bool | `false` | **USE THIS** for visual references. The model finds actual images to work from. This is huge — it can reference real photos of anyone/anything. |
| `thinking_level` | string | `minimal` | `minimal` (fast) or `high` (best quality) |
| `response_modalities` | list | `["TEXT","IMAGE"]` | `["TEXT","IMAGE"]`, `["IMAGE"]`, or `["TEXT"]` |
| `transparent_background` | bool | `false` | Produce a transparent PNG/WebP cut-out via the two-pass difference matte (~2x cost; see below) |
| `preserve_original` | bool | `true` | Also keep the pass-1 (white-background) image, not just the cut-out |
| `alpha_output_format` | string | `png` | Alpha-capable output format: `png` or `webp` |

**Image size guide:**
- `512px` — fastest, lowest cost (0.5K)
- `1K` — fast, good for testing (~1-2 MB)
- `2K` — recommended for most use cases (~3-5 MB)
- `4K` — maximum quality for production assets (~8-15 MB)

#### Transparent backgrounds — set one flag, get a real alpha cut-out

**Just set `transparent_background=true`.** You get back a ready-to-use transparent PNG/WebP (real alpha channel) at `transparent_path` — no manual masking, no second tool, no follow-up steps.

> Generating an **app icon or logo**? Use the dedicated [`generate_app_icon`](#generate_app_icon) tool instead — it forces square + transparent + 1024px PNG so the icon constraints can't be set wrong.

Under the hood this is a **two-pass difference matte**. The subject is rendered once on a pure white (`#FFFFFF`) background, that image is edited to a pure black (`#000000`) background, and the two frames are combined to solve for alpha per pixel: since `obs_white − obs_black = (1−α)·255` on every channel, `α = 1 − mean(obs_white − obs_black)/255`, and the foreground colour is un-premultiplied from the black frame. Because there's no colour key, there's no green spill/halo; alpha is fractional, so soft edges, glow, glass, and faint shadows all survive. Pillow-only, zero ML downloads — but it costs a **second model call** (~2x tokens/latency).

The technique assumes the edit pass changed *only* the background. If the model drifts the subject between passes, the matte degrades — the result still returns (`aligned`/`alignment_error` flag it, with a loud `post_processing_warnings` entry) so you can decide whether to regenerate.

Each returned image gains: `transparent_path`, `background_removed`, `background_removal_mode` (`"difference_matte"`), `aligned`, `alignment_error`, `alpha_output_format`, and `post_processing_warnings`. By default the pass-1 (white-background) original is preserved alongside the cut-out (`preserve_original=true`).

```jsonc
// generate_image(prompt="a friendly robot mascot", transparent_background=true)
{
  "images": [{
    "path": "/path/to/a-friendly-robot-mascot-...png",            // pass-1 (white bg)
    "transparent_path": "/path/to/a-friendly-robot-mascot-...-transparent.png",
    "background_removed": true,
    "background_removal_mode": "difference_matte",
    "aligned": true,
    "alignment_error": 0.004,
    "alpha_output_format": "png",
    "post_processing_warnings": []
  }]
}
```

It nails crisp-edged subjects and soft glow/glass. The one failure mode is the edit pass drifting the subject (flagged via `aligned: false`) — regenerate if edges look ghosted.

---

### `generate_app_icon`

Purpose-built for **app icons and logos**. Square, transparent, and 1024px are **forced** — there is no `aspect_ratio`, `image_size`, `output_format`, or `transparent_background` knob to get wrong. Every result is a real alpha-channel PNG at `transparent_path`, ready to drop into a `.iconset` directory and convert with `iconutil -c icns`.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | string | required | Describe the icon/logo mark only — framing & transparency are handled |
| `reference_image_paths` | str \| list | `null` | Brand/style reference image path(s), up to 14 |
| `enable_google_search` | bool | `false` | Ground design in real web references |
| `enable_image_search` | bool | `false` | Use Google Image Search for visual context |
| `thinking_level` | string | `high` | `minimal` or `high` (icons reward `high`) |
| `allow_icon_words_in_prompt` | bool | `false` | Escape hatch — bypass the prompt guard only when a word like "logo" is genuinely part of the subject |

> **The `prompt` must describe ONLY the subject, never the deliverable.** This tool already turns whatever you describe *into* an icon, so framing words like "app icon", "logo", "favicon", or "squircle" in the prompt are rejected (set `allow_icon_words_in_prompt=true` only if such a word is literally part of the depicted subject). Right: `"a glowing electric-blue magnifying glass over a network graph"`. Wrong: `"an app icon of a magnifying glass"`.

```jsonc
// generate_app_icon(prompt="a glowing electric-blue magnifying glass over a network graph")
{
  "images": [{
    "transparent_path": "/path/to/...-transparent.png",  // square, 1024px, alpha
    "background_removed": true,
    "alpha_output_format": "png"
  }]
}
```

---

### `batch_generate`

Generate multiple images in parallel.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompts` | list | required | List of prompt strings (max 8) |
| `aspect_ratio` | string | `1:1` | Aspect ratio applied to all images |
| `image_size` | string | `2K` | Resolution for all images |
| `output_format` | string | `png` | Format for all images |
| `response_modalities` | list | `["TEXT","IMAGE"]` | Modalities for all images |
| `batch_size` | int | `8` | Max concurrent requests |
| `enable_image_search` | bool | `false` | Use Google Image Search for visual context |
| `thinking_level` | string | `minimal` | `minimal` or `high` |
| `transparent_background` | bool | `false` | Apply the two-pass difference matte to every image (each costs a second model call) |
| `preserve_original` | bool | `true` | Keep the pass-1 (white-background) images too |
| `alpha_output_format` | string | `png` | Transparent output format: `png` or `webp` |

---

## MCP Prompt Templates

26 expert prompt templates are available as MCP slash commands in Claude Code (type `/` to browse). Each template returns a crafted prompt and recommended parameters ready to pass directly to `generate_image` or `batch_generate`. For app icons and logos, use the dedicated [`generate_app_icon`](#generate_app_icon) tool instead.

| Command | Description | Default aspect ratio |
|---------|-------------|----------------------|
| `photography_shot` | Photorealistic shot with lens/lighting specs | 16:9 |
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
