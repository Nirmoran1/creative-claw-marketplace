# Nano Banana 2 (Gemini 3.1 Flash Image)

**Model ID:** `image/nano-banana-2`
**Edit Model:** Use `generate_image` with `image_url` parameter

Google's Gemini 3.1 Flash image generation model. Uses multimodal reasoning (not diffusion) — it processes images as visual tokens predicted autoregressively through the same reasoning pipeline that handles text. This makes it exceptional at understanding complex instructions and rendering text.

## Prompting Strategy

### Use Natural Language, Not Tags

Nano Banana 2 uses multimodal reasoning (not diffusion). Write prompts as natural sentences, not comma-separated keyword lists.

**Do this:**
> A frosted glass bottle on a slate surface, single dried chili beside it, late afternoon raking light from the right, soft neutral background fading to charcoal, editorial food photography aesthetic, shot on 85mm f/1.4.

**Not this:**
> frosted glass bottle, slate surface, chili, golden hour, dark background, editorial, masterpiece, best quality, 8k, trending on artstation

- Avoid quality boosters like "masterpiece, best quality, trending on artstation" — they have zero effect
- Skip weighted token syntax like `(subject:1.5)` — the model ignores it
- 1-3 sentences is optimal for general images; longer prompts are fine for text-heavy designs
- Provide context about intended use (e.g. "for a Brazilian high-end cookbook") to trigger appropriate styling decisions automatically

### Prompt Structure (Google's Recommended Order)

**[Subject + Adjectives] doing [Action] in [Location/Context]. [Composition/Camera Angle]. [Lighting/Atmosphere]. [Style/Media]. [Specific Constraint/Text].**

1. **Subject** — who or what is in the scene
2. **Composition** — framing, camera angle, perspective
3. **Action** — what's happening
4. **Location** — setting and environment
5. **Style** — artistic direction, mood, color palette

### Photographic Language

Camera terms map directly to visual treatments:
- "wide-angle shot" → expansive perspective
- "85mm portrait lens" → flattering compression, bokeh
- "shallow depth of field" → blurred background
- "bird's eye view" → top-down perspective
- "low-angle shot" → dramatic, imposing

### Lighting and Camera Control

Use photographer's language for precise control:
- Specify lighting: "soft diffused window light", "dramatic rim lighting", "golden hour backlight", "three-point softbox setup"
- Specify lens: "shot on 85mm f/1.4", "macro lens close-up", "wide-angle 24mm"
- Specify mood: "high-key ethereal", "low-key moody", "studio lit on white seamless"
- Film stocks: "Kodak Portra 400", "Fuji Velvia" trigger era-appropriate rendering
- Era grounding: "1960s aesthetic" automatically triggers film grain, desaturation, and period-accurate composition

### Artistic Styles

For non-photographic styles, be explicit about the medium:
- "watercolor painting with soft bleeding edges and paper texture"
- "Japanese flat illustration"
- "3D rendering with subsurface scattering"
- "pixel art with limited color palette"
- "oil painting with visible brushstrokes"
- "graphic novel style with heavy inking"

### Technical Content (Diagrams, Equations, Schematics)

Nano Banana 2 validates structural accuracy — flow arrows point in logical directions, anatomical labels point to correct structures, equations render with proper notation. Be explicit: label each element precisely (e.g., "Box 1: 'Receive Order' → Box 2: 'Process Payment'") rather than saying "a business flowchart."

### Handling Unwanted Elements (No Negative Prompts)

Nano Banana 2 does **not** support traditional negative prompts. Use positive framing instead — describe the desired scene so precisely that undesired elements are implicitly excluded:

- Instead of "no blur" → write "crisp sharp focus throughout the frame"
- Instead of "no people in background" → write "empty street" or "deserted plaza"
- Instead of "no watermarks" → write "clean pristine image"
- Avoid contradictions in prompts — don't combine "minimal white background" with "dense complex background details"

## Text Rendering

This is Nano Banana 2's headline feature. It validates text character-by-character before rendering.

### Critical Rule: Wrap Text in Double Quotes

Always put text you want rendered in `"double quotes"` with individual style specifications:

> Concert poster titled "MIDNIGHT BRASS" in tall condensed serif at top, saxophone player silhouetted against smoky amber spotlight, "JUNE 14-16" in small caps below, "BROOKLYN ARTS CENTER" in thin sans-serif at bottom, deep navy and warm gold palette.

### Text Best Practices

- Keep text elements to **3-5 per image**
- Use **larger text** whenever possible — small text at 1K resolution often blurs
- Stick to **short phrases** rather than full paragraphs
- Supports **multilingual rendering** (Japanese, Arabic, Chinese, Korean, etc.)
- For pixel-perfect accuracy on product labels or legal copy, generate the background with Nano Banana 2 and overlay text programmatically

## Parameters

