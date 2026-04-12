# Seedance 2.0

**Model ID:** `video/seedance-2.0`
**Fast variant:** `video/seedance-2.0-fast` (same quality, faster and cheaper — use for drafts)
**Image-to-Video:** Pass `image_url` parameter

ByteDance's most advanced video generation model. Cinematic output with native audio, real-world physics simulation, and director-level camera control. Multi-modal: accepts text, up to 9 reference images, 3 reference videos, and 3 audio tracks in a single generation.

## Key Strengths

- **Native audio** — dialogue, SFX, and ambient sound generated in-model (on by default)
- **Real-world physics** — gravity, inertia, fluid dynamics, cloth/hair simulation
- **Director-level camera control** — responds to cinematic shot language
- **Image-to-video** — animate a reference image with strong subject consistency
- **Multi-reference** — lock character/style/motion/audio via `@1`, `@2`, `@3` syntax
- **Resolution control** — 480p, 720p (default), or 1080p

## Supports Image Input

Yes — use `video/seedance-2.0` with `image_url` to animate from a reference image. For image-to-video, describe **motion changes only** and append `preserve composition and colors` so the model doesn't drift from the source frame.

For style or character consistency across clips, pass additional reference images via `image_urls` in extras (maps to the `@1`..`@9` slots).

## Prompting Strategy

### The 6-Step Formula (Official)

Seedance 2.0's official guide recommends this ordering. Target length: **60–100 words**.

> `[Subject], [Action], in [Environment], camera [Camera Movement], style [Style], avoid [Constraints]`

1. **Subject** — concrete visual description (age, clothing, distinguishing features). Not "a businesswoman" — instead "a woman in her early 30s, navy blazer, dark hair in a loose bun, serious expression."
2. **Action** — specific verbs, not adjectives. "Pours", "spins", "slams", not "amazing" or "dynamic."
3. **Environment** — location **plus** lighting source and quality.
4. **Camera** — **one** primary movement (see table below). Multiple conflicting movements cause jitter.
5. **Style** — film references, color palette, era. E.g. `35mm film grain, Kodak color palette, anamorphic lens flare`.
6. **Constraints** — negative cues. E.g. `avoid jitter, avoid bent limbs, avoid identity drift`.

**Do this:**
> Slow dolly push forward. A woman in a red coat walks through a misty autumn forest, leaves tumbling around her. Golden diffused morning light filters through bare branches. Cinematic color grade, 35mm film grain, shallow depth of field. Avoid jitter and bent limbs.

**Not this:**
> beautiful woman walking in forest, cinematic, 4k, amazing, masterpiece

### The 8 Camera Movements

Pick **exactly one** primary movement. This is the single highest-impact element you can add.

| Movement | Effect | Best use |
|---|---|---|
| **Push-in** | Camera moves toward subject | Emotional focus, reveal |
| **Pull-out** | Camera moves away | Environmental reveal |
| **Pan** | Horizontal sweep from fixed position | Scanning a scene |
| **Tracking** | Follows subject laterally | Action, walking, running |
| **Orbit** | Camera circles the subject | Product, character portraits |
| **Aerial / crane** | Bird's-eye or vertical sweep | Landscapes, scale |
| **Handheld** | Subtle natural shake | Documentary, realism |
| **Fixed** | Completely still | Let subject action dominate |

**Rhythmic modifiers:** use `slow`, `smooth`, `gentle`, `subtle` — not f-stops, ISO, or other technical jargon.

### Lighting Is The Secret Weapon

Lighting descriptions are the most **underused** high-impact element. Always specify source, quality, and optionally a color temperature directive.

| Lighting | Keywords |
|---|---|
| Golden hour | `warm golden hour sunlight`, `rim light through leaves` |
| Overcast | `soft diffused cloud light, no harsh shadows` |
| Blue hour | `blue twilight, cool tones` |
| Studio | `clean studio lighting, softbox from the left` |
| Dramatic | `hard chiaroscuro, deep shadows, single key light` |
| Neon / urban | `neon reflections on wet pavement, cyan and magenta` |

Pro tip: add `color temperature: warm` or `color temperature: cool` as an explicit directive — Seedance follows it reliably.

### Audio Direction

Audio is on by default (`generate_audio: true`). Audio cues belong in the prompt, not in a separate field.

> A chef slams a cleaver through a watermelon. The blade thuds through the rind with a satisfying crack. Seeds scatter across the wooden cutting board. Kitchen ambiance: sizzling pans, extractor fan humming.

For dialogue, describe the speaker **and delivery tone**:
> A tour guide gestures at the ancient ruins. "This temple was built over two thousand years ago," she says with quiet reverence. Wind whispers through the stone columns.

### Multi-Reference Syntax (`@1`, `@2`, `@3`)

When you pass `image_urls` or reference videos/audio, address them positionally in the prompt:

