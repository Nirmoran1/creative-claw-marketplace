---
name: creativeclaw
description: Creative Claw AI media studio — generate images, videos, speech, branded graphics, and manage brand themes. Routes your request to the right MCP workflow and loads model-specific guides on demand. Requires the Creative Claw MCP server to be connected.
tags:
  - image
  - video
  - banner
  - reel
  - brand
  - theme
  - html
  - media
  - creative
arguments: []
---

# Creative Claw

AI media studio running via MCP. Generate images, videos, speech, branded HTML graphics, and manage brand themes — all through one server connected to 1,000+ AI models.

## Prerequisite

This skill requires the **Creative Claw MCP server** to be connected. If tools like `generate_image`, `generate_video`, `render_html_image` are not available, the user needs to connect first:

```
/plugin install creative-claw@creative-claw-marketplace
```

Or connect the MCP directly: `https://app.creativeclaw.co/mcp`

## How to Use the MCP Server's Knowledge

The Creative Claw MCP server ships its own **prompts** (full workflow guides) and **resources** (per-model prompting guides). You MUST load these into context before doing any generation work. They contain the detailed workflows, model selection, prompting strategies, and anti-patterns — do not guess or improvise.

### Step 1: Load the right MCP prompt

MCP prompts are the workflow guides. When the user asks to do something, **invoke the matching MCP prompt** to load the full workflow into context. The server name is `Creative Claw`.

| User wants to... | MCP Prompt to invoke |
|---|---|
| Generate or edit an image | `create-image` |
| Generate a video clip | `create-video` |
| Render a branded graphic from HTML/CSS | `create-html-image` |
| Create or manage a brand theme | `create-brand-theme` |
| Build a programmatic video with Remotion | `create-video-remotion` |
| Get oriented / "what can I do?" / onboard me | `onboard` |

### Step 2: Load the model-specific guide

Before crafting any generation prompt, read the model's prompting guide using `ReadMcpResourceTool` with server `Creative Claw`. These guides contain the exact prompt structure, keywords, and pitfalls for each model.

**Discover all available guides:**
```
ListMcpResourcesTool(server: "Creative Claw")
```

**Read a specific guide:**
```
ReadMcpResourceTool(server: "Creative Claw", uri: "creative-claw://guides/video/seedance-2.0")
```

Known guides at time of writing:

**Image models:**
- `creative-claw://guides/image/flux-2-pro`
- `creative-claw://guides/image/flux-schnell`
- `creative-claw://guides/image/gpt-image-1.5`
- `creative-claw://guides/image/nano-banana-2`
- `creative-claw://guides/image/nano-banana-pro`
- `creative-claw://guides/image/recraft-v3`

**Video models:**
- `creative-claw://guides/video/hailuo-02-pro`
- `creative-claw://guides/video/hailuo-2.3-fast`
- `creative-claw://guides/video/heygen-avatar-4`
- `creative-claw://guides/video/kling-v3-pro`
- `creative-claw://guides/video/seedance-2.0`
- `creative-claw://guides/video/sora-2-pro`
- `creative-claw://guides/video/veo-3.1`

New guides may be added to the server — always run `ListMcpResourcesTool` to discover the latest.

### Step 3: Check the brand theme

If the user has a brand, call `get_theme` before any generation. The theme contains colors, fonts, logos, and style tokens that should inform every prompt and render.

## Use-Case Routing

### "Make me a banner / social card / OG image"
1. Invoke MCP prompt: `create-html-image` (for layout-driven) or `create-image` (for photorealistic)
2. Load brand theme with `get_theme`
3. Platform dimensions:

| Platform | Size | Notes |
|---|---|---|
| Instagram Post | 1080x1080 | Center-weighted |
| Instagram Story | 1080x1920 | 150px safe zone top/bottom |
| LinkedIn Post | 1200x627 | |
| LinkedIn Banner | 1584x396 | No text in outer 10% |
| Twitter/X Post | 1600x900 | |
| YouTube Thumbnail | 1280x720 | Bold text, high contrast |
| Facebook Cover | 1200x630 | |
| OG Image | 1200x630 | |
| Email Header | 600x200 | |

