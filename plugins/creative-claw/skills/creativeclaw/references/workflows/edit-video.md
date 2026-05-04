# Edit Existing Video Footage

You are editing video by conversation. Transcribe the source(s), pick the best takes, cut on word boundaries, color-grade, burn subtitles, optionally smart-reframe to vertical, and render. The user owns the creative direction; you own the production correctness.

## When to use this workflow

- The user has **existing footage** they want cut, graded, captioned, or reframed
- Talking-head video, montage, tutorial, interview, travel, podcast clips, multi-take selection
- The user wants you to **handle the post-production craft** (cut points, grade decisions, subtitle styling) and only confirm the strategy

If the user wants to **generate new footage from a prompt** → `workflows/video-gen.md`. If the user wants **deterministic, code-driven branded video** → `workflows/code-video-hyperframes.md`.

## Principles

1. **Audio is primary, visuals follow.** Cut candidates come from speech boundaries and silence gaps. Drill into visuals only at decision points.
2. **LLM reasons from raw transcript + on-demand visuals.** The only derived artifact that earns its keep is the packed phrase-level transcript (`takes_packed.md`). Everything else — filler tagging, retake detection, shot classification — is derived at decision time.
3. **Ask → confirm → execute → iterate → persist.** Never touch the cut until the user has confirmed the strategy in plain English.
4. **Generalize.** Don't assume what kind of video this is. Look at the material, ask the user, then edit.
5. **Artistic freedom is the default.** Specific values, presets, fonts, and durations in this guide are *worked examples*. Make your own taste calls. The only mandatory parts are the Hard Rules below.
6. **Verify your own output before showing it.** Self-eval the rendered MP4 at every cut boundary before presenting.

## Hard rules (production correctness — non-negotiable)

These are correctness, not taste. Deviation produces silent failures.

1. **Subtitles applied LAST in the filter chain**, after every overlay. Otherwise overlays hide captions.
2. **Per-segment extract → lossless `-c copy` concat**, not single-pass filtergraph. Otherwise overlays force double-encode of every segment.
3. **30 ms audio fades at every segment boundary** (`afade=t=in:st=0:d=0.03,afade=t=out:st={dur-0.03}:d=0.03`). Otherwise audible pops.
4. **Overlays use `setpts=PTS-STARTPTS+T/TB`** to shift overlay's frame 0 to its window start. Otherwise you see the middle of the animation during the overlay window.
5. **Master SRT uses output-timeline offsets**: `output_time = word.start - segment_start + segment_offset`. Otherwise captions misalign after concat.
6. **Never cut inside a word.** Snap every cut edge to a word boundary from the transcript.
7. **Pad every cut edge.** Working window: 30–200 ms. Tighter for fast-paced, looser for cinematic.
8. **Word-level verbatim ASR only.** Never SRT/phrase mode (loses sub-second gap data). Never normalized fillers (loses editorial signal). Creative Claw's `transcribe` returns this shape natively.
9. **Cache transcripts per source.** Never re-transcribe unless the source file itself changed. The cache file is `<edit_dir>/transcripts/<stem>.json`.
10. **Strategy confirmation before execution.** Never touch the cut until the user has approved the plain-English plan.
11. **All session outputs go in `<videos_dir>/edit/`.** Never write inside the skill directory.

## Directory layout

User footage lives wherever they put it. All session outputs go into `<videos_dir>/edit/`:

```
<videos_dir>/
├── <source files, untouched>
└── edit/
    ├── project.md               ← memory, appended every session
    ├── takes_packed.md          ← phrase-level transcripts (LLM's primary reading view)
    ├── edl.json                 ← cut decisions (see assets/edl-schema.json)
    ├── transcripts/<name>.json  ← cached Scribe JSON (immutable per source)
    ├── animations/slot_<id>/    ← per-overlay source + render
    ├── clips_graded/            ← per-segment extracts with grade + fades
    ├── master.srt               ← output-timeline subtitles
    ├── verify/                  ← debug frames / timeline PNGs
    ├── preview.mp4
    └── final.mp4
```

## Helpers (`helpers/`)