> `@1` walks through the city with the motion of `@2`, set to the mood of `@3`.

Use cases:
- `@Image` — lock character appearance across clips
- `@Video` — inherit motion style (dance, camera work) from a reference
- `@Audio` — match atmosphere/pacing to a reference track

Limits: 9 images + 3 videos + 3 audio tracks. Reference videos/audio must be ≤15 seconds.

### Negative Prompts (Always Include)

Seedance responds well to explicit exclusions. Append to the `avoid` clause of every prompt:

- `avoid jitter` — suppresses temporal instability
- `avoid bent limbs` — essential for character shots
- `avoid temporal flicker` — for longer / high-motion clips
- `avoid identity drift` — for character consistency across frames

## Common Failures → Fixes

| Problem | Cause | Fix |
|---|---|---|
| Static, lifeless video | No motion verb | Add explicit motion: `steam rising slowly, subtle camera drift right` |
| Flat lighting | No light source specified | `soft side lighting from the left` or `golden afternoon light through windows` |
| Subject inconsistency | Abstract or conflicting descriptors | Use concrete visuals: not "futuristic device" but `white cylinder with a glowing blue ring at its base` |
| Chaotic motion | `fast` keyword used alone, or multiple camera moves | Replace `fast` with a rhythmic modifier; keep ONE camera movement |
| Limb warping | No negative prompt | Append `avoid bent limbs, avoid jitter` |
| Character drift across clips | No reference image | Pass `image_urls` and address as `@1` |

## Iteration Loop

Official recommendation — the **single variable adjustment** method:

1. **Baseline** — generate 2–3 options from the full 6-step prompt
2. **Change one variable** per iteration (camera angle **or** lighting **or** motion intensity — never all three)
3. **Lock** elements that work and keep them constant
4. **Finalize** at 1080p once the prompt is dialed in; use `seedance-2.0-fast` for every draft before the final

Tip: tight close-ups are cheaper to iterate and more consistent than wide landscape shots.

## Parameters

| Parameter | Type | Values | Default | Notes |
|---|---|---|---|---|
| **prompt** | string | — | required | 6-step formula, 60–100 words |
| **image_url** | string | URL | — | Source image for I2V mode |
| **resolution** | enum | 480p, 720p, 1080p | `720p` | Higher = slower and more expensive |
| **duration** | string | — | `auto` | Video duration |
| **aspect_ratio** | string | — | `auto` | Output aspect ratio |
| **generate_audio** | boolean | true/false | `true` | Native audio generation |
| **seed** | integer | — | — | For reproducibility across iterations |
| **image_urls** | array | URLs | — | Reference images, addressed as `@1`..`@9` (via extras) |

## Example Prompts

### Product (orbit + studio lighting)
> Slow orbit around a luxury watch on polished marble. Light refracts through the sapphire crystal, casting prismatic highlights. The second hand ticks with precise mechanical movement. Clean studio lighting, softbox from the left, color temperature: cool. 35mm macro. Subtle ambient music, faint ticking. Avoid jitter.

### Nature / Physics (aerial + golden hour)
> Aerial crane shot descending toward a mountain waterfall. The camera drops from above the treeline into a close-up of water crashing against moss-covered rocks. Spray droplets catch sunlight, forming micro-rainbows. Warm golden hour light, cinematic color grade. Sound of rushing water crescendos as the camera descends. Avoid temporal flicker.

### Human Motion (handheld + neon)
> Handheld tracking shot following a street dancer in a concrete underpass. She spins on one foot, jacket flaring with centrifugal force. Neon reflections on wet pavement, cyan and magenta, single key light from above. Gritty, raw atmosphere. Sneakers squeak on concrete, each footfall echoes. Avoid bent limbs, avoid identity drift.

### Dialogue (fixed + chiaroscuro)
> Medium shot, fixed camera. A dimly lit jazz bar. A man in a leather jacket leans across the table. "I've been thinking about what you said last night," he says quietly. The woman opposite tilts her head, pauses, replies: "And?" Hard chiaroscuro lighting, single warm key light, deep shadows. Glasses clink at the bar. Avoid jitter.

### Image-to-Video (preserve source)
> `@1` turns her head slowly toward the camera, hair lifting in a gentle breeze. Subtle push-in. Preserve composition and colors of the source image. Avoid identity drift, avoid bent limbs.

## When to Use Seedance 2.0

- **Use Seedance 2.0** for: cinematic quality with native audio, physics-heavy motion (water, cloth, impacts), director-level camera control, or multi-reference character/style consistency
- **Use Seedance 2.0 Fast** for: drafts, iteration, and every pass before the final
- **Consider other models** when you need: multi-shot sequencing (Kling v3 Pro), clips longer than ~10s (Sora 2 Pro), first-last-frame transitions (Veo 3.1), or talking avatars (HeyGen)