| Parameter | Values | Notes |
|---|---|---|
| **Prompt** | string (max 50,000 chars) | Required. Natural language description |
| **Aspect Ratio** | auto, 21:9, 16:9, 3:2, 4:3, 5:4, 1:1, 4:5, 3:4, 2:3, 9:16, 4:1, 1:4, 8:1, 1:8 | "auto" analyzes prompt to pick optimal ratio. Extreme ratios (4:1, 1:4, 8:1, 1:8) are unique to Nano Banana 2 |
| **Resolution** | 0.5K ($0.06), 1K ($0.08), 2K ($0.12), 4K ($0.16) | Default: 1K. 0.5K is unique to Nano Banana 2 — great for quick prototypes |
| **Thinking Mode** | Minimal, High, Dynamic | Controls reasoning depth. Minimal = fastest. High = best quality for complex prompts. Dynamic = model decides |
| **Output Format** | PNG (default, lossless), JPEG, WebP | PNG for text-heavy/transparency, JPEG for photos, WebP for web |
| **Batch Size** | 1-4 images per call | Each image priced separately |
| **Safety Tolerance** | 1-6 | Default: 4. Increase if creative prompts get blocked |
| **Web Search** | enable_web_search | Adds $0.015/gen. Use for real-world subjects and data visualizations only |
| **Seed** | any integer | For reproducible generations |

### Cost Optimization Strategy

Generate 4 variations at 1K resolution, select the best, then regenerate the winner at 2K/4K. This avoids wasting 4K credits on iterations.

## Advanced Capabilities

### Character Consistency (Multi-Shot)

Upload 3-5 reference images to maintain character or brand consistency:
- Explicitly state: "Keep the person's facial features exactly the same as Image 1"
- Maintain identity while varying expressions, angles, and distances
- Accepts up to **14 reference images** in a single edit

### Dimensional Translation (2D to 3D)

- Convert floor plans to interior renders
- Transform sketches and doodles into polished assets
- Upload wireframes or grids to force specific compositions

### Google Search Grounding

Enable `enable_web_search` to let the model verify facts via Google Search before generating. Useful for:
- Data visualizations and infographics with real-world data
- Current events or timely subjects
- Diagrams that need factual accuracy

Skip for fictional or purely creative content — it adds $0.015/generation.

## Editing Workflow

To edit an image, call `generate_image` with `image_url` and `model: "image/nano-banana-2"`. No masking required — describe edits in plain English.

- **Background change:** "Change the background to a sunset beach. Keep the person exactly as they are."
- **Object removal:** "Remove the car from the left side and fill in naturally with the surrounding grass."
- **Style swap:** "Convert this photo to a watercolor painting style while keeping all subjects intact."
- **Text editing:** "Change the headline text to read 'SUMMER SALE' in the same font style."
- **Multi-image compositing:** Upload multiple source images and describe which elements from each to combine.

### Editing Tips

- **Edit, don't re-roll** — make conversational adjustments rather than regenerating from scratch
- State both what to change AND what to preserve
- Use high-quality, clear source images
- Assign distinct descriptions to each reference image
- Make one change per prompt for complex scenes
- Accepts up to **14 reference images** in a single edit

### Conversational Workflow

Rather than crafting one perfect prompt, start with an 80% correct output, then iterate:
1. Generate initial image
2. "Change the lighting to sunset and make the text neon blue"
3. "Move the subject slightly to the left and add fog"

## Example Prompts

### Product Photography
> A frosted glass bottle on slate surface, single dried chili beside it, late afternoon raking light, soft neutral background fading to charcoal, editorial food photography aesthetic.

### Typography Poster
> Concert poster titled "MIDNIGHT BRASS" in tall condensed serif at top, saxophone player silhouetted against smoky amber spotlight, "JUNE 14-16" in small caps below, "BROOKLYN ARTS CENTER" in thin sans-serif at bottom, deep navy and warm gold palette.

### Infographic
> Vertical coffee brewing methods chart with four sections: "POUR OVER" (V60 illustration), "FRENCH PRESS" (plunger diagram), "ESPRESSO" (portafilter sketch), "COLD BREW" (mason jar), with brew time and grind size in clean sans-serif, kraft texture background, muted earth tones.

### Bilingual Content
> Tea house loyalty card with "TENTH CUP FREE" in clean bold English at top, Chinese equivalent in brush-style below, ten circle stamps with three filled, minimalist sage green and cream scheme, small teapot icon.

## When to Use Nano Banana 2 vs Other Models

- **Use Nano Banana 2** when you need: fast generation, text in images, multilingual content, infographics, posters, UI mockups, or rapid iteration at low cost
- **Use Nano Banana Pro instead** when you need: higher fidelity, more complex reasoning, or the absolute best quality from the Gemini family
- **Use FLUX models instead** when you need: pure photorealism without text, or the fastest possible generation (FLUX Schnell)
