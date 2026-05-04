"""Extract mono 16 kHz PCM WAV from a video for transcription via Creative Claw.

Creative Claw's `transcribe` MCP tool accepts audio only (not video). This helper
runs the ffmpeg extraction step and prints the resulting WAV path. Claude then
uploads the WAV to Creative Claw via `upload_asset` (or `get_upload_url` for
files >25 MB), calls the `transcribe` tool, polls `check_job`, and writes the
returned JSON to `<edit_dir>/transcripts/<video_stem>.json`.

This script does NOT call any API. It is purely the deterministic audio-prep
step. The MCP calls happen on Claude's side so they're billed through the user's
Creative Claw credits and visible in their dashboard.

Cached: if `<edit_dir>/transcripts/<video_stem>.json` already exists, prints
"cached" and exits 0 — Hard Rule 9 (never re-transcribe).

Usage:
    python helpers/prepare_audio.py <video_path>
    python helpers/prepare_audio.py <video_path> --edit-dir /custom/edit
    python helpers/prepare_audio.py <video_path> --out /tmp/specific.wav
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def extract_audio(video_path: Path, dest: Path) -> None:
    """Run ffmpeg to extract mono 16 kHz s16le PCM WAV."""
    cmd = [
        "ffmpeg", "-y", "-i", str(video_path),
        "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le",
        str(dest),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(f"ffmpeg failed:\n{result.stderr}")


def main() -> None:
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg not found on PATH — install it first")

    ap = argparse.ArgumentParser(
        description="Extract audio for Creative Claw transcription. "
                    "Prints the WAV path on success — Claude uploads + transcribes via MCP."
    )
    ap.add_argument("video", type=Path, help="Path to video file")
    ap.add_argument(
        "--edit-dir", type=Path, default=None,
        help="Edit output directory (default: <video_parent>/edit). "
             "Used for cache check against transcripts/<stem>.json.",
    )
    ap.add_argument(
        "--out", type=Path, default=None,
        help="Output WAV path (default: a temp file in /tmp that the OS cleans up). "
             "Pass an explicit path if you need the WAV to persist.",
    )
    args = ap.parse_args()

    video = args.video.resolve()
    if not video.exists():
        sys.exit(f"video not found: {video}")

    edit_dir = (args.edit_dir or (video.parent / "edit")).resolve()
    transcript_path = edit_dir / "transcripts" / f"{video.stem}.json"

    if transcript_path.exists():
        print(f"cached: {transcript_path}")
        sys.exit(0)

    if args.out:
        out_wav = args.out.resolve()
        out_wav.parent.mkdir(parents=True, exist_ok=True)
    else:
        # mkstemp so the file persists past this process — caller decides when to delete
        fd, tmp_path = tempfile.mkstemp(suffix=f"_{video.stem}.wav", prefix="cc_audio_")
        import os
        os.close(fd)
        out_wav = Path(tmp_path)

    extract_audio(video, out_wav)

    size_mb = out_wav.stat().st_size / (1024 * 1024)
    print(f"audio: {out_wav}")
    print(f"size_mb: {size_mb:.2f}")
    print(f"target_transcript: {transcript_path}")
    print()
    print("Next steps for Claude (do NOT have the user run these):")
    if size_mb < 25:
        print(f"  1. upload_asset(file_url='file://{out_wav}', tags=['video-use', '{video.stem}'])")
    else:
        print(f"  1. get_upload_url(filename='{out_wav.name}') → curl PUT → confirm_upload(...)")
    print("  2. transcribe(audio_url=<asset url>, diarize=true, tag_audio_events=true)")
    print("  3. check_job(jobId) until completed")
    print(f"  4. Write the returned Scribe JSON verbatim to {transcript_path}")


if __name__ == "__main__":
    main()
