# Seedance 2.0

**Model ID:** `video/seedance-2.0`
**Fast variant:** `video/seedance-2.0-fast` (same quality, faster and cheaper)
**Image-to-Video:** Pass `image_url` parameter

ByteDance's most advanced video generation model. Cinematic output with native audio, real-world physics simulation, and director-level camera control. The Fast variant offers the same quality at reduced cost and generation time.

## Key Strengths

- **Native audio** -- generated audio with dialogue and SFX (enabled by default)
- **Real-world physics** -- accurate gravity, inertia, fluid dynamics, cloth/hair simulation
- **Director-level camera control** -- responds to cinematic camera language
- **Image-to-video** -- animate a reference image with strong consistency
- **Reference images** -- pass multiple `image_urls` via extras for style/character reference
- **Resolution control** -- 480p, 720p (default), or 1080p output

## Supports Image Input

Yes -- use `video/seedance-2.0` with `image_url` to animate from a reference image. The model preserves the visual details of the source image while adding motion according to the prompt.

For style or character consistency across clips, pass additional reference images via `image_urls` in extras.

## Prompting Strategy

### Scene Direction Style

Like Kling v3 Pro, Seedance responds best to cinematic scene direction rather than tag-based prompts. Describe motion, camera behavior, and physical interactions.

**Do this:**
> Slow dolly push-in on a barista pouring steamed milk into a ceramic latte cup. The milk swirls into a rosetta pattern, surface tension creating clean edges. Warm café lighting, shallow depth of field, anamorphic lens flare from the window behind.

**Not this:**
> barista making latte art, cinematic, 4k, masterpiece, beautiful

### Prompt Structure (Recommended Order)

1. **Camera movement** -- how the camera moves (dolly, tracking, crane, handheld)
2. **Subject and action** -- who/what with precise physical motion
3. **Physics details** -- material interactions, weight, momentum, fluid/cloth behavior
4. **Environment and lighting** -- setting, light sources, atmosphere
5. **Audio direction** -- dialogue, ambient sound, SFX

### Camera Movement Commands

| Command | Effect |
|---|---|
| Tracking shot | Camera follows subject laterally |
| Dolly push-in / pull-out | Camera moves toward or away from subject |
| Crane shot | Vertical sweeping movement |
| Handheld | Natural shake for documentary feel |
| Orbital / arc | Camera circles the subject |
| FPV drone | First-person aerial with rolls and whips |
| Macro close-up | Extreme close-up with shallow DOF |
| Low-angle | Ground-level dramatic perspective |
| Slow zoom | Gradual lens zoom for tension or reveal |

### Audio Direction

Audio is on by default (`generate_audio: true`). Include audio cues in your prompt:

> A chef slams a cleaver through a watermelon. The blade thuds through the rind with a satisfying crack. Seeds scatter across the wooden cutting board. Kitchen ambiance: sizzling pans in the background, extractor fan humming.

For dialogue, describe the speaker and their delivery:
> A tour guide gestures at the ancient ruins. "This temple was built over two thousand years ago," she says with quiet reverence. Wind whispers through the stone columns.

## Parameters

| Parameter | Type | Values | Default | Notes |
|---|---|---|---|---|
| **prompt** | string | -- | required | Cinematic scene direction |
| **image_url** | string | URL | -- | Source image for I2V mode |
| **resolution** | enum | 480p, 720p, 1080p | "720p" | Higher = slower and more expensive |
| **duration** | string | -- | "auto" | Video duration |
| **aspect_ratio** | string | -- | "auto" | Output aspect ratio |
| **generate_audio** | boolean | true/false | true | Native audio generation |
| **seed** | integer | -- | -- | For reproducibility |
| **image_urls** | array | URLs | -- | Reference images for style/character (via extras) |

## Example Prompts

### Product Video
> Slow orbital shot around a luxury watch on a polished marble surface. The camera glides at a slight downward angle. Light refracts through the sapphire crystal, casting prismatic highlights on the marble. The second hand ticks with precise mechanical movement. Soft ambient music, subtle ticking sound.

### Nature / Physics
> Aerial crane shot descending toward a mountain waterfall. The camera drops from above the treeline, pushing through mist into a close-up of water crashing against moss-covered rocks. Spray droplets catch sunlight, creating micro-rainbows. Sound of rushing water crescendos as the camera descends.

### Human Motion
> Handheld tracking shot following a street dancer in a concrete underpass. She spins on one foot, arms extending outward, jacket flaring with centrifugal force. Each foot placement echoes against the walls. Dust motes float in the shaft of light from above. Raw, gritty atmosphere. Sneakers squeak on concrete.

### Dialogue Scene
> Medium shot in a dimly lit jazz bar. A pianist plays softly in the background. A man in a leather jacket leans across the table and says, "I've been thinking about what you said last night." The woman across from him tilts her head, pauses, then replies: "And?" Glasses clink at the bar behind them.

## When to Use Seedance 2.0

- **Use Seedance 2.0** when you need: cinematic quality with native audio, physics-heavy motion (water, cloth, impacts), director-level camera control, or reference-image consistency
- **Use Seedance 2.0 Fast** when: you want the same quality for drafts or iteration at lower cost
- **Consider other models** when: you need multi-shot sequencing (Kling v3 Pro), clips longer than ~10s (Sora 2 Pro), first-last-frame transitions (Veo 3.1), or talking avatars (HeyGen)
