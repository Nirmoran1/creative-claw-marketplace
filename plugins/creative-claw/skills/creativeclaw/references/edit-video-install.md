# Edit-Video Install

One-time setup before the `edit-video` workflow can run. Read this only when the preflight in `workflows/edit-video.md` reports `MISSING`. Daily editing reads `workflows/edit-video.md`, not this file.

## Install prompt contract (read first)

You — the agent — are doing this install. The user is at the keyboard, not driving.

- **Run the preflight first**, then tell the user in one sentence what's missing and what you'll do about it. Wait for their go-ahead.
- **Do everything yourself.** The only things to ask the user about: confirming a `brew install` they'll see in the terminal, or pasting a sudo password if a system dialog forces one.
- **Never silently continue with a missing tool.** A failing helper mid-edit is worse than a 60-second install detour.
- **Verify with a real Python import at the end** — `command -v` is not enough.

## What's actually needed

| Dep | Used by | Why |
|---|---|---|
| `ffmpeg` + `ffprobe` | every helper | Cuts, extracts, grades, concats, muxes. |
| `python3` (≥ 3.10) | every helper | The helpers are Python scripts. |
| `pillow`, `numpy`, `opencv-python` | helpers | PNG overlays, array math, face detection. |

That's it. Transcription runs server-side via the Creative Claw MCP — no API key, no local Whisper.

## Step 0 — Preflight

```bash
echo "--- edit-video preflight ---"
command -v ffmpeg >/dev/null && command -v ffprobe >/dev/null && echo "ffmpeg: OK" || echo "ffmpeg: MISSING"
command -v python3 >/dev/null && python3 --version 2>&1 | sed 's/^/python3: /' || echo "python3: MISSING"
python3 -c "import PIL, numpy, cv2" 2>/dev/null && echo "py-deps: OK" || echo "py-deps: MISSING"
command -v brew >/dev/null && echo "brew: present" || echo "brew: not installed (fine, use uv path below)"
echo "--- end ---"
```

Pick the install path based on the `brew:` line. **Do not install Homebrew if it isn't there** — the `uv` path is faster and needs no admin.

## Path A — brew is present

Three commands cover everything that's missing:

```bash
brew install ffmpeg          # if ffmpeg: MISSING
brew install python@3.12     # if python3 is missing or < 3.10
brew install uv              # only if you don't already have uv or pipx
```

Then install the Python deps without polluting system Python:

```bash
uv pip install --system pillow numpy opencv-python
```

Skip to Step 2 to verify.

## Path B — no brew (don't install it)

Stay lean. `uv` handles everything except the `ffmpeg` binary, and a static `ffmpeg` build is one download.

### B1. Install `uv` (one line, no admin)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then make sure it's on this shell's PATH for the rest of the install:

```bash
export PATH="$HOME/.local/bin:$PATH"
command -v uv && uv --version   # should print a version
```

### B2. Let `uv` manage Python and the deps

`uv` will download a self-contained Python if one isn't installed. Create a scoped venv so nothing leaks into the rest of the system:

```bash
uv python install 3.12   # no-op if 3.12+ is already there
uv venv ~/.creativeclaw/edit-video-venv --python 3.12
uv pip install --python ~/.creativeclaw/edit-video-venv/bin/python \
  pillow numpy opencv-python
```

Tell the user: helpers will be invoked via `~/.creativeclaw/edit-video-venv/bin/python helpers/<name>.py`. The workflow doc already supports this — set `EDIT_VIDEO_PYTHON=~/.creativeclaw/edit-video-venv/bin/python` in the shell or pass the full path each call.

### B3. Static `ffmpeg`

Download a self-contained binary, drop it in `~/.local/bin`, no admin needed.

```bash
mkdir -p ~/.local/bin
# macOS — evermeet.cx ships notarized static arm64/x86_64 builds
curl -L https://evermeet.cx/ffmpeg/getrelease/zip -o /tmp/ffmpeg.zip
curl -L https://evermeet.cx/ffmpeg/getrelease/ffprobe/zip -o /tmp/ffprobe.zip
unzip -o /tmp/ffmpeg.zip  -d ~/.local/bin
unzip -o /tmp/ffprobe.zip -d ~/.local/bin
chmod +x ~/.local/bin/ffmpeg ~/.local/bin/ffprobe

export PATH="$HOME/.local/bin:$PATH"
ffmpeg -version | head -1
```

If macOS Gatekeeper flags the binary on first run, `xattr -dr com.apple.quarantine ~/.local/bin/ffmpeg ~/.local/bin/ffprobe` clears it.

For Linux, install via the system package manager (`apt-get install ffmpeg`, `pacman -S ffmpeg`, etc.) — static builds aren't worth the trouble there.

## Step 2 — Verify with real imports

`command -v` lies (stub binaries, broken native deps). Run the actual things the helpers will run:

```bash
ffprobe -version | head -1
python3 -c "import PIL, numpy, cv2; print('py-deps OK', PIL.__version__, numpy.__version__, cv2.__version__)"
```

If you took Path B, swap `python3` for the venv interpreter:

```bash
~/.creativeclaw/edit-video-venv/bin/python -c "import PIL, numpy, cv2; print('OK')"
```

Both must succeed. If they do, tell the user:

> *"Edit-video tools are ready. Drop a clip into a folder and tell me what you want — cuts, subtitles, color grade, vertical reframe."*

If anything fails, surface the exact error to the user instead of silently continuing.

## Cold-start notes

- **`opencv-python` install takes 30–60 s** the first time (native wheels). That's normal — tell the user before kicking it off so they don't think it's hung.
- **Apple Silicon:** all three Python wheels and the evermeet ffmpeg builds have native arm64 versions. No flags needed.
- **PEP 668 / `externally-managed-environment`:** the symptom of running bare `pip install` on Homebrew/system Python. Both paths above dodge it (`uv pip install --system` on Path A, scoped venv on Path B). Don't reach for `--break-system-packages`.
- **Don't run a real transcription as part of install.** It costs Creative Claw credits. Wait for the user's first clip.
- **Re-install / upgrade later:** `brew upgrade ffmpeg` (Path A) or re-run the evermeet curl + `uv pip install -U pillow numpy opencv-python` (Path B). Helpers are version-tolerant — any modern ffmpeg (≥ 4.x) and opencv-python ≥ 4.7 work.
