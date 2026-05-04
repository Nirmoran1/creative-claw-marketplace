# HyperFrames Primer

The minimum you need to know to write a composition that renders correctly via `render_html_video`. For the full workflow (asset gen, scene planning, anti-patterns), see `workflows/code-video-hyperframes.md`.

## What HyperFrames is

A browser-based video composition engine. You write **one HTML file** with CSS + GSAP, the server runs it in headless Chromium for `duration` seconds, captures every frame, and encodes to MP4. No build step, no React, no framework — just a page that knows how to animate itself.

## The capture contract

Three things must be true for the page to render correctly:

1. **A `window.__timelines` registration.** The capture engine reads this synchronously after page load to know what to play.
2. **All timelines start `{ paused: true }`.** The engine controls playback and seeks.
3. **Synchronous timeline construction.** No `async`, `setTimeout`, or `Promise` around the `gsap.timeline()` call.

Minimum working composition:

```html
<!doctype html>
<html>
<head>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
</head>
<body>
  <h1 id="title">Hello</h1>
  <script>
    window.__timelines = window.__timelines || {};
    const tl = gsap.timeline({ paused: true });
    tl.from("#title", { y: 60, opacity: 0, duration: 0.7, ease: "power3.out" }, 0.3);
    window.__timelines["root"] = tl;
  </script>
</body>
</html>
```

Duration comes from the `duration` parameter you pass to `render_html_video`, not from the GSAP timeline length. If your timeline is shorter than `duration`, the page holds the final state. If longer, it gets cut off.

## Layout before animation

Position every element at its **hero frame** (the moment when it's fully entered, correctly placed) using static CSS. Then write `gsap.from()` to animate INTO that position, and `gsap.to()` only for the final exit.

**Right:**
```css
.title { font-size: 120px; }   /* final state */
```
```js
tl.from(".title", { y: 60, opacity: 0, duration: 0.7 }, 0.3);  // journey to it
```

**Wrong:** positioning at the start state (`opacity: 0`, offscreen) and tweening to a guessed final position. You can't see overlaps until render.

For multi-scene comps: every scene's content has its own hero-frame CSS. Scene transitions handle the swap; never animate the previous scene's content `opacity: 0` before the transition fires.

## Hard rules (silent breakage if violated)

1. **Deterministic only.** No `Math.random()`, `Date.now()`, time-based logic. If you need randomness, seed it (mulberry32).
2. **No `repeat: -1`** on any timeline or tween. Calculate the exact count: `repeat: Math.ceil(duration / cycleDuration) - 1`.
3. **GSAP animates visual properties only** — `opacity`, `x`, `y`, `scale`, `rotation`, `color`, `backgroundColor`, `borderRadius`, `transform`. **Never** `visibility`, `display`, or media element `play()`/`pause()`.
4. **Never the same property on the same element from two timelines.** Conflicts produce undefined output.
5. **Synchronous timeline construction.** The engine reads `window.__timelines` synchronously after page load.
6. **Video must be `muted playsinline`.** Audio is always a separate `<audio>` element. The framework owns playback — never call `.play()`/`.pause()`/`.currentTime`.
7. **No `<br>` in body text** that wraps naturally — produces unwanted breaks. Use `max-width` for natural wrapping. Exception: short display titles where each word is deliberately on its own line.
8. **Animate a wrapper div, not the video element itself** — animating `<video>` dimensions causes flicker.

## Scene transitions

For multi-scene compositions:

1. **Always use entrance animations** on every scene. Every element animates IN via `gsap.from()`. No element appears fully formed.
2. **Never use exit animations** except on the final scene. The transition IS the exit. The outgoing scene's content must be fully visible at the moment the transition starts.
3. **Always use a transition between scenes.** No jump cuts.

Worked example:
```js
// Scene 1 entrance — all elements animate IN
tl.from("#s1-title", { y: 50, opacity: 0, duration: 0.7, ease: "power3.out" }, 0.3);
tl.from("#s1-subtitle", { y: 30, opacity: 0, duration: 0.5, ease: "power2.out" }, 0.6);

// NO exit tweens — transition handles the swap
// Scene 2 entrance
tl.from("#s2-heading", { x: -40, opacity: 0, duration: 0.6, ease: "expo.out" }, 8.0);
```

## Animation guardrails

- Offset the first animation 0.1–0.3s — never `t=0`, looks robotic.
- Vary easing across entrance tweens — at least 3 different eases per scene.
- Don't repeat an entrance pattern within a scene.
- Avoid full-screen linear gradients on dark backgrounds (H.264 banding) — use radial or solid + localized glow.
- 60px+ headlines, 20px+ body, 16px+ data labels for video legibility.
- `font-variant-numeric: tabular-nums` on number columns.

## Fonts and assets

- Any web font works: `<link>` tag, `@import`, `@font-face`. Google Fonts and Bunny Fonts CDNs are fine.
- All Google Font weights and italic variants are loaded automatically when you reference the family — use `font-weight: 900` and `font-style: italic` freely.
- External media: add `crossorigin="anonymous"` to `<img>` and `<video>` tags pulling from CDNs.
- Inter is loaded by default as a fallback.

## Tailwind

Tailwind CSS works out of the box — no build step, no setup. Use utility classes anywhere.

## Common mistakes that break renders

- Forgetting `window.__timelines["root"] = tl` — page renders, no animation runs.
- Using `repeat: -1` for an "ambient" loop — capture engine hangs.
- Building the timeline inside `document.fonts.ready.then(...)` or `setTimeout` — timeline doesn't exist when capture starts.
- `<video src="...">` without `muted playsinline` — Chromium blocks autoplay.
- Animating `display: none` → `display: block` — GSAP can't tween display.
- Using `gsap.set()` on a future-scene element at page load — element may not exist yet. Use `tl.set(selector, vars, time)` inside the timeline at the right moment.

## What to read next

- For the full code-video workflow: `workflows/code-video-hyperframes.md`
- For dimensions and platform safe zones: `platform-dimensions.md`
- For polling the async render job: `async-jobs.md`
