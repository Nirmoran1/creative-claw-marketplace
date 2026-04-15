# Creative Claw

**Generate on-brand media, inside Claude.**

Creative Claw is an MCP plugin that brings a full AI media studio into Claude Code and Claude Desktop. Generate on-brand images, videos, speech, and HTML-rendered branded graphics — all from natural language, all through one account. Save your brand once and every future visual stays on-brand automatically. No API keys. No platform switching. Just describe what you need.

> [creativeclaw.co](https://creativeclaw.co) | [Join the Beta](https://creativeclaw.co)

---

## What You Get

### MCP Server (auto-connected)

One connection to Creative Claw's MCP server gives you 30+ tools for media generation, editing, layout rendering, branding, and asset management:

| Category          | Tools                                                                                                               |
| ----------------- | ------------------------------------------------------------------------------------------------------------------- |
| **Image**         | `generate_image` (generate + edit), `compare_models`, `load_image`                                                  |
| **Video**         | `generate_video`, `check_job`                                                                                       |
| **Speech**        | `generate_speech`                                                                                                   |
| **HTML → media**  | `render_html_image`, `render_template`                                                                              |
| **Media editing** | `remove_background`, `upscale_media`, `trim_video`, `scale_video`, `add_subtitles`, `extract_frames`, `merge_media` |
| **Models**        | `list_models`, `get_model_params`                                                                                   |
| **Assets**        | `search_assets`, `update_asset`, `delete_asset`, `upload_asset`, `import_media`, `get_upload_url`, `confirm_upload` |
| **Brand themes**  | `get_theme`, `list_themes`, `update_theme`, `delete_theme`                                                          |
| **Templates**     | `create_template`, `update_template`, `list_templates`, `render_template`                                           |
| **Credits**       | `get_credits_balance`, `get_credits_link`                                                                           |

Access 1,000+ production-ready AI models — FLUX, Gemini, Veo, Sora, Kling, Seedance, Hailuo, HeyGen, Recraft, ElevenLabs, and more — through a single unified account with usage-based pricing.

### Skills (Creative Workflows)

Skills are prompt-based workflows that teach Claude _how_ to use the tools effectively — model selection, prompt engineering, multi-step production pipelines, and brand-aware rendering.

| Skill                     | What It Does                                                                                                                                                                                                                            |
| ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **creative-claw-onboard** | First-time orientation. Explains the mission, tours the studio's capabilities, and walks new users through their first generation — images, videos, HTML renders, or voice.                                                             |
| **create-image**          | Helps you pick the right model, craft effective prompts, and generate or edit images. Covers the full roster of recommended models with detailed reference guides.                                                                      |
| **create-video**          | Guides you through model selection, reference image generation, camera direction, multi-segment video production, and talking avatars. Covers recommended video models with detailed reference guides.                                  |
| **create-html-image**     | Render on-brand images from HTML/CSS via headless Chromium — quote cards, OG images, social banners, stat cards, hero layouts. Full browser CSS surface (grid, flex, filter, clip-path, variable fonts, inline SVG). Pulls from themes. |
| **create-brand-theme**    | Create, extract, update, and apply brand themes. Onboards a new brand from a website, local folder, or direct URLs — saves colors, fonts, logos, shapes, and photography style as a reusable theme.                                     |

Each generation skill includes per-model reference files with prompting best practices, parameter tables, example prompts, and comparison guidance.

---

## Supported Models

### Image Generation

| Model            | ID                                | Highlights                                                  |
| ---------------- | --------------------------------- | ----------------------------------------------------------- |
| GPT Image 1.5    | `fal-ai/gpt-image-1.5`            | Production-quality, strong prompt adherence, fine detail    |
| Gemini 3 Pro     | `fal-ai/nano-banana-pro`          | Complex reasoning, semantic understanding, text in images   |
| Gemini 3.1 Flash | `fal-ai/nano-banana-2`            | Fast, high-fidelity, excellent text rendering, multilingual |
| FLUX.2 Pro       | `fal-ai/flux-2-pro`               | Zero-config professional quality, HEX color precision       |
| Recraft V3       | `fal-ai/recraft/v3/text-to-image` | #1 on benchmarks, design and illustration                   |
| FLUX Schnell     | `fal-ai/flux/schnell`             | Fastest (~0.5s), cheapest, great for drafts                 |

### Image Editing

| Model            | ID                            | Highlights                                      |
| ---------------- | ----------------------------- | ----------------------------------------------- |
| GPT Image 1.5    | `fal-ai/gpt-image-1.5/edit`   | Strong prompt adherence, identity preservation  |
| Gemini 3 Pro     | `fal-ai/nano-banana-pro/edit` | Semantic edit instructions, 14 reference images |
| FLUX Kontext Max | `fal-ai/flux-pro/kontext/max` | Typography, consistency, precise edits          |
| Gemini 3.1 Flash | `fal-ai/nano-banana-2/edit`   | Fast, no masking required                       |

### Video Generation

| Model             | ID                                                       | Audio                   | Image Input                  |
| ----------------- | -------------------------------------------------------- | ----------------------- | ---------------------------- |
| Veo 3.1           | `fal-ai/veo3.1`                                          | Native dialogue + SFX   | Yes (`/image-to-video`)      |
| Veo 3.1 Fast      | `fal-ai/veo3.1/fast`                                     | Native dialogue + SFX   | Yes (`/fast/image-to-video`) |
| Sora 2 Pro        | `fal-ai/sora-2/text-to-video/pro`                        | Native audio            | Yes (`/image-to-video/pro`)  |
| Kling v3 Pro      | `fal-ai/kling-video/v3/pro/text-to-video`                | Native audio + lip-sync | Yes (`/image-to-video`)      |
| Seedance 2.0      | `fal-ai/bytedance/seedance-2.0/text-to-video`            | Native audio            | Yes (`/image-to-video`)      |
| Seedance 2.0 Fast | `fal-ai/bytedance/seedance-2.0/fast/text-to-video`       | Native audio            | Yes (`/image-to-video`)      |
| Hailuo-02 Pro     | `fal-ai/minimax/hailuo-02/pro/text-to-video`             | Yes                     | Yes (`/image-to-video`)      |
| Hailuo 2.3 Fast   | `fal-ai/minimax/hailuo-2.3-fast/standard/image-to-video` | No                      | Yes (I2V only)               |

### Talking Avatars

| Model              | ID                                     | Highlights                                                    |
| ------------------ | -------------------------------------- | ------------------------------------------------------------- |
| HeyGen Avatar 4    | `fal-ai/heygen/avatar4/image-to-video` | Photo → talking avatar with lip-sync, 400+ poses, 100+ voices |
| HeyGen Video Agent | `fal-ai/heygen/v2/video-agent`         | Budget talking avatar from text (~$2/min)                     |

These are our top picks. Use `list_models` to browse 100+ more across all categories.

---

## Install

### Claude Code

```bash
# 1. Add the marketplace
claude plugin marketplace add CreativeClawCo/creative-claw-marketplace

# 2. Install the plugin
claude plugin install creative-claw@creative-claw-marketplace

# 3. Authenticate — on first use, the MCP server will prompt you to sign in via Clerk OAuth
```

That's it. The plugin connects to Creative Claw's MCP server and gives you access to all generation tools plus the `/creative-claw-onboard`, `/create-image`, `/create-video`, `/create-html-image`, and `/create-brand-theme` skills.

### Claude Desktop

Add to your MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "creative-claw": {
      "type": "http",
      "url": "https://app.creativeclaw.co/mcp"
    }
  }
}
```

No API keys needed — auth is handled via Clerk OAuth on first connection.

---

## Quick Start

Just talk to Claude naturally:

```
"Generate a product photo of my headphones on a marble surface, golden hour lighting"
  -> /create-image picks the best model, crafts the prompt, generates

