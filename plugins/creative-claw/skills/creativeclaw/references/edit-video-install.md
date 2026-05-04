# Edit-Video Install (system tools)

One-time setup on a new machine before the `edit-video` workflow can run. Read this only when a preflight check fails — daily editing reads `workflows/edit-video.md`.

## What you're installing

The Creative Claw plugin itself is already installed (you got here through it). What's missing is the **system-level toolchain** the local helpers in `helpers/` shell out to:

| Dep | Used by | Why |
|---|---|---|
| `ffmpeg` + `ffprobe` | `prepare_audio.py`, `render.py`, `grade.py`, `smart_vertical.py` | Every cut, extract, grade, concat, mux. Hard requirement. |
| `python3` (≥ 3.10) | all helpers | The helpers are Python scripts. |
| `pillow` (PIL) | `render.py`, `timeline_view.py` | PNG overlay generation, filmstrip composition. |
| `numpy` | `smart_vertical.py`, `timeline_view.py` | Array math for face-track smoothing and waveforms. |
| `opencv-python` | `smart_vertical.py` | YuNet face detection for 16:9 → 9:16 reframe. |
| `yt-dlp` *(optional)* | manual download step | Only needed if the user wants you to pull source clips from a URL. |

Transcription is **not** in this list — `transcribe` runs server-side via the Creative Claw MCP. No ElevenLabs API key is needed.

## Preflight check

Run this before the first helper call in any new edit session. If everything passes, do nothing and proceed with the workflow:

```bash
command -v ffmpeg >/dev/null && command -v ffprobe >/dev/null && \
  python3 -c "import PIL, numpy, cv2" 2>/dev/null && echo "edit-video OK" || \
  echo "edit-video MISSING — see references/edit-video-install.md"
```

If it prints `MISSING`, do the install steps below before touching any helper.

## Install steps

### 1. ffmpeg (required)

```bash
# macOS
command -v ffmpeg >/dev/null || brew install ffmpeg

# Debian / Ubuntu
# sudo apt-get update && sudo apt-get install -y ffmpeg

# Arch
# sudo pacman -S ffmpeg
```

If a sudo or brew prompt is needed, **tell the user the exact command and wait**. Do not invent a password. On macOS without Homebrew, point the user at https://brew.sh and stop.

### 2. Python deps (required)

```bash
# Prefer uv if available; otherwise pip.
command -v uv >/dev/null && \
  uv pip install --system pillow numpy opencv-python || \
  pip install pillow numpy opencv-python
```

If the user is in a project with its own Python environment (venv / poetry / conda), install into that environment instead — don't pollute their global `site-packages`.

### 3. yt-dlp (optional)

Only install if the user actually wants to pull source clips from URLs. Don't block install on it.

```bash
# macOS
brew install yt-dlp
# Linux
pip install yt-dlp
```

## Verify

Re-run the preflight check above. It must print `edit-video OK` before you proceed. If it still prints `MISSING`, surface the import error to the user — don't silently continue and let a helper crash mid-edit.

```bash
ffprobe -version | head -1
python3 -c "import PIL, numpy, cv2; print('python deps OK')"
```

## Cold-start notes

- **Don't run a real transcription as part of install.** It costs Creative Claw credits. Wait until the user gives you their first clip.
- **`opencv-python` install can be slow** (~30–60 s on first install — it pulls a wheel with native libs). That's normal; don't kill it.
- **Apple Silicon:** all deps have native arm64 wheels. No special flags needed.
- **Linux without a recognized package manager:** print the manual ffmpeg URL (https://ffmpeg.org/download.html) and wait rather than guessing.
- **Already installed via the system but venv is active:** `python3 -c "import cv2"` may fail inside a fresh venv even when global has it. Install into the active environment, not globally.
- **Re-install / upgrade:** `pip install -U pillow numpy opencv-python` and `brew upgrade ffmpeg`. The helpers are version-tolerant — any modern ffmpeg (≥ 4.x) and any opencv-python ≥ 4.7 work.