| Script | Purpose |
|---|---|
| `prepare_audio.py <video>` | Extract mono 16 kHz WAV via ffmpeg. Cached against the transcript file. Hands off to MCP `transcribe` (see Step 1). |
| `pack_transcripts.py --edit-dir <dir>` | `transcripts/*.json` → `takes_packed.md`. Phrase-level break on silence ≥ 0.5 s. |
| `timeline_view.py <video> <start> <end>` | Filmstrip + waveform PNG for a time range. **Use at decision points only**, not as a scan tool. |
| `render.py <edl.json> -o <out>` | The full render pipeline. Per-segment extract → concat → overlays (PTS-shifted) → subtitles LAST. `--preview` for 720p fast. `--build-subtitles` to generate master.srt inline. |
| `grade.py <in> -o <out>` | Color grade. Default mode is auto (analyzes brightness/contrast/saturation, applies bounded ±8% correction). Or `--preset warm_cinematic` / `neutral_punch` / raw `--filter`. |
| `smart_vertical.py <in> -o <out>` | Face-tracked 16:9 → 9:16 (1080×1920) reframe. OpenCV YuNet detection, smoothed crop trajectory, single ffmpeg pass. |

All helpers live alongside `SKILL.md`. Resolve their paths from `helpers/` relative to this skill.

## Transcription via Creative Claw

Creative Claw's MCP `transcribe` tool wraps ElevenLabs Scribe — same model, same JSON shape. Billed through the user's Creative Claw credits. **Do not call ElevenLabs directly.**

Per source clip, in order:

1. **Skip if cached.** If `<edit>/transcripts/<stem>.json` exists, do nothing (Hard Rule 9).
2. **Run `prepare_audio.py <video>`.** Extracts mono 16 kHz WAV to a temp file, prints the path. The script prints "cached" and exits 0 if the transcript already exists.
3. **Upload the WAV** to Creative Claw. For files <25 MB use `upload_asset` with the local path; for larger files use `get_upload_url` → `curl PUT` → `confirm_upload`. Tag with `["video-use", "<project>"]` so it's findable later.
4. **Call `transcribe`** with the asset URL:
   ```
   transcribe({
     audio_url: "<R2 URL from upload>",
     diarize: true,
     tag_audio_events: true
     // omit language_code unless user specified — Scribe auto-detects
   })
   ```
   Returns a `jobId`.
5. **Poll `check_job`** until `status === "completed"`. Typical: 30 s – 3 min.
6. **Write the result verbatim** to `<edit>/transcripts/<video_stem>.json`. Shape: `{"words": [{"type": "word"|"spacing"|"audio_event", "start", "end", "text", "speaker_id"}, ...]}` — exactly what `pack_transcripts.py` consumes. If Creative Claw wraps the payload (e.g. `{"transcript": {...}}`), unwrap to the inner Scribe object before writing.
7. **Run `pack_transcripts.py --edit-dir <edit>`** to produce `takes_packed.md`.

For multi-take folders: fire one `transcribe` per source in parallel (multiple MCP calls in one message), poll all jobs together. Cap at ~4 concurrent.

If Creative Claw `transcribe` is unavailable, **stop and tell the user**. Do not fall back to direct ElevenLabs calls.

## B-roll: identify by start frame

B-roll usually doesn't need transcription. Instead, extract the first frame of each b-roll source and look at it before placing it.

1. **Extract a representative frame** to `<edit>/verify/broll_thumbs/<stem>.jpg`:
   ```bash
   ffmpeg -y -i <broll.mp4> -vframes 1 -q:v 2 <edit>/verify/broll_thumbs/<stem>.jpg
   # or skip 2s in if the head is black/slate:
   ffmpeg -y -ss 2 -i <broll.mp4> -vframes 1 -q:v 2 <edit>/verify/broll_thumbs/<stem>.jpg
   ```
   Run all extractions in parallel (one Bash call per clip in a single message).

2. **Open each thumbnail with Read** so you actually see it. Caption each one in plain English (one line). For ambiguous or long clips, use `timeline_view.py` for a filmstrip.

3. **Match b-roll to narration beats** using the talking-head transcript. Note `(broll_clip, narration_time_range, why)` triples in your strategy proposal before cutting.

4. **Place b-roll as overlays** in `edl.json` (`overlays[]` field) with `start_in_output` aligned to the narration beat. Hard Rule 1 still holds — subtitles render after b-roll overlays.

When the user drops a `broll/` folder, treat it as a b-roll source set automatically. Don't transcribe b-roll unless they say it has usable dialogue.

## The process

