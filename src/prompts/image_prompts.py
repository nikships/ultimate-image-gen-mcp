"""
MCP prompt templates for image generation.

Each prompt returns a crafted generation prompt plus recommended
`generate_image` / `batch_generate` parameters for the LLM to use.
"""

from typing import Any

from ..config.constants import MAX_BATCH_SIZE


def register_image_prompts(mcp_server: Any) -> None:
    """Register all image-generation prompt templates with the MCP server."""

    @mcp_server.prompt()
    def photography_shot(
        subject: str,
        lighting: str = "golden hour",
        aspect_ratio: str = "16:9",
        image_size: str = "2K",
    ) -> str:
        """Expert photorealistic photography prompt with lens and lighting specs."""
        return f"""You are a professional photographer directing a photo shoot.

Generate an image using the following crafted prompt:

PROMPT:
"Photorealistic photograph of {subject}. Shot on a Sony α7R V with a 85mm f/1.4 prime \
lens. Aperture f/1.8 for creamy background separation. {lighting.title()} lighting — \
warm directional light casting long shadows with rich colour temperature. \
Shallow depth of field, ultra-sharp subject, smooth bokeh background. \
HDR tonal range, true-to-life skin tones, natural colour grading. \
Captured at eye level, rule-of-thirds composition. \
Professional editorial quality, no AI artefacts."

Call `generate_image` with these parameters:
- prompt: (use the PROMPT above)
- aspect_ratio: "{aspect_ratio}"
- image_size: "{image_size}"
- response_modalities: ["TEXT", "IMAGE"]"""

    @mcp_server.prompt()
    def logo_design(
        brand_name: str,
        style: str = "modern minimalist",
        primary_color: str = "black",
        industry: str = "",
    ) -> str:
        """Professional logo design prompt optimised for brand identity."""
        industry_context = f" for a {industry} company" if industry else ""

        return f"""You are a senior brand identity designer.

Generate an image using the following crafted prompt:

PROMPT:
"{style.title()} logo design for "{brand_name}"{industry_context}. \
Primary colour: {primary_color}. \
Clean vector-style artwork, strong silhouette that works at any scale. \
Negative space used intentionally. Lettermark or wordmark — whichever suits the name best. \
Flat design with no gradients unless they serve the concept. \
Transparent or white background. \
Professional, timeless, instantly recognisable."

Call `generate_image` with these parameters:
- prompt: (use the PROMPT above)
- aspect_ratio: "1:1"
- image_size: "4K"
- response_modalities: ["IMAGE"]"""

    @mcp_server.prompt()
    def app_icon(
        concept: str,
        platform: str = "generic",
        style: str = "",
        primary_color: str = "",
    ) -> str:
        """High-quality app icon — premium, dimensional, export-ready.

        No baked-in style or palette defaults — the model is free to choose
        the most striking interpretation of the concept unless the caller
        explicitly passes ``style`` or ``primary_color``. The artwork fills
        the canvas edge-to-edge with no drop shadow, bezel, frame, glass
        trim, or outer outline, so the result drops straight into a
        ``.iconset`` directory for ``iconutil`` (or onto a store listing
        after flattening for iOS).
        """
        platform_notes = {
            "ios": (
                "iOS applies its own rounded-corner mask, so render the artwork "
                "as a full-bleed square (no rounded corners drawn in the artwork "
                "itself). The App Store also requires the final upload to be "
                "flattened onto an opaque background (no alpha channel)."
            ),
            "android": (
                "For an Android adaptive icon, keep the focal subject within the "
                "central safe zone (about the middle 66%, leaving ~25% padding "
                "on every side), since launchers crop to circles, squircles, "
                "and rounded squares. The artwork itself should still fill the "
                "canvas — the launcher does the cropping."
            ),
            "macos": (
                "The rounded-square (squircle) artwork fills the canvas — its "
                "rounded corners touch within ~1-2% of the canvas edges, with "
                "only tiny corner triangles outside the squircle. macOS draws "
                "its own shadow at render time, so do NOT bake a drop shadow, "
                "ground reflection, or surface into the image."
            ),
            "generic": (
                "Render the icon to fill the canvas with no surrounding mockup, "
                "presentation surface, or device-frame styling."
            ),
        }
        platform_note = platform_notes.get(platform.lower(), platform_notes["generic"])

        style_phrase = f"{style.strip().title()} style. " if style.strip() else ""
        palette_phrase = (
            f"Anchor the palette around {primary_color.strip()}, extended with "
            "complementary highlight and rim tones for dimensional shading. "
            if primary_color.strip()
            else "Choose a palette that makes the concept feel inevitable — rich tonal "
            "depth with clear light direction, not a single flat hue. "
        )

        return f"""You are a senior app icon designer.

Generate an image using the following crafted prompt:

PROMPT:
"App icon for {concept}. {style_phrase}{palette_phrase}A single bold focal form — \
no text, letters, numbers, or words anywhere in the image. \
\
The icon is premium and dimensional, in the spirit of macOS Sonoma, iOS 18, Vision Pro, \
Linear, Raycast, and Arc: a tangible, sculpted, three-dimensional focal subject living \
inside a deep atmospheric interior. Volumetric light spills from within — a soft inner \
glow radiating from the subject, fine specular highlights catching edges and facets, \
gentle haze pooling in the deeper recesses, sparse luminous particles or faint network \
filaments drifting through the space around the form. Cinematic lighting with a clear \
key, a subtle rim, and shadowed wells that give the interior real depth. \
Interpret '{concept}' as one unforgettable focal object — sculpted geometry, layered \
translucency, faceted crystal, glassy strata, liquid metal, luminous filament, organic \
bioluminescence, whatever interpretation hits hardest for this specific concept. \
Make a deliberate, distinctive creative choice — not the safest possible reading. \
\
COMPOSITION: The artwork IS the exported icon. It fills the canvas edge-to-edge as a \
rounded-square (squircle) — no outer frame, no bezel, no glass trim, no metallic border, \
no chrome ring, no outer outline, no drop shadow baked into the image, no ground plane, \
no presentation surface, no mockup framing. Inside the squircle, the focal subject sits \
centered with generous breathing room. Silhouette stays readable at 16x16 px while the \
rendering itself remains dimensional and cinematic. {platform_note}"

Call `generate_image` with these parameters:
- prompt: (use the PROMPT above)
- aspect_ratio: "1:1"
- image_size: "2K"
- transparent_background: true
- alpha_output_format: "png"
- response_modalities: ["IMAGE"]

The resulting transparent PNG is ready to drop straight into a `.iconset` directory and \
convert to `.icns` via `iconutil`, or to upload as a store listing asset. For an iOS App \
Store submission, flatten onto an opaque background first (Apple rejects icons that \
contain an alpha channel)."""

    @mcp_server.prompt()
    def cinematic_scene(
        subject: str,
        mood: str,
        setting: str,
        time_of_day: str = "golden hour",
    ) -> str:
        """Film-still prompt with cinematography language and colour grading."""
        return f"""You are a cinematographer composing a film still.

Generate an image using the following crafted prompt:

PROMPT:
"Cinematic film still of {subject} in {setting}. \
Mood: {mood}. Time of day: {time_of_day}. \
Shot on ARRI Alexa 35 with a 35mm anamorphic lens — characteristic horizontal lens flares. \
Colour grade: desaturated midtones with crushed blacks and a subtle warm highlight roll-off. \
Film grain at ISO 800. Shallow focus with deliberate rack-focus blur on background elements. \
Dramatic chiaroscuro lighting. \
Scene feels pulled from a prestige feature film — narrative tension, visual poetry."

Call `generate_image` with these parameters:
- prompt: (use the PROMPT above)
- aspect_ratio: "21:9"
- image_size: "2K"
- response_modalities: ["TEXT", "IMAGE"]"""

    @mcp_server.prompt()
    def product_mockup(
        product: str,
        background: str = "studio white",
        hero_shot: bool = True,
    ) -> str:
        """Commercial product photography prompt for e-commerce and marketing."""
        shot_style = (
            "Hero shot — product centred, slightly elevated angle, bold and confident"
            if hero_shot
            else "Lifestyle context shot — product shown in natural use environment"
        )
        aspect = "1:1" if hero_shot else "4:5"

        return f"""You are a commercial product photographer.

Generate an image using the following crafted prompt:

PROMPT:
"High-end commercial product photograph of {product}. \
Background: {background}. \
{shot_style}. \
Studio strobe lighting with a large octabox key light and subtle fill reflector — \
no harsh shadows, clean specular highlights that reveal material texture. \
Colour-accurate rendering: true whites, saturated brand colours. \
Razor-sharp focus across the entire product. \
No props unless they reinforce brand story. \
Retouched to e-commerce/advertising standard — immaculate, aspirational."

Call `generate_image` with these parameters:
- prompt: (use the PROMPT above)
- aspect_ratio: "{aspect}"
- image_size: "2K"
- response_modalities: ["TEXT", "IMAGE"]"""

    @mcp_server.prompt()
    def batch_storyboard(
        concept: str,
        num_scenes: int = 4,
        aspect_ratio: str = "16:9",
        image_size: str = "2K",
    ) -> str:
        """Multi-scene storyboard — instructs the LLM to call batch_generate."""
        num_scenes = min(num_scenes, MAX_BATCH_SIZE)

        scene_descriptions = "\n".join(
            f"  Scene {i + 1}: [describe a distinct moment that advances the story — \
different camera angle, lighting change, or narrative beat from Scene {i}]"
            for i in range(num_scenes)
        )

        return f"""You are a visual development artist creating a storyboard for: "{concept}"

Your task is to:
1. Write {num_scenes} distinct scene prompts that together tell a coherent visual story.
2. Each scene should vary in: camera angle, lighting, distance (wide/medium/close-up), \
and emotional beat.
3. Maintain consistent characters, colour palette, and art direction across all scenes.

Scene breakdown to flesh out:
{scene_descriptions}

Once you have crafted all {num_scenes} scene prompts, call `batch_generate` with:
- prompts: [list of all {num_scenes} crafted scene prompt strings]
- aspect_ratio: "{aspect_ratio}"
- image_size: "{image_size}"
- response_modalities: ["TEXT", "IMAGE"]

`batch_generate` processes all scenes in parallel, so all {num_scenes} images will be \
ready at the same time. Cap is {MAX_BATCH_SIZE} scenes maximum."""

    @mcp_server.prompt()
    def macro_shot(
        subject: str,
        detail: str,
        texture_adjective: str = "intricate",
        material: str = "organic",
        lighting_direction: str = "right",
        background_color: str = "neutral",
    ) -> str:
        """Extreme macro photography prompt for microscopic detail."""
        return f"""You are a specialist macro photographer.

Generate an image using the following crafted prompt:

PROMPT:
"Extreme macro photography of {subject}. Shot on a 100mm macro lens at f/2.8. \
Incredibly shallow depth of field. The focus is razor-sharp on {detail}, \
revealing microscopic textures, {texture_adjective} surfaces, and fine {material} details. \
Lighting is a single, hard micro-snoot from the {lighting_direction}, creating high-contrast micro-shadows. \
Background is a completely blurred out {background_color}."

Call `generate_image` with these parameters:
- prompt: (use the PROMPT above)
- aspect_ratio: "1:1"
- image_size: "2K"
- response_modalities: ["TEXT", "IMAGE"]"""

    @mcp_server.prompt()
    def fashion_portrait(
        subject: str,
        clothing: str,
        material: str,
        shadow_pattern: str = "window blinds",
        background_material: str = "textured concrete",
    ) -> str:
        """Editorial fashion portrait with dramatic lighting and texture."""
        return f"""You are a high-end fashion photographer.

Generate an image using the following crafted prompt:

PROMPT:
"Editorial fashion portrait of {subject}. Shot in a studio setup. \
Lighting features a harsh gobo projecting a shadow pattern of {shadow_pattern} \
across the subject's face and {background_material}. \
The subject is wearing {clothing} made of {material}, which catches the light. \
Hyper-detailed skin texture, visible pores, natural skin flaws. \
85mm lens, f/8 for total sharpness."

Call `generate_image` with these parameters:
- prompt: (use the PROMPT above)
- aspect_ratio: "4:5"
- image_size: "2K"
- response_modalities: ["TEXT", "IMAGE"]"""

    @mcp_server.prompt()
    def technical_cutaway(
        object_system: str,
        internal_element_1: str,
        internal_element_2: str,
    ) -> str:
        """Hand-drawn technical cutaway diagram in the style of Stephen Biesty."""
        return f"""You are a technical illustrator specializing in educational cutaways.

Generate an image using the following crafted prompt:

PROMPT:
"A highly detailed, technical cutaway diagram of {object_system} in the intricate, \
hand-drawn style of Stephen Biesty. The drawing reveals the internal mechanics, \
{internal_element_1}, and {internal_element_2}. Clean white background, precise linework, \
watercolor shading, and neat, minimalist typography pointing to various components."

Call `generate_image` with these parameters:
- prompt: (use the PROMPT above)
- aspect_ratio: "3:2"
- image_size: "4K"
- response_modalities: ["IMAGE"]"""

    @mcp_server.prompt()
    def flat_lay(
        theme: str,
        surface: str,
        props: list[str],
        colors: list[str],
    ) -> str:
        """Flat lay overhead photography with geometric arrangement."""
        props_str = ", ".join(props)
        colors_str = " and ".join(colors)
        return f"""You are a commercial still-life photographer.

Generate an image using the following crafted prompt:

PROMPT:
"Flat lay overhead photography of {theme}. Arranged meticulously on a {surface} surface. \
The composition includes {props_str} arranged in a pleasing geometric grid (knolling). \
Soft, diffuse window light coming from the top left, creating long, soft shadows. \
High resolution, vibrant and color-coordinated palette centering around {colors_str}."

Call `generate_image` with these parameters:
- prompt: (use the PROMPT above)
- aspect_ratio: "1:1"
- image_size: "2K"
- response_modalities: ["TEXT", "IMAGE"]"""

    @mcp_server.prompt()
    def action_freeze(
        subject: str,
        action: str,
        location: str,
        element: str = "water",
    ) -> str:
        """High-speed action shot with frozen movement and motion-blurred background."""
        return f"""You are an action sports photographer.

Generate an image using the following crafted prompt:

PROMPT:
"A dynamic, high-speed action shot of {subject} performing {action} in {location}. \
The subject is frozen perfectly in time, illuminated by a high-speed strobe flash, \
while the background exhibits severe motion blur to convey intense speed. \
Droplets/particles of {element} are suspended in mid-air, catching the rim light. \
Low angle, wide field of view."

Call `generate_image` with these parameters:
- prompt: (use the PROMPT above)
- aspect_ratio: "16:9"
- image_size: "2K"
- response_modalities: ["TEXT", "IMAGE"]"""

    @mcp_server.prompt()
    def night_street(
        location: str,
        light_source: str = "neon sign",
        color: str = "cyan",
        surface: str = "wet asphalt",
    ) -> str:
        """Haunting, moody night street photograph with low light and cinematic grading."""
        return f"""You are a night street photographer.

Generate an image using the following crafted prompt:

PROMPT:
"A haunting, moody night street photograph of {location}. Shot on a 50mm lens at f/1.4 \
for excellent low-light gathering. The scene is illuminated only by practical light \
sources: a glowing {light_source} casting a {color} pool of light on the {surface}. \
Deep, crushed blacks, moody cinematic teal-and-orange color grading."

Call `generate_image` with these parameters:
- prompt: (use the PROMPT above)
- aspect_ratio: "16:9"
- image_size: "2K"
- response_modalities: ["TEXT", "IMAGE"]"""

    @mcp_server.prompt()
    def drone_aerial(
        location: str,
        element_1: str,
        element_2: str,
    ) -> str:
        """Drone aerial photography looking straight down with golden hour light."""
        return f"""You are a drone photographer.

Generate an image using the following crafted prompt:

PROMPT:
"Drone aerial photography looking straight down at {location}. \
The composition focuses on the stark, abstract geometric patterns formed by \
{element_1} contrasting with {element_2}. The lighting is low-angle \
'golden hour' sunlight, creating long, dramatic, stretching shadows that emphasize \
the topography and textures of the ground."

Call `generate_image` with these parameters:
- prompt: (use the PROMPT above)
- aspect_ratio: "4:5"
- image_size: "4K"
- response_modalities: ["IMAGE"]"""

    @mcp_server.prompt()
    def stylized_3d_render(
        subject: str,
        material: str,
        rim_light_color: str = "vibrant pink",
        glow_color: str = "soft white",
    ) -> str:
        """Hyper-realistic 3D render of a cute, stylized subject with subsurface scattering."""
        return f"""You are a 3D artist specializing in high-end character renders.

Generate an image using the following crafted prompt:

PROMPT:
"A hyper-realistic 3D render of a cute, stylized {subject} made of {material}. \
Rendered in Unreal Engine 5 with subsurface scattering making the material look soft \
and slightly translucent. Studio lighting with a {rim_light_color} rim light and a \
{glow_color} ambient glow. The character is placed against an infinite cyclorama background."

Call `generate_image` with these parameters:
- prompt: (use the PROMPT above)
- aspect_ratio: "1:1"
- image_size: "2K"
- response_modalities: ["IMAGE"]"""

    @mcp_server.prompt()
    def sem_microscopy(
        subject: str,
        color_1: str,
        color_2: str,
    ) -> str:
        """Scanning Electron Microscope (SEM) style image with false-color imaging."""
        return f"""You are a scientific visualization specialist.

Generate an image using the following crafted prompt:

PROMPT:
"Scanning Electron Microscope (SEM) style image of {subject}. \
False-color imaging using a palette of {color_1} and {color_2}. \
Extreme magnification revealing alien-like, repeating geometric structures, \
sharp jagged edges, and deep porous cavities. High contrast, highly scientific \
and clinical aesthetic."

Call `generate_image` with these parameters:
- prompt: (use the PROMPT above)
- aspect_ratio: "1:1"
- image_size: "2K"
- response_modalities: ["IMAGE"]"""

    @mcp_server.prompt()
    def double_exposure(
        primary_subject: str,
        secondary_scene: str,
        background_color: str = "off-white",
    ) -> str:
        """Double exposure photographic art blending subject and scene."""
        return f"""You are a digital artist specializing in double exposure photography.

Generate an image using the following crafted prompt:

PROMPT:
"Double exposure photographic art. The primary silhouette is a {primary_subject}, \
filled entirely with a secondary image of {secondary_scene}. \
The edges of the silhouette softly blend into a {background_color} background. \
High contrast, ethereal, moody, with the textures of the {secondary_scene} \
interacting flawlessly with the contours of the {primary_subject}."

Call `generate_image` with these parameters:
- prompt: (use the PROMPT above)
- aspect_ratio: "2:3"
- image_size: "2K"
- response_modalities: ["IMAGE"]"""

    @mcp_server.prompt()
    def architectural_viz(
        structure: str,
        style: str,
        materials: list[str],
        landscape: str,
        time_of_day: str = "golden hour",
    ) -> str:
        """High-end architectural visualization with accurate lighting and textures."""
        materials_str = ", ".join(materials)
        return f"""You are an architectural visualization expert.

Generate an image using the following crafted prompt:

PROMPT:
"Architectural Visualization of a {structure} in {style} style. \
Materials: {materials_str}. Surrounding landscape: {landscape}. \
Time of day: {time_of_day}. Lighting: Primary light source from the sun, \
accurate ray-traced reflections on glass and water surfaces. \
Camera: Two-point perspective, low angle, tilt-shift lens for vertical correction."

Call `generate_image` with these parameters:
- prompt: (use the PROMPT above)
- aspect_ratio: "3:2"
- image_size: "4K"
- response_modalities: ["TEXT", "IMAGE"]"""

    @mcp_server.prompt()
    def isometric_illustration(
        location: str,
        aesthetic: str,
        colors: list[str],
        activity: str,
    ) -> str:
        """Isometric 3D illustration with orthographic camera and vibrant colors."""
        colors_str = ", ".join(colors)
        return f"""You are a digital illustrator specializing in isometric art.

Generate an image using the following crafted prompt:

PROMPT:
"Isometric 3D Illustration of {location}. Aesthetic: {aesthetic}. \
Color palette: {colors_str}. Activity: {activity}. \
Lighting: Global illumination, soft ambient occlusion, orthographic camera projection. \
Background: Solid neutral color, isolated object."

Call `generate_image` with these parameters:
- prompt: (use the PROMPT above)
- aspect_ratio: "1:1"
- image_size: "2K"
- response_modalities: ["IMAGE"]"""

    @mcp_server.prompt()
    def food_photography(
        dish: str,
        plating_style: str = "Michelin Star",
        surface_material: str = "dark slate",
        vibe: str = "elegant",
    ) -> str:
        """High-end food photography with backlighting and specular highlights."""
        return f"""You are a professional food photographer.

Generate an image using the following crafted prompt:

PROMPT:
"Food Photography of {dish}. Plating: {plating_style} on a {surface_material} surface. \
Lighting: Backlit with a large diffuser, creating specular highlights on the \
glossy parts of the food. Vibe: {vibe}. Camera: 105mm macro lens at a 45-degree angle."

Call `generate_image` with these parameters:
- prompt: (use the PROMPT above)
- aspect_ratio: "4:5"
- image_size: "2K"
- response_modalities: ["TEXT", "IMAGE"]"""

    @mcp_server.prompt()
    def motion_blur(
        subject: str,
        action: str,
        blur_color: str,
        background: str = "dark and moody",
    ) -> str:
        """In-camera motion blur sequence with rear-curtain sync strobe."""
        return f"""You are an experimental photographer using slow-shutter techniques.

Generate an image using the following crafted prompt:

PROMPT:
"In-Camera Motion Blur Sequence of {subject} performing {action}. \
Technique: Slow shutter (1/15th sec) with rear-curtain sync strobe flash. \
Visual Result: The subject's core is frozen and sharp, while the movement drags \
into a smooth, smeared trail of {blur_color} light. Setting: {background}."

Call `generate_image` with these parameters:
- prompt: (use the PROMPT above)
- aspect_ratio: "16:9"
- image_size: "2K"
- response_modalities: ["TEXT", "IMAGE"]"""

    @mcp_server.prompt()
    def typography_physical(
        text: str,
        location: str,
        material: str,
    ) -> str:
        """Typography embedded into a physical environment with accurate lighting."""
        return f"""You are a graphic designer and environmental artist.

Generate an image using the following crafted prompt:

PROMPT:
"Typography embedded into physical environment. Text: '{text}'. \
Environment: {location}. Integration: The text is constructed out of {material}. \
Lighting: The text interacts with the environment's light, casting accurate \
shadows onto nearby surfaces. Camera: Eye-level, wide angle, high dynamic range."

Call `generate_image` with these parameters:
- prompt: (use the PROMPT above)
- aspect_ratio: "16:9"
- image_size: "4K"
- response_modalities: ["IMAGE"]"""

    @mcp_server.prompt()
    def retro_futurism(
        device: str,
        style: str = "1970s Cassette Futurism",
        glow_color: str = "amber",
    ) -> str:
        """Analog sci-fi / retro-futurism with chunky tech and CRT screens."""
        return f"""You are a concept artist for a 1970s science fiction film.

Generate an image using the following crafted prompt:

PROMPT:
"Retro-Futurism / Analog Sci-Fi depiction of {device}. Design Language: {style}. \
Features: chunky buttons, CRT screens, scratched paint, dust in crevices. \
Lighting: Harsh fluorescent overhead lighting, glowing {glow_color} LED indicators. \
Camera: Polaroid SX-70 emulation, slightly soft focus, muted contrast."

Call `generate_image` with these parameters:
- prompt: (use the PROMPT above)
- aspect_ratio: "4:3"
- image_size: "2K"
- response_modalities: ["IMAGE"]"""

    @mcp_server.prompt()
    def surreal_dreamscape(
        object: str,
        twist: str,
        location: str,
    ) -> str:
        """Surrealism / Dreamscape with impossible physics and ethereal light."""
        return f"""You are a surrealist digital artist.

Generate an image using the following crafted prompt:

PROMPT:
"Surrealism / Dreamscape art of an ordinary {object}. Surreal Twist: The object is \
{twist}. Environment: {location}. Physics: Defying gravity, floating elements. \
Lighting: Ethereal, omnidirectional soft light with no visible source. \
Color Grading: Pastel tones, low contrast, hazy atmosphere."

Call `generate_image` with these parameters:
- prompt: (use the PROMPT above)
- aspect_ratio: "1:1"
- image_size: "2K"
- response_modalities: ["IMAGE"]"""

    @mcp_server.prompt()
    def character_sheet(
        character: str,
        clothing: str,
        features: list[str],
    ) -> str:
        """Character concept art sheet with multiple poses and clean rendering."""
        features_str = ", ".join(features)
        return f"""You are a character designer for a video game studio.

Generate an image using the following crafted prompt:

PROMPT:
"Character Concept Art Sheet of {character}. Features: {features_str}. \
Outfit: {clothing}. Layout: A-Pose front, 3/4 profile, and action pose. \
Background: Neutral medium gray. Rendering Style: Clean line art with \
flat cel-shading, concept art industry standard."

Call `generate_image` with these parameters:
- prompt: (use the PROMPT above)
- aspect_ratio: "3:2"
- image_size: "4K"
- response_modalities: ["IMAGE"]"""

    @mcp_server.prompt()
    def pbr_texture(
        material_type: str,
        micro_structure: str,
        imperfections: list[str],
    ) -> str:
        """Seamless PBR texture map visualization with raking side light."""
        imperfections_str = ", ".join(imperfections)
        return f"""You are a material artist for real-time engines.

Generate an image using the following crafted prompt:

PROMPT:
"Seamless PBR texture map visualization of {material_type}. \
Details: {micro_structure}. Imperfections: {imperfections_str}. \
Lighting: Raking side light to emphasize normal map depth and bump. \
Composition: Flat 2D plane facing the camera filling the entire frame."

Call `generate_image` with these parameters:
- prompt: (use the PROMPT above)
- aspect_ratio: "1:1"
- image_size: "2K"
- response_modalities: ["IMAGE"]"""

    @mcp_server.prompt()
    def historical_photo(
        era: str,
        subject: str,
        location: str,
        film_emulation: str = "wet plate collodion",
    ) -> str:
        """Historical period piece photography with period-accurate details."""
        return f"""You are a historical archivist and photographer.

Generate an image using the following crafted prompt:

PROMPT:
"Historical Period Piece Photography of {subject} in the era of {era}. \
Location: {location}. Lighting: Natural light mimicking candlelight. \
Post-Processing: {film_emulation} emulation, heavy optical vignetting, \
period-accurate props and costumes."

Call `generate_image` with these parameters:
- prompt: (use the PROMPT above)
- aspect_ratio: "4:5"
- image_size: "2K"
- response_modalities: ["TEXT", "IMAGE"]"""

    @mcp_server.prompt()
    def bioluminescent_nature(
        subject: str,
        glow_color: str,
        location: str,
    ) -> str:
        """Bioluminescent nature macro with long exposure aesthetic."""
        return f"""You are a nature photographer exploring bioluminescence.

Generate an image using the following crafted prompt:

PROMPT:
"Bioluminescent Nature Macro of {subject}. Modifications: Emitting a natural, \
glowing {glow_color} bioluminescence. Environment: {location}. \
Background: Pitch black with faint out-of-focus glowing particles. \
Camera: Extreme Macro, long exposure feel, high ISO grain."

Call `generate_image` with these parameters:
- prompt: (use the PROMPT above)
- aspect_ratio: "1:1"
- image_size: "2K"
- response_modalities: ["TEXT", "IMAGE"]"""

    @mcp_server.prompt()
    def silhouette_shot(
        subject: str,
        action: str,
        focal_point: str,
    ) -> str:
        """Cinematic silhouette master shot with heavy backlighting."""
        return f"""You are a director of photography framing a silhouette shot.

Generate an image using the following crafted prompt:

PROMPT:
"Cinematic Silhouette Master Shot of {subject} performing {action}. \
Background Focal Point: Massive {focal_point}, extremely bright. \
Lighting: Pure black silhouette, absolutely zero fill light, heavy back-lit fog \
wrapping around the subject's edges. Camera: Ultra-wide cinematic aspect ratio (2.35:1), \
deep depth of field."

Call `generate_image` with these parameters:
- prompt: (use the PROMPT above)
- aspect_ratio: "21:9"
- image_size: "4K"
- response_modalities: ["TEXT", "IMAGE"]"""

    # Every prompt above is a closure registered with the MCP server via the
    # `@mcp_server.prompt()` decorator. Static analyzers (Pyright, etc.) can't
    # see the decorator's side effects on `mcp_server` and flag each closure as
    # "not accessed". Referencing them here makes the registrations explicit to
    # the analyzer without changing runtime behaviour.
    _registered_prompts = (
        photography_shot,
        logo_design,
        app_icon,
        cinematic_scene,
        product_mockup,
        batch_storyboard,
        macro_shot,
        fashion_portrait,
        technical_cutaway,
        flat_lay,
        action_freeze,
        night_street,
        drone_aerial,
        stylized_3d_render,
        sem_microscopy,
        double_exposure,
        architectural_viz,
        isometric_illustration,
        food_photography,
        motion_blur,
        typography_physical,
        retro_futurism,
        surreal_dreamscape,
        character_sheet,
        pbr_texture,
        historical_photo,
        bioluminescent_nature,
        silhouette_shot,
    )
    del _registered_prompts