**When to use which tool:**
- Typography, quotes, stats, announcements, badges → `render_html_image`
- Photorealistic scenes, artistic imagery → `generate_image`
- AI background + branded text overlay → `generate_image` first, then `render_html_image` with it via `inline_images`

### "Make me a TikTok / Reel / Short"
1. Invoke MCP prompt: `create-video`
2. Read the model guide for the chosen video model
3. Platform specs:

| Platform | Aspect | Optimal duration | Notes |
|---|---|---|---|
| TikTok | 9:16 | 15-60s | Hook in first 1-3s |
| Instagram Reels | 9:16 | 15-30s | 250px safe zone at bottom |
| YouTube Shorts | 9:16 | 15-60s | Title overlay at bottom |

**Reel structure:** Hook (0-3s) → Body (2-4 segments, 3-20s) → CTA (last 2-3s)

**Formats:** Product showcase, before/after, tutorial, testimonial, montage.

**Workflow:** Plan segments → generate reference image per segment → generate video clips → `add_subtitles` → `generate_speech` or upload audio → `merge_media`.

### "Make assets for my landing page"
1. Invoke MCP prompts: `create-image` AND `create-html-image` (you'll use both)
2. Load brand theme
3. Asset checklist:

| Asset | Tool | Size |
|---|---|---|
| Hero image | `generate_image` | 1920x1080 |
| Hero + text overlay | `generate_image` → `render_html_image` | 1920x1080 |
| OG / social share | `render_html_image` | 1200x630 |
| Feature illustrations | `generate_image` (same model for consistency) | 800x800 |
| Section backgrounds | `generate_image` | 1920x1080 |
| Product shots (cutout) | `remove_background` | varies |
| Testimonial cards | `render_html_image` | 600x400 |
| Favicon | `generate_image` | 512x512 |

**Style consistency:** Use ONE model for all illustrations. Same style prefix in every prompt. Pass a reference image via `image_url` to maintain consistency across a set.

### "Set up my brand / create a theme"
1. Invoke MCP prompt: `create-brand-theme`
2. Follow the workflow in the prompt — it covers website extraction, local folders, URL lists, and generating from scratch

### "Build a motion video / animated video with Remotion"
1. Invoke MCP prompt: `create-video-remotion`
2. Generate assets with `generate_image`, `render_html_image`, `generate_speech`
3. Follow the Remotion workflow in the prompt

### "Make me an image / edit this image"
1. Invoke MCP prompt: `create-image`
2. Read the guide for the chosen model
3. Follow the workflow in the prompt

### "Make me a video"
1. Invoke MCP prompt: `create-video`
2. Read the guide for the chosen model
3. Follow the workflow in the prompt — always generate a reference image first

### "What can Creative Claw do?" / "Onboard me"
1. Invoke MCP prompt: `onboard`
2. Follow the onboarding conversation flow

## Key Tools Quick Reference

**Generate:** `generate_image`, `generate_video`, `generate_speech`, `render_html_image`, `compare_models`
**Edit:** `remove_background`, `upscale_media`, `trim_video`, `scale_video`, `add_subtitles`, `extract_frames`, `merge_media`
**Brand:** `get_theme`, `update_theme`, `list_themes`
**Templates:** `create_template`, `render_template`, `list_templates`
**Assets:** `search_assets`, `upload_asset`, `import_media`, `update_asset`
**Jobs:** `check_job` (poll async jobs until complete)
**Credits:** `get_credits_balance`, `get_credits_link`
**View:** `load_image` (display an image inline)

## Important Patterns

- **Load the MCP prompt first.** The prompts contain the real workflow knowledge. This skill just routes you there.
- **Read the model guide before prompting.** Every model has different prompt structure and keywords.
- **Discover resources dynamically.** Run `ListMcpResourcesTool(server: "Creative Claw")` — new guides are added regularly.
- **Always generate a reference image before video.** The `create-video` prompt explains why.
- **Always use `inline_images` in `render_html_image`.** Never raw external URLs in `<img>` tags.
- **Always check brand theme first** if the user has a brand.
- **Video generation is async.** `generate_video` returns a job ID → poll with `check_job`.
- **Name and tag assets** with `update_asset` after generation — makes them searchable later.