1. **Inventory.** `ffprobe` every source. Run `prepare_audio.py` then transcribe-via-MCP each primary clip in parallel. Run `pack_transcripts.py`. Sample one or two `timeline_view`s for a visual first impression.
2. **Pre-scan for problems.** One pass over `takes_packed.md` to note verbal slips, mis-speaks, phrasings to avoid. Plain list, feeds into the editor brief.
3. **Converse.** Describe what you see in plain English. Ask material-shaped questions. Collect: content type, target length and aspect, aesthetic / brand direction, pacing feel, must-preserve moments, must-cut moments, animation and grade preferences, subtitle needs. Don't use a fixed checklist.
4. **Propose strategy** (4–8 sentences): shape, take choices, cut direction, animation plan, grade direction, subtitle style, length estimate. **Wait for confirmation.**
5. **Execute.** Build `edl.json` (see `assets/edl-schema.json` for the shape). Drill into `timeline_view` at ambiguous moments. Build animation overlays in parallel sub-agents (one Agent call per slot). Apply grade per-segment via `render.py`. Compose final via `render.py`.
6. **Preview** with `render.py --preview` (720 p fast).
7. **Self-eval** before showing the user. Run `timeline_view` on the **rendered output** at every cut boundary (±1.5 s window). Check each image for:
   - Visual discontinuity / flash / jump at the cut
   - Waveform spike at the boundary (audio pop that slipped past the 30 ms fade)
   - Subtitle hidden behind an overlay (Rule 1 violation)
   - Overlay misaligned or showing wrong frames (Rule 4 violation)

   Also sample first 2 s, last 2 s, and 2–3 mid-points — grade consistency, subtitle readability, overall coherence. Run `ffprobe` on the output to verify duration matches `total_duration_s`.

   If anything fails: fix → re-render → re-eval. **Cap at 3 self-eval passes.** If issues remain, flag them rather than looping.
8. **Audio polish (optional, voice tracks only).** If the source audio sounds noisy — background hum, room reverb, traffic, music bleed, HVAC, keyboard clicks — offer voice isolation **before** the final render but **after** all cuts are locked. See "Voice isolation" below. Skip silently for clean studio audio or when the user explicitly wants ambient sound preserved.
9. **Iterate + persist.** Natural-language feedback, re-plan, re-render. Never re-transcribe. On confirmation, do the final render. Append a section to `<edit>/project.md`.

## EDL — the single artifact

The Edit Decision List is the only file that fully describes the cut. The LLM authors it; `render.py` consumes it. Schema lives at `assets/edl-schema.json`. Example:

```json
{
  "version": 1,
  "sources": {
    "C0103": "/abs/path/C0103.MP4",
    "C0108": "/abs/path/C0108.MP4"
  },
  "ranges": [
    { "source": "C0103", "start": 2.42, "end": 6.85,
      "beat": "HOOK", "quote": "...", "reason": "Cleanest delivery." },
    { "source": "C0108", "start": 14.30, "end": 28.90,
      "beat": "SOLUTION", "quote": "...", "reason": "Only take without false start." }
  ],
  "grade": "warm_cinematic",
  "overlays": [
    { "file": "edit/animations/slot_1/render.mp4", "start_in_output": 0.0, "duration": 5.0 }
  ],
  "subtitles": "edit/master.srt",
  "total_duration_s": 87.4
}
```

**Field semantics:**
- `sources` — ID → absolute path. Lets `ranges` reference clips compactly.
- `ranges[]` — ordered cuts. `start`/`end` in source-clip time. Concatenated to form the output. `beat` / `quote` / `reason` are LLM-written rationale kept for re-edits.
- `grade` — preset name or raw ffmpeg filter string. Applied per-segment during extract (Hard Rule 2).
- `overlays[]` — `start_in_output` is in OUTPUT timeline. PTS shift handled by `render.py` (Hard Rule 4).
- `subtitles` — path to master SRT, applied LAST (Hard Rule 1).
- `total_duration_s` — sanity check; `render.py` verifies via ffprobe.

## Cut craft