"Make a 15-second cinematic video of coffee being poured in slow motion"
  -> /create-video recommends the right model for physics, generates a reference image, then the video

"Edit this image — change the background to a beach sunset, keep the person unchanged"
  -> /create-image routes to an edit model, preserves identity, swaps background

"Make me a LinkedIn quote card with our brand colors"
  -> /create-html-image writes the HTML, pulls colors/fonts/logo from the saved brand theme, renders via headless Chromium

"Set up our brand — here's our website"
  -> /create-brand-theme extracts colors/fonts/logos from the site, uploads the assets, saves as a reusable theme

"I need a TikTok-style product video for this shoe" [attach image]
  -> /create-video generates reference frames, picks an I2V model, produces the clip
```

---

## Architecture

```
You -> Claude + Skills (model selection, prompt engineering, creative direction, brand-aware rendering)
              |
         MCP Tools (generate_image, generate_video, render_html_image, update_theme, ...)
              |
       Creative Claw Server (fal.ai + headless Chromium + R2 storage + Clerk auth)
              |
       Permanent media URLs (never expire)
```

**No API keys.** No CLI wrappers. No expiring URLs. Just skills + MCP.

---

## Project Structure

This repo is a **marketplace** — it contains one or more installable plugins.

```
.claude-plugin/
  marketplace.json         # Marketplace manifest (required for Claude Code marketplace sync)
  plugin.json              # Root plugin metadata
plugins/
  creative-claw/
    .claude-plugin/
      plugin.json          # Plugin manifest (MCP server config)
    openclaw.plugin.json   # OpenClaw compatibility
    skills/
      creative-claw-onboard/
        SKILL.md           # /creative-claw-onboard — first-time orientation + studio tour
      image-generation/
        SKILL.md           # /create-image — image generation & editing workflow
        references/        # Per-model prompting guides
      video-generation/
        SKILL.md           # /create-video — video generation workflow
        references/        # Per-model prompting guides
      create-html-image/
        SKILL.md           # /create-html-image — HTML → PNG via headless Chromium
      create-brand-theme/
        SKILL.md           # /create-brand-theme — create, extract, update, and apply brand themes
```

---

## Pricing

Usage-based — pay only for what you generate. No subscriptions, no commitments. Check [creativeclaw.co](https://creativeclaw.co) for current rates.

---

## Compatibility

- **Claude Code** — via `.claude-plugin/plugin.json`
- **Claude Desktop** — via MCP server config
- **OpenClaw** — via `openclaw.plugin.json`

All use the same skills and connect to the same MCP server.

---

## License

Apache-2.0

---

Built by [Creative Claw Co.](https://creativeclaw.co)
