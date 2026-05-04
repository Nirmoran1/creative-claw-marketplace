# xAI TTS

**Model ID:** `speech/xai-tts`
**Endpoint:** `xai/tts/v1`
**Tool:** `generate_speech`

xAI's text-to-speech model. Designed around expressive spoken delivery — it
understands inline and wrapping markup that directs emotion, pacing, and
volume in-line with the text. Same speech stack that powers Tesla and
Starlink voice interfaces. Strong in 20 languages, with telephony-ready
output codecs (G.711 μ-law/A-law) for phone-call use cases.

## Why pick it

- **Expressive out of the box** — mark `[laugh]`, `[sigh]`, `[pause]` inside
  the text and the model delivers them as audio cues. No model-side config.
- **Span-level control** — wrap a phrase in `<whisper>…</whisper>` or
  `<emphasis>…</emphasis>` and the delivery changes only for that span.
- **Telephony native** — ask for `output_format: "mulaw"` at `sample_rate:
8000` and you get audio that drops straight into an IVR / phone bridge.
- **Cheap** — $0.0042 / 1k characters (1 credit / 1k chars). Roughly 5× cheaper
  than MiniMax HD and 20× cheaper than ElevenLabs v3.

## Parameters

| Parameter       | Values                                                 | Default  | Notes                                                                 |
| --------------- | ------------------------------------------------------ | -------- | --------------------------------------------------------------------- |
| `text`          | string, max 15,000 chars                               | required | Plain text with optional inline/wrapping tags (see below)             |
| `voice_id`      | `eve`, `ara`, `rex`, `sal`, `leo`                      | `eve`    | 5 voices, mix of male/female. Pick by ear — descriptions are minimal. |
| `language`      | `auto`, `en`, `es`, `fr`, `de`, `it`, `pt`, … (20+)    | `auto`   | `auto` detects from text. Force when the text is ambiguous.           |
| `output_format` | `mp3`, `wav`, `pcm`, `mulaw`, `alaw`                   | `mp3`    | Use `mulaw`/`alaw` + 8kHz for telephony.                              |
| `sample_rate`   | `8000`, `16000`, `22050`, `24000`, `44100`, `48000` Hz | `24000`  | 8000 for phone, 24000 for default speech, 48000 for high-fi.          |

Top-level `generate_speech` params map cleanly:

- `text` → `text` ✓
- `voice_id` → `voice_id` ✓

Other xAI params don't share names with our generic TTS schema, so pass them
through `extras`:

```json
{
  "model": "speech/xai-tts",
  "text": "…",
  "voice_id": "eve",
  "extras": {
    "language": "en",
    "output_format": "wav",
    "sample_rate": 24000
  }
}
```

## Speech tags (the differentiator)

Tags go **inside the text** — you don't need to pass them as a separate
parameter. The model reads them as direction, not as words to speak aloud.

### Inline cues (non-verbal sounds + pacing)

Drop these at the exact point in the text where the cue should happen:

| Tag         | Effect                                                 |
| ----------- | ------------------------------------------------------ |
| `[laugh]`   | Short laugh                                            |
| `[chuckle]` | Softer, shorter laugh                                  |
| `[sigh]`    | Audible exhale                                         |
| `[breath]`  | Breath intake                                          |
| `[pause]`   | Brief silence (≈ short comma)                          |
| `[whisper]` | Next phrase delivered as a whisper (until punctuation) |

> "Oh [sigh] fine. [pause] I'll do it myself."

### Wrapping tags (span-level delivery)

Apply to a phrase. Must be closed — the style reverts after `</…>`.

| Tag                      | Effect                               |
| ------------------------ | ------------------------------------ |
| `<whisper>…</whisper>`   | Quiet, breathy delivery              |
| `<emphasis>…</emphasis>` | Stressed, louder, slightly slower    |
| `<slow>…</slow>`         | Reduces pace without dropping volume |
| `<loud>…</loud>`         | Raises volume without yelling        |

> `<whisper>Don't look now, but</whisper> <emphasis>he's right behind you.</emphasis>`

### Combining tags

Wrapping and inline tags can nest:

> `<whisper>He leaned in [pause] "are you sure?"</whisper>`

Keep it readable — stacking too many cues in one sentence usually degrades
output. Treat them like stage directions, not markup.

## Telephony (IVR / phone-call audio)

For playback over a phone bridge or SIP trunk, you want G.711 at 8 kHz:

```json
{
  "model": "speech/xai-tts",
  "text": "Thanks for calling. Press 1 for sales, 2 for support.",
  "voice_id": "rex",
  "extras": {
    "output_format": "mulaw",
    "sample_rate": 8000
  }
}
```

- `mulaw` (μ-law) for North American / Japanese phone systems
- `alaw` for European phone systems
- `pcm` at 8000 Hz if you want to transcode yourself

## Language handling

- Leave `language: "auto"` for mixed or English-only content
- Force `language` when the text is short and ambiguous (single words,
  proper nouns, numeric strings)
- xAI's pronunciation is phonetically strong on phone-call vocabulary —
  names, account numbers, financial/medical/legal terminology — which is
  noticeably better than most general-purpose TTS models

## Cost

- $0.0042 per 1,000 characters → **1 credit per 1,000 characters**
- 500 chars = 1 credit (minimum)
- Full 15,000-char request = 15 credits

## When to use xAI TTS vs other speech models

- **Use xAI TTS** for: expressive narration, phone-call / IVR audio,
  budget-sensitive long-form content, and anywhere you want stage
  directions inside the text.
- **Use MiniMax HD** for: 300+ voices, fine-grained emotion/pitch/speed
  controls, high-quality multilingual dubbing.
- **Use ElevenLabs v3** for: voice cloning, highest naturalness, 32+
  languages at premium quality.
- **Use Dia TTS** for: multi-speaker dialogue where you need `[S1]`/`[S2]`
  turn-taking.
- **Use Chatterbox** for: zero-shot voice cloning from a reference clip.
- **Use Kokoro** for: pure throughput / testing when you don't care about
  expressiveness.

## Example: expressive narration

```json
{
  "model": "speech/xai-tts",
  "voice_id": "ara",
  "text": "So I walk in, right? [pause] And he's just [laugh] standing there with the cat on his head. <whisper>I couldn't look away.</whisper> <emphasis>It was magnificent.</emphasis>"
}
```

## Example: mixed-language announcement

```json
{
  "model": "speech/xai-tts",
  "voice_id": "eve",
  "text": "Welcome aboard. [pause] Bienvenido a bordo.",
  "extras": { "language": "auto" }
}
```

## Limits & gotchas

- **15,000 character cap per request.** For longer content, split on
  sentence boundaries and stitch the audio in post.
- **Tags are best-effort.** Tags at the very start of a sentence or
  adjacent to other tags occasionally get dropped — rephrase if a cue
  goes missing.
- **`auto` language can mispredict** on 1–2 word inputs. Force `language`
  for short strings.
- **Returned URL is short-lived on fal.** `generate_speech` already
  re-hosts the audio to R2, so the URL in the tool result is permanent.
