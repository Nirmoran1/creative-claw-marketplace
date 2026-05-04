# HeyGen Avatar 4

**Model ID:** `video/heygen-avatar-4`
**Budget alternative:** `video/heygen-agent` (text-only, ~$2/min vs $6/min)

HeyGen's Photo Avatar 4. Turn any photo of a person into a talking avatar with accurate lip-sync. 400+ poses, 100+ built-in voices. Ideal for presentations, explainers, marketing videos, and personalized messages.

## Key Strengths

- **Photo-to-talking-avatar** -- any clear face photo becomes a speaking video
- **Accurate lip-sync** -- mouth movements match speech naturally
- **400+ poses** -- built-in body positions and gestures
- **100+ voices** -- multilingual built-in voices, or bring your own audio
- **Custom audio lip-sync** -- pass `audio_url` to sync to your own voiceover
- **Captions** -- built-in caption generation
- **Resolution up to 1080p**

## Important: Requires image_url

This model only works in image-to-video mode. You must provide `image_url` with a photo containing a clear, front-facing face. The model does not support text-to-video generation.

## Parameters

| Parameter | Type | Values | Default | Notes |
|---|---|---|---|---|
| **image_url** | string | URL | required | Photo with a clear face |
| **prompt** | string | -- | -- | The text the avatar will speak |
| **voice** | string | -- | -- | Voice name to use (from 100+ built-in voices) |
| **audio_url** | string | URL | -- | Custom audio for lip-sync. Overrides prompt and voice |
| **talking_style** | enum | stable, expressive | "stable" | "expressive" adds more head/body animation |
| **expression** | string | -- | -- | Facial expression to maintain |
| **resolution** | enum | 360p-1080p | "720p" | Output resolution |
| **aspect_ratio** | enum | 16:9, 9:16, 1:1 | "16:9" | Video aspect ratio |
| **caption** | boolean | true/false | false | Add captions to the video |
| **background** | object | {type, value} | -- | Background configuration |

## Workflows

### Basic Talking Avatar
1. Generate or upload a portrait photo with `generate_image` or `upload_asset`
2. Call `generate_video` with `model: "video/heygen-avatar-4"`, `image_url`, and `prompt` (the speech text)
3. Optionally set `voice` and `talking_style`

### Custom Voice Lip-Sync
1. Generate speech audio with `generate_speech` (or upload your own audio)
2. Pass the audio URL as `audio_url` to Avatar 4
3. The avatar will lip-sync to your custom audio

### Presentation / Explainer
1. Generate a professional headshot or use the user's photo
2. Write the script as the `prompt`
3. Set `talking_style: "expressive"` for more engaging delivery
4. Enable `caption: true` for accessibility
5. Use `aspect_ratio: "16:9"` for landscape presentations or `"9:16"` for social/mobile

## Tips

- **Face quality matters** -- use a well-lit, front-facing photo with a clear face. Avoid profile shots or heavy occlusion.
- **Script length = video length** -- the video duration is determined by how long the text takes to speak
- **Expressive vs stable** -- use "stable" for professional/corporate content, "expressive" for casual or marketing content
- **Combine with other tools** -- generate the avatar video, then use `merge_media` to add background music or `edit_video` to add subtitles

## When to Use HeyGen Avatar 4

- **Use Avatar 4** when: you need a realistic talking head, product explainer, personalized message, or presentation video
- **Use HeyGen Agent instead** when: you want a budget option and don't need a custom photo (text-only, ~$2/min)
- **Consider other models** when: you need cinematic non-avatar video (Veo 3.1, Seedance 2.0), long-form narrative (Sora 2 Pro), or abstract/artistic content
