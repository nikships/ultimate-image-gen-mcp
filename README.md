![Ultimate Gemini MCP Banner](https://raw.githubusercontent.com/anand-92/ultimate-image-gen-mcp/main/showcase/banner.png)

# Gemini 3 Pro Image MCP Server 🎨

> Professional MCP server for Google's Gemini 3 Pro Image - state-of-the-art image generation with advanced reasoning, high-resolution output, and Google Search grounding.

## ✨ Features

### Gemini 3 Pro Image Capabilities
- **High-Resolution Output**: Generate images in 1K, 2K, and 4K resolutions
- **Advanced Text Rendering**: Create legible, stylized text in infographics, menus, diagrams, and marketing assets
- **Up to 14 Reference Images**: Mix up to 14 reference images (6 objects + 5 humans) for consistent style and characters
- **Google Search Grounding**: Use real-time data from Google Search (weather, stocks, events, maps)
- **Thinking Mode**: Model uses reasoning process to refine composition before generating final output

### Advanced Capabilities
- 🤖 **AI Prompt Enhancement**: Automatically optimize prompts using Gemini Flash for superior results
- 🔍 **Google Search Integration**: Generate images based on real-time information
- 🎨 **Reference Images**: Use up to 14 images for style consistency and character preservation
- 📐 **Flexible Aspect Ratios**: Support for 10 aspect ratios (1:1, 16:9, 9:16, 3:2, 4:3, 4:5, 5:4, 2:3, 3:4, 21:9)
- 💭 **Thought Process Visibility**: See the model's thinking process (interim images and reasoning)
- 🚀 **Batch Processing**: Generate multiple images efficiently with parallel processing
- 🎯 **Dual Modalities**: Get both text explanations and images in responses

### Production Ready
- Comprehensive error handling and validation
- Configurable settings via environment variables
- Detailed logging and debugging
- MCP resources for configuration and model information

## 🎬 Showcase - Gemini 3 Pro Image Features

> **Gemini 3 Pro Image** - Experience state-of-the-art image generation with advanced reasoning and high-resolution output.

### Key Features in Action

All images can be generated with **4K resolution** and **optional AI prompt enhancement**.

### Example Use Cases

**1. High-Resolution Professional Assets**
```
Generate a 4K image of "modern office interior with natural lighting"
- Model: gemini-3-pro-image-preview
- Image Size: 4K
- Aspect Ratio: 16:9
```

**2. Real-Time Data Visualization**
```
Generate an image with Google Search grounding:
"Visualize the current weather forecast for the next 5 days in San Francisco as a clean, modern weather chart. Add a visual on what I should wear each day"
- Enable Google Search: true
- Aspect Ratio: 16:9
```

**3. Reference Image Consistency**
```
Use reference images to maintain consistent characters:
- Provide up to 5 human reference images
- Provide up to 6 object reference images
- Generate "An office group photo of these people, they are making funny faces"
```

**4. Advanced Text Rendering**
```
Generate infographics, menus, or diagrams with legible text:
"Create a restaurant menu with elegant typography showing appetizers, mains, and desserts"
- Image Size: 2K
- Aspect Ratio: 3:4
```

### 🔥 Why Gemini 3 Pro Image Is Powerful

1. **State-of-the-Art Quality**: Built-in generation capabilities up to 4K resolution
2. **Advanced Reasoning**: Thinking mode refines composition before final output
3. **Real-Time Grounding**: Google Search integration for accurate, current data
4. **Character Consistency**: Use up to 14 reference images for maintaining style
5. **Professional Features**: Advanced text rendering for infographics and marketing

## 🎨 Prompt Enhancement Showcase

See the power of AI prompt enhancement! When enabled, simple prompts can be transformed into detailed, cinematic descriptions:

**Original:** "A fierce wolf wearing the black symbiote Spider-Man suit, web-slinging through city at night"

**Enhanced:** "A powerfully built Alaskan Tundra Wolf, snarling fiercely, wearing the matte black, viscous, wet-looking symbiote suit with exaggerated white spider emblem. Captured mid-air in dramatic web-slinging arc with taut glowing webbing. Extreme low-angle perspective, hyper-detailed neo-noir cityscape at midnight with rain-slicked asphalt. High-contrast cinematic lighting with deep shadows and electric neon rim lighting."

### Generated Images (2K, 16:9, Prompt Enhancement: ON)

**Wolf - Black Symbiote Suit**

![Wolf in Black Symbiote Suit](https://raw.githubusercontent.com/anand-92/ultimate-image-gen-mcp/main/showcase/examples/wolf_symbiote.png)

**Lion - Classic Red & Blue Suit**

![Lion in Classic Spider-Man Suit](https://raw.githubusercontent.com/anand-92/ultimate-image-gen-mcp/main/showcase/examples/lion_classic.png)

**Black Panther - Symbiote Suit**

![Panther in Symbiote Suit](https://raw.githubusercontent.com/anand-92/ultimate-image-gen-mcp/main/showcase/examples/panther_symbiote.png)

**Eagle - Classic Suit in Flight**

![Eagle in Spider-Man Suit](https://raw.githubusercontent.com/anand-92/ultimate-image-gen-mcp/main/showcase/examples/eagle_classic.png)

**Grizzly Bear - Symbiote Suit**

![Bear in Symbiote Suit](https://raw.githubusercontent.com/anand-92/ultimate-image-gen-mcp/main/showcase/examples/bear_symbiote.png)

**Fox - Classic Suit at Dusk**

![Fox in Spider-Man Suit](https://raw.githubusercontent.com/anand-92/ultimate-image-gen-mcp/main/showcase/examples/fox_classic.png)

All images generated with `enhance_prompt: true`, showcasing how simple descriptions can become photorealistic, cinematic masterpieces with dramatic lighting, detailed textures, and professional composition when enhancement is enabled.

## 📸 Photorealistic Capabilities

Gemini 3 Pro Image excels at creating incredibly realistic images of people in unusual and imaginative scenarios:

**Jensen Huang - GPU Surfing**

![Jensen surfing on GPU through cyberpunk city](https://raw.githubusercontent.com/anand-92/ultimate-image-gen-mcp/main/showcase/examples/jensen_gpu_surfing.png)
*Riding a giant NVIDIA GPU chip through a neon-lit cyberpunk cityscape*

**Elon Musk - Mars Chess Match**

![Elon playing chess with robot on Mars](https://raw.githubusercontent.com/anand-92/ultimate-image-gen-mcp/main/showcase/examples/elon_mars_chess.png)
*Playing chess with a humanoid robot on the surface of Mars, Earth visible in background*

**Jensen Huang - GPU Kitchen**

![Jensen cooking with GPU appliances](https://raw.githubusercontent.com/anand-92/ultimate-image-gen-mcp/main/showcase/examples/jensen_gpu_kitchen.png)
*Cooking breakfast in a high-tech kitchen where all appliances are GPUs with RGB lighting*

**Elon Musk - Cybertruck Symphony**

![Elon conducting Cybertruck orchestra](https://raw.githubusercontent.com/anand-92/ultimate-image-gen-mcp/main/showcase/examples/elon_cybertruck_symphony.png)
*Conducting a symphony orchestra made entirely of Tesla Cybertrucks in a concert hall*

**Jensen Huang - Underwater Data Center**

![Jensen scuba diving in data center](https://raw.githubusercontent.com/anand-92/ultimate-image-gen-mcp/main/showcase/examples/jensen_underwater_datacenter.png)
*Scuba diving in an underwater data center surrounded by glowing servers and tropical fish*

**Elon Musk - SpaceX Skateboarding**

![Elon skateboarding at SpaceX](https://raw.githubusercontent.com/anand-92/ultimate-image-gen-mcp/main/showcase/examples/elon_spacex_skateboard.png)
*Skateboarding through the SpaceX factory with a Starship rocket in the background*

These images demonstrate the model's exceptional ability to:
- Generate photorealistic human likenesses
- Blend reality with creative, surreal concepts
- Maintain accurate lighting and perspective
- Create detailed, believable environments
- Handle complex compositions with multiple elements

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- [Google Gemini API key](https://makersuite.google.com/app/apikey) (free)

### Installation

#### Option 1: Using uv (Recommended)
```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install and run the server
uvx ultimate-gemini-mcp
```

#### Option 2: Using pip
```bash
pip install ultimate-gemini-mcp
```

#### Option 3: From Source
```bash
git clone <repository-url>
cd ultimate-gemini-mcp
uv sync
```

### Configuration

Create a `.env` file in your project directory:
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

Or set environment variables directly:
```bash
export GEMINI_API_KEY=your_api_key_here
```

## 📖 Usage

### With Claude Desktop

Add to your `claude_desktop_config.json`:

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

**Important Notes:**

1. **Images are automatically saved** to `~/gemini_images` (your home directory). You can optionally set `OUTPUT_DIR` to customize this location:
   - **macOS**: `"OUTPUT_DIR": "/Users/yourusername/custom_folder"`
   - **Windows**: `"OUTPUT_DIR": "C:\\Users\\YourUsername\\custom_folder"`

2. **uvx path issues on macOS**: If you get `spawn uvx ENOENT` errors, use the full path to uvx:
   ```json
   "command": "/Users/yourusername/.local/bin/uvx"
   ```

**Config file locations:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### With Claude Code (VS Code)

```bash
# Add MCP server to Claude Code
claude mcp add ultimate-gemini \
  --env GEMINI_API_KEY=your-api-key \
  -- uvx ultimate-gemini-mcp
```

**Note**: Images are automatically saved to `~/gemini_images`. To customize, add `--env OUTPUT_DIR=/your/custom/path`.

### With Cursor

Add to Cursor's MCP configuration (`.cursor/mcp.json`):

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

**Note**: Images are automatically saved to `~/gemini_images`. Optionally add `"OUTPUT_DIR": "/your/custom/path"` to customize.

## 🎯 Available Models

### Gemini 3 Pro Image
- **gemini-3-pro-image-preview** (default): State-of-the-art image generation optimized for professional asset production with:
  - Built-in 1K, 2K, and 4K resolution support
  - Advanced text rendering capabilities
  - Up to 14 reference images for consistency
  - Google Search grounding for real-time data
  - Thinking mode with reasoning process
  - Support for both TEXT and IMAGE response modalities

## 🛠️ Tools

### `generate_image`

Generate professional images using Gemini 3 Pro Image with advanced features.

**Parameters:**
- `prompt` (required): Text description of the image to generate
- `model`: Model to use (default: gemini-3-pro-image-preview)
- `enhance_prompt`: Automatically enhance prompt using AI (default: false) - Enable for simple/vague prompts
- `aspect_ratio`: Aspect ratio like 1:1, 16:9, 9:16, 3:2, 4:5, etc. (default: 1:1)
- `image_size`: Resolution: 1K, 2K, or 4K (default: 1K)
- `output_format`: Image format: png, jpeg, webp (default: png)
- `reference_image_paths`: List of paths to reference images (up to 14 total)
  - Maximum 6 object images for high-fidelity inclusion
  - Maximum 5 human images for character consistency
- `enable_google_search`: Enable Google Search grounding for real-time data (default: false)
- `response_modalities`: Response types like ["TEXT", "IMAGE"] (default: both)

**Examples:**
```
1. Basic image generation:
   Generate an image of "a serene mountain landscape at sunset with a lake reflection"

2. High-resolution with specific aspect ratio:
   Generate a 4K image of "modern minimalist architecture" with aspect_ratio 16:9

3. With Google Search grounding:
   Generate an image with Google Search enabled: "Current weather map for New York City"

4. With reference images:
   Generate an image with reference_image_paths: ["/path/person1.png", "/path/person2.png"]
   and prompt: "An office group photo of these people making funny faces"
```

### `batch_generate`

Process multiple prompts efficiently with parallel batch processing.

**Parameters:**
- `prompts` (required): List of text prompts
- `model`: Model to use for all images
- `enhance_prompt`: Enhance all prompts (default: false) - Enable for simple/vague prompts
- `aspect_ratio`: Aspect ratio for all images
- `batch_size`: Parallel processing size (default: from config)

**Example:**
```
Batch generate images for these prompts:
1. "minimalist logo design for a tech startup"
2. "modern dashboard UI design"
3. "mobile app wireframe"
```

## 🎨 Advanced Features

### AI Prompt Enhancement

When enabled, the server uses Gemini Flash to automatically enhance your prompts:

**Original:** `a cat wearing a space helmet`

**Enhanced:** `A photorealistic portrait of a domestic tabby cat wearing a futuristic space helmet, close-up composition, warm studio lighting, detailed fur texture, reflective helmet visor showing subtle reflections, soft focus background, professional photography style`

This significantly improves image quality without requiring you to be a prompt engineering expert!

### Google Search Grounding

Generate images based on real-time data:

```
Generate an image with Google Search enabled:
- prompt: "Visualize the current weather forecast for San Francisco as a modern chart"
- enable_google_search: true
```

The response will include grounding metadata with search sources used.

### Reference Images for Consistency

Maintain consistent characters and objects across generations:

```
Generate an image with:
- prompt: "An office group photo of these people, they are making funny faces"
- reference_image_paths: ["/path/person1.png", "/path/person2.png", "/path/person3.png"]
- aspect_ratio: "5:4"
- image_size: "2K"
```

You can provide up to 14 reference images (max 6 objects, max 5 humans).

### High-Resolution Assets

Generate professional 4K assets:

```
Generate a 4K image of "minimalist logo design for a tech startup"
with image_size: "4K" and aspect_ratio: "1:1"
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key (required) | - |
| `OUTPUT_DIR` | Directory for generated images | `~/gemini_images` |
| `ENABLE_PROMPT_ENHANCEMENT` | Enable AI prompt enhancement | `false` |
| `ENABLE_BATCH_PROCESSING` | Enable batch processing | `true` |
| `DEFAULT_MODEL` | Default model | `gemini-3-pro-image-preview` |
| `DEFAULT_IMAGE_SIZE` | Default resolution | `2K` |
| `ENABLE_GOOGLE_SEARCH` | Enable Google Search grounding | `false` |
| `REQUEST_TIMEOUT` | API request timeout (seconds) | `60` |
| `MAX_BATCH_SIZE` | Maximum parallel batch size | `8` |
| `LOG_LEVEL` | Logging level | `INFO` |

## 📚 MCP Resources

### `models://list`
View all available models with descriptions and features.

### `settings://config`
View current server configuration.

## 🎭 Use Cases

### Web Development
- Hero images and banners
- UI/UX mockups and wireframes
- Logo and branding assets
- Placeholder images

### App Development
- App icons and splash screens
- User interface elements
- Marketing materials
- Documentation images

### Content Creation
- Blog post illustrations
- Social media graphics
- Presentation visuals
- Product mockups

### Creative Projects
- Character design iterations
- Concept art exploration
- Style variations
- Scene composition

## 📊 Gemini 3 Pro Image Features

| Feature | Support | Details |
|---------|---------|---------|
| Resolution Options | ✅ 1K, 2K, 4K | Built-in high-resolution generation |
| Reference Images | ✅ Up to 14 | 6 objects + 5 humans for consistency |
| Google Search Grounding | ✅ Real-time data | Weather, stocks, events, maps |
| Thinking Mode | ✅ Advanced reasoning | Visible thought process and interim images |
| Text Rendering | ✅ Advanced | Legible text in infographics, menus, diagrams |
| Aspect Ratios | ✅ 10 options | Full flexibility for any format |
| Response Modalities | ✅ TEXT + IMAGE | Dual output modes |
| Prompt Enhancement | ✅ Built-in | AI-powered optimization |
| Thought Signatures | ✅ Automatic | Preserved across multi-turn interactions |
| Best For | Professional assets, marketing, real-time visualization |

## 🐛 Troubleshooting

### "spawn uvx ENOENT" error
- **Cause**: Claude Desktop cannot find the `uvx` command in its PATH
- **Solution**: Use the full path to uvx in your config:
  ```json
  "command": "/Users/yourusername/.local/bin/uvx"
  ```
- Find your uvx location with: `which uvx`

### Custom output directory
- **Default**: Images are automatically saved to `~/gemini_images` in your home directory
- **Customize**: Set `OUTPUT_DIR` in your MCP config if you want a different location:
  ```json
  "env": {
    "GEMINI_API_KEY": "your-key",
    "OUTPUT_DIR": "/your/custom/path"
  }
  ```

### "GEMINI_API_KEY not found"
- Add your API key to `.env` or environment variables
- Get a free key at [Google AI Studio](https://makersuite.google.com/app/apikey)

### "Content blocked by safety filters"
- Modify your prompt to comply with content policies
- Try rephrasing without potentially sensitive content

### "Rate limit exceeded"
- Wait a few moments and try again
- Consider upgrading your API plan for higher limits

### Images not saving
- Check that OUTPUT_DIR exists and is writable
- Verify you have sufficient disk space
- Create the directory manually: `mkdir -p /path/to/your/images`

## 🤝 Contributing

Contributions are welcome! This project combines the best features from multiple MCP servers:
- mcp-image (TypeScript): Prompt enhancement and editing features
- nanobanana-mcp-server (Python): Architecture and FastMCP integration
- gemini-imagen-mcp-server (TypeScript): Imagen API support and batch processing

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

Built on the excellent work of:
- [mcp-image](https://github.com/shinpr/mcp-image) - Prompt enhancement concept
- [nanobanana-mcp-server](https://github.com/zhongweili/nanobanana-mcp-server) - FastMCP architecture
- [gemini-imagen-mcp-server](https://github.com/serkanhaslak/gemini-imagen-mcp-server) - Imagen integration

## 🔗 Links

- [Google AI Studio](https://makersuite.google.com/app/apikey) - Get your API key
- [Gemini API Documentation](https://ai.google.dev/gemini-api/docs)
- [Model Context Protocol](https://modelcontextprotocol.io/)

---

**Ready to create amazing AI-generated images?** Install now and start generating! 🚀