- **Audio-first.** Candidate cuts from word boundaries and silence gaps in the transcript.
- **Preserve peaks.** Laughs, punchlines, emphasis. Extend past punchlines to include reactions — the laugh IS the beat.
- **Speaker handoffs benefit from air.** 400–600 ms common. Less for fast-paced, more for cinematic.
- **Audio events are signals.** `(laughs)`, `(sighs)`, `(applause)` mark beats — extend past them.
- **Silence gaps are cut candidates.** ≥ 400 ms is usually clean. 150–400 ms is usable with a visual check. < 150 ms is unsafe (mid-phrase).
- **Pad cut edges 30–200 ms.** Tighter for montage energy, looser for documentary. Worked example from one shipped video: 50 ms before first kept word, 80 ms after last.
- **Never reason audio and video independently.** Every cut must work on both tracks.

## Color grade

Reason about the image, not a preset. Look at a frame via `timeline_view`, decide what's wrong, adjust one thing, look again.

Mental model is ASC CDL. Per channel: `out = (in * slope + offset) ** power`, then global saturation. `slope` → highlights, `offset` → shadows, `power` → midtones.

Default mode of `grade.py` is **auto** — measures brightness, contrast, saturation; emits a bounded ±8% correction. "Clean without looking graded." Safe default.

For creative looks, use `--preset warm_cinematic` (subtle teal/orange split, desaturated) or `--preset neutral_punch` (contrast bump + S-curve, no hue shifts) or `--filter '<raw ffmpeg>'`.

Apply **per-segment during extract** (not post-concat — re-encodes twice).

## Subtitles

Three dimensions to reason about: **chunking** (1/2/3/sentence per line), **case** (UPPER/Title/Natural), **placement** (margin from bottom). Right combo depends on content.

Worked example: **`bold-overlay`** (short-form tech launch, fast-paced social) — 2-word chunks, UPPERCASE, break on punctuation, Helvetica 18 Bold, white-on-outline, `MarginV=35`. `render.py` ships this as `SUB_FORCE_STYLE`.

For narrative / documentary / education: 4–7 word chunks, sentence case, larger font, `MarginV=60–80`.

Hard rules: subtitles last (Rule 1), output-timeline offsets (Rule 5).

## Animations / overlays

Match the brand and the content. Get palette and font from the conversation — don't assume defaults. If user hasn't said, propose in the strategy phase.

**Tool options:**
- **PIL + PNG sequence + ffmpeg** — simple overlay cards (counters, typewriter text, single bar reveals). Fast to iterate.
- **HyperFrames** (`render_html_video` MCP tool) — for HTML/CSS/JS-driven branded overlays with GSAP animation. See `workflows/code-video-hyperframes.md` and `hyperframes-primer.md`.
- **Manim** — formal diagrams, equation derivations, graph morphs.

**Duration rules of thumb** (context-dependent):
- Sync-to-narration explanations: 5–7 s simple cards, 8–14 s complex diagrams.
- Beat-synced accents (music, fast montage): 0.5–2 s.
- Hold the final frame ≥ 1 s before the cut.
- Over voiceover: total duration ≥ `narration_length + 1 s`.
- Never parallel-reveal independent elements — eye can't track two new things at once.

**Easing** (universal — never `linear`):
```python
def ease_out_cubic(t):    return 1 - (1 - t) ** 3
def ease_in_out_cubic(t):
    if t < 0.5: return 4 * t ** 3
    return 1 - (-2 * t + 2) ** 3 / 2
```

