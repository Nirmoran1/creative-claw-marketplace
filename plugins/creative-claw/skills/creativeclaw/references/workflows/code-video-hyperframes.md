# Code-Driven Video with HyperFrames + Creative Claw

You are a video production specialist building **code-driven, deterministic video** by writing an HTML/CSS/JS composition and rendering it via the `render_html_video` MCP tool. The render runs HyperFrames + headless Chromium on Modal and returns a permanent MP4 URL.

## When to use this workflow

- Kinetic typography, branded title cards, animated stat cards, lower thirds, end screens
- Branded content series — one composition, swap data per episode
- Animated infographics and data visualizations
- Animated logo reveals, countdowns, audio-reactive visuals
- Anything that should be deterministic, on-brand, and frame-accurate

If the user wants **photoreal motion** (people, scenes, products in space), use `workflows/video-gen.md` with an AI model instead. If the user wants a **static branded image**, use `workflows/html-image.md`.

## The core idea

**Creative Claw generates the assets. HyperFrames composes them as HTML/CSS/JS, runs the page in headless Chromium for `duration` seconds, and captures it as MP4.**

- Creative Claw → permanent URLs for images, video clips, speech, branded PNGs
- Reference those URLs directly in the HTML composition (`<img src=...>`, `<video src=...>`, `<audio src=...>`)
- HyperFrames + GSAP timeline drives motion
- `render_html_video` returns a job ID → poll with `check_job` → MP4 URL

## Workflow

### Step 1 — Pull the brand theme

`get_theme` first. Colors, fonts, logos, shapes, photography style — everything below should pull from these tokens. If no theme exists and the user wants on-brand output, hand off to the brand-theme workflow before continuing.

### Step 2 — Plan the composition

Before writing HTML, decide:

1. **Storyboard** — break the video into scenes. Each scene is a CSS-styled section with its own GSAP timeline segment.
2. **Dimensions** — lock in early. Common: `1920×1080` (landscape), `1080×1920` (vertical/Reels/TikTok), `1080×1080` (square).
3. **Duration + fps** — HyperFrames captures the page for `duration` seconds. 24 (cinematic), 30 (standard), 60 (smooth, doubles render time).
4. **Asset list** — what AI assets need to be generated first? Hero images, background clips, voiceover, branded title cards (rendered separately via `render_html_image`).

### Step 3 — Generate assets with Creative Claw

Generate everything you'll reference in the composition. Every result is a permanent URL.

**Branded title cards / lower thirds / stat cards** → `render_html_image` (deterministic, pulls from theme).
**Photoreal hero images / backgrounds** → `generate_image` (always with theme reference image via `image_url`).
**Cinematic clips** → `generate_video` → poll `check_job`.
**Voiceover** → `generate_speech`.
**Cutout product shots** → `generate_image` then `remove_background`.

Tag everything: `tags: ["<project>", "scene-N", "<role>"]`.

### Step 4 — Write the HTML composition

A HyperFrames composition is **one HTML file** with three layers:

1. **Markup** — semantic HTML for every visible element, positioned at its hero-frame location with CSS.
2. **Style** — full CSS surface. Tailwind utility classes are available out of the box.
3. **Timeline** — GSAP timeline that drives entrances, motion, and scene changes. Register on `window.__timelines["root"]`.

```html
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    /* full browser CSS — flex, grid, filter, mask, transforms, variable fonts */
    body { margin: 0; background: #0a0a0a; color: #fff; font-family: 'Inter', sans-serif; }
    .scene { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; opacity: 0; }
    .title { font-size: 120px; font-weight: 900; letter-spacing: -0.04em; }
  </style>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
</head>
<body>
  <div class="scene" id="s1"><h1 class="title">Hello</h1></div>
  <div class="scene" id="s2"><img src="https://cdn.creativeclaw.co/u/.../hero.png" style="width:100%"></div>

  <script>
    window.__timelines = window.__timelines || {};
    const tl = gsap.timeline({ paused: true });

    // Scene 1: 0–3s
    tl.to("#s1", { opacity: 1, duration: 0.4, ease: "power2.out" }, 0.2);
    tl.from("#s1 .title", { y: 60, opacity: 0, duration: 0.7, ease: "power3.out" }, 0.3);
    // Scene 2 transition: 3–3.5s crossfade
    tl.to("#s1", { opacity: 0, duration: 0.5 }, 3);
    tl.to("#s2", { opacity: 1, duration: 0.5 }, 3);

    window.__timelines["root"] = tl;
  </script>
</body>
</html>
```

