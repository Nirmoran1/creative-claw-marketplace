# Platform Dimensions and Safe Zones

When the user names a platform without giving dimensions, use these. Machine-readable copy: `assets/platform-dimensions.json`.

## Static (image / banner)

| Use case | Dimensions | Aspect | Notes |
|---|---|---|---|
| **Open Graph** (default for `render_html_image`) | 1200×630 | 1.91:1 | Facebook, Twitter, LinkedIn link previews |
| **Open Graph (Medium / Substack)** | 1500×750 | 2:1 | |
| **LinkedIn post (square)** | 1200×1200 | 1:1 | Most versatile for feed |
| **LinkedIn post (social square)** | 1080×1080 | 1:1 | Matches IG sizing |
| **LinkedIn cover / hero** | 1584×396 | 4:1 | Profile header. No text in outer 10%. |
| **Twitter / X post** | 1600×900 | 16:9 | |
| **Instagram feed (square)** | 1080×1080 | 1:1 | Center-weighted composition |
| **Instagram story / TikTok cover** | 1080×1920 | 9:16 | 150px safe zone top + bottom |
| **YouTube thumbnail** | 1280×720 | 16:9 | Bold text, high contrast — competes in a grid |
| **Facebook cover** | 1200×630 | 1.91:1 | |
| **Hero / website banner** | 1920×1080 | 16:9 | |
| **Email header** | 600×200 | 3:1 | Wide aspect, tiny vertical real estate |
| **Favicon** | 512×512 | 1:1 | Square, simple at small sizes |
| **App icon** | 1024×1024 | 1:1 | iOS/Android base size |

## Video / motion

| Use case | Dimensions | Aspect | Optimal duration | Notes |
|---|---|---|---|---|
| **TikTok** | 1080×1920 | 9:16 | 15–60 s | Hook in first 1–3 s |
| **Instagram Reels** | 1080×1920 | 9:16 | 15–30 s | 250 px safe zone at bottom (UI overlay) |
| **YouTube Shorts** | 1080×1920 | 9:16 | 15–60 s | Title overlay at bottom |
| **YouTube standard** | 1920×1080 | 16:9 | varies | |
| **YouTube cinematic** | 1920×1080 (24 fps) | 16:9 | varies | 24 fps for filmic feel |
| **Square social video** | 1080×1080 | 1:1 | 15–60 s | IG, LinkedIn |
| **4K cinematic** | 3840×2160 | 16:9 | varies | 24 fps usually |

## Reel / Short structure

For short-form vertical video:

- **Hook** (0–3 s): the moment that earns the rest of the video. Visual + verbal. No logo intros.
- **Body** (2–4 segments, 3–20 s each): the substance.
- **CTA** (last 2–3 s): the ask.

Common formats: product showcase, before/after, tutorial, testimonial, montage.

## Safe zones

- **Instagram Story / TikTok**: top 150 px and bottom 250 px are likely covered by username, captions, and like/share UI. Keep critical content in the central 1080×1520 area.
- **YouTube Shorts**: bottom 200 px overlap with title and channel UI.
- **LinkedIn cover**: avatar circle covers the lower-left ~250 px. Text in outer 10% gets cropped on mobile.
- **YouTube thumbnail**: lower-right gets covered by duration badge. Lower-left covered by progress bar on hover.

## Frame rates

- **24 fps** — cinematic, filmic motion blur expectation, slowest render
- **30 fps** — standard for social, screen content
- **60 fps** — smooth motion (sports, gaming, fast UI), doubles render time vs 30

When in doubt, use 30 fps.