**Parallel sub-agent pattern** for multiple animations:
- One `Agent` tool call per slot, all dispatched in a single message.
- Each prompt is self-contained (sub-agents have no parent context). Include: one-sentence goal, absolute output path, exact tech spec (resolution, fps, codec, pix_fmt, CRF, duration), style palette as concrete values, font path, frame-by-frame timeline, anti-list, deliverable checklist, and "Do not ask questions — pick the most obvious interpretation and proceed."
- One sub-agent = one file (unique filenames; parallel agents don't overwrite).

## Voice isolation (final audio polish)

Use the MCP `isolate_audio` tool (ElevenLabs Voice Isolator) to strip background noise, music, and reverb from the voice track. This is the **last** audio step — run it after all cuts are locked and concatenated, never on raw source clips (that would invalidate the cached transcript).

**When to suggest it:**
- Audible background hum, traffic, HVAC, keyboard clicks, room reverb, or music bleed in the talking-head track
- User flags audio quality as a concern
- Repurposing field-recorded footage (phone, on-location, untreated room)

**When NOT to use it:**
- Clean studio / lavalier / treated-room audio — isolation can introduce artifacts on already-clean tracks
- The ambient sound is **part of the piece** (concert, street scene, ASMR, environmental documentary)
- B-roll-only or music-driven segments with no voice

**Always confirm with the user first.** It costs credits and changes the sonic character. Frame it like: *"The room tone on this is pretty noisy — want me to run voice isolation as a final pass? It'll strip the background but the voice will sound a bit drier."* Wait for yes before running.

**How to apply (final step, after cuts are locked):**

1. After `render.py` produces the cut video (with concatenated audio, fades, but **before** subtitles burn-in is locked as final), extract the audio track:
   ```bash
   ffmpeg -y -i <cut>.mp4 -vn -c:a pcm_s16le <edit>/audio_pre_isolation.wav
   ```
2. Upload via `upload_asset` (small) or `get_upload_url` → PUT → `confirm_upload` (large). Tag `["video-use", "<project>", "pre-isolation"]`.
3. Call `isolate_audio({ audio_url: "<R2 URL>" })`. Returns `jobId`.
4. Poll `check_job` until `status === "completed"`. Typical: 20 s – 2 min depending on length.
5. Download the cleaned audio URL to `<edit>/audio_isolated.wav`.
6. Mux back into the cut video (video stream untouched, audio replaced):
   ```bash
   ffmpeg -y -i <cut>.mp4 -i <edit>/audio_isolated.wav \
     -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k <edit>/cut_isolated.mp4
   ```
7. Re-apply subtitles burn-in over `cut_isolated.mp4` (Hard Rule 1 still holds — subtitles last).
8. Self-eval: spot-check 2–3 segments for unnatural artifacts, lisp/sibilance damage, or over-aggressive cleanup. If isolation made it worse, fall back to the pre-isolation cut and tell the user.

**Why audio-only and not the whole video?** `isolate_audio` only accepts audio URLs, and decoupling it lets you keep the locked picture/cut intact while swapping just the audio track — no re-encode of video, no risk to overlays or grade.

## Smart vertical reframe

`smart_vertical.py <in> -o <out>` reframes 16:9 → 1080×1920 driven by face tracking. Use when the user wants to repurpose landscape footage as TikTok / Reels / Shorts. Tracks face centers every N frames, smooths the trajectory, single ffmpeg pass with `crop` driven by sendcmd.

## Memory — `project.md`

Append one section per session at `<edit>/project.md`:

```markdown
## Session N — YYYY-MM-DD

**Strategy:** one paragraph
**Decisions:** take choices, cuts, grades, animations + why
**Reasoning log:** one-line rationale for non-obvious decisions
**Outstanding:** deferred items
```

On startup, read `project.md` if it exists and summarize the last session in one sentence before asking whether to continue.

## Anti-patterns

- **Hand-tuned moment-scoring functions.** The LLM picks better than any heuristic.
- **Whisper SRT / phrase-level output.** Loses sub-second gap data — always word-level verbatim.
- **Burning subtitles into base before compositing overlays.** Overlays hide them (Hard Rule 1).
- **Single-pass filtergraph with overlays.** Double re-encode. Use per-segment extract → concat.
- **Linear easing.** Robotic. Always cubic.
- **Hard audio cuts at boundaries.** Audible pops (Hard Rule 3).
- **Sequential sub-agents for animations.** Always parallel.
- **Editing before confirming the strategy.** Never.
- **Re-transcribing cached sources.** Immutable outputs of immutable inputs.
- **Falling back to direct ElevenLabs calls.** If Creative Claw `transcribe` is unavailable, stop and tell the user.
- **Assuming what kind of video it is.** Look first, ask second, edit last.
- **Running `isolate_audio` on raw source clips or before cuts are locked.** Always operate on the final concatenated audio, after cuts. Otherwise you waste credits and risk invalidating the transcript cache.
- **Running `isolate_audio` without asking.** Costs credits and changes sonic character — confirm with the user before submitting.
- **Running `isolate_audio` on already-clean studio audio.** It introduces artifacts on tracks that don't need it.

## MCP tools used here

**Transcription** — `transcribe`, `check_job`, `upload_asset` (or `get_upload_url` + `confirm_upload`)
**Audio polish** — `isolate_audio` (final pass, voice-only tracks; ask user first)
**Editing** — `trim_video`, `scale_video`, `merge_media`, `add_subtitles`, `extract_frames`, `remove_background` (when needed)
**Assets** — `search_assets`, `update_asset`, `import_media`
**Credits** — `get_credits_balance` (transcription burns credits)