**Read `references/hyperframes-primer.md` before writing any composition** — it covers the timeline contract, the never-do list, layout-before-animation, scene transition rules, and font handling.

### Step 5 — Render

```
render_html_video({
  html: "<full HTML string>",
  duration: 8,
  fps: 30,
  width: 1920,
  height: 1080,
  format: "mp4",
  name: "product-demo-v1",
  tags: ["product-demo", "hero"]
})
```

Returns `{ jobId, status: "queued" }`. Poll with `check_job(jobId)` until `status === "completed"`. Typical render: 30–120 s depending on duration and fps.

### Step 6 — Iterate

Edit the HTML, re-render. Renders are deterministic — same HTML → same MP4. Use `render_html_image` to spot-check a specific frame at a fraction of the time/cost.

## Common patterns

### Branded content series

One composition template, swap data per episode:

1. Create a brand theme.
2. Generate per-episode assets with Creative Claw (hero images, voiceover, stat cards).
3. Write a parameterized composition. Inject episode data via JS literals or a `<script type="application/json">` block.
4. Loop: for each episode, build the HTML string with the episode's URLs/text, call `render_html_video`.

### AI clip + brand chrome overlay

1. `generate_video` → cinematic background clip.
2. `render_html_image` → transparent PNG overlays (logo, lower third, end card).
3. In the composition: `<video>` for the clip with `muted playsinline`, `<audio>` separately for sound, branded `<img>` overlays positioned absolute, animated in/out via GSAP.

### Data visualization video

1. `render_html_image` or `generate_image` → branded background.
2. Build the chart inline with CSS + a counting GSAP tween (`gsap.to({ val: 0 }, { val: 100, duration: 2, onUpdate: … })`).
3. `generate_speech` → narration. Reference as `<audio>` in the composition.

### Talking avatar + branded wrapper

1. `generate_video` with a HeyGen avatar → talking head clip.
2. `render_html_image` → branded frame, lower third with name/title.
3. Composition: avatar `<video>` in a shaped container (border-radius, mask), brand `<img>` elements around it.

### Product demo with voiceover

1. `generate_image` + `remove_background` → clean product cutouts from multiple angles.
2. `generate_speech` → voiceover. Note its duration.
3. Composition timeline: animate product images (zoom, rotate, pan), GSAP synced to voiceover beats.

## Asset management

- **Tag everything** at generation time: `tags: ["<project>", "<scene>", "<role>"]` so `search_assets` finds them later.
- **Name meaningfully** — `name: "product-demo-hero-shot"`, not `name: "image-1"`.
- **Keep a constants block** at the top of your composition with all asset URLs — easy to swap.
- **Generate at composition resolution.** If the comp is 1920×1080, generate the hero at 1920×1080 — `upscale_media` is a fallback, not a plan.

## MCP tools used here

**Generation** — `generate_image`, `generate_video`, `generate_speech`, `render_html_image`, `render_html_video`, `render_template`
**Editing** — `remove_background`, `upscale_media`, `trim_video`, `merge_media`
**Assets** — `search_assets`, `update_asset`, `upload_asset`
**Brand** — `get_theme`, `list_themes`
**Jobs** — `check_job` (always required after `render_html_video` and `generate_video`)

## Anti-patterns

- **Don't skip the brand theme** — every composition that ships should pull tokens from a theme.
- **Don't use `repeat: -1`** on any timeline or tween — breaks the capture engine. Calculate the exact repeat count.
- **Don't build timelines asynchronously** (inside `async`, `setTimeout`, `Promise`). The capture engine reads `window.__timelines` synchronously after page load.
- **Don't animate `display`, `visibility`, or call `play()`/`pause()` on media elements** — the framework owns playback.
- **Don't render at 60fps unless the motion needs it** — doubles render time.
- **Don't generate the entire video with AI models** when the goal is deterministic branded output. Use AI for cinematic clips; use HyperFrames for everything that needs to be repeatable.
