"""Smart vertical (9:16) crop driven by face tracking.

Reads a 16:9 video, detects faces every N frames using OpenCV YuNet,
smooths the crop trajectory, and renders 1080×1920 with ffmpeg
using a sendcmd-driven `crop` filter.

Usage:
    python smart_vertical.py input.mp4 -o output.mp4
    python smart_vertical.py input.mp4 -o output.mp4 --sample-fps 4 --smooth 1.5

Algorithm:
  1. Sample frames at `sample_fps`. For each: run YuNet face detection.
  2. Crop center x = mean of detected face centers (clamped to valid range).
     0 faces → keep previous (or center).
  3. Low-pass smooth the (t, x) trajectory with a moving average over
     `smooth` seconds — eliminates jitter while still tracking.
  4. Emit ffmpeg sendcmd file with crop x updates at `sample_fps`.
  5. Single ffmpeg pass: sendcmd → crop → libx264.
"""
from __future__ import annotations
import argparse, json, subprocess, urllib.request
from pathlib import Path
import cv2
import numpy as np

YUNET_URL = "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx"
YUNET_PATH = Path("~/.cache/face_detection_yunet_2023mar.onnx").expanduser()


def ensure_model() -> Path:
    if not YUNET_PATH.exists():
        YUNET_PATH.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(YUNET_URL, YUNET_PATH)
    return YUNET_PATH


def detect_track(
    video_path: Path,
    sample_fps: float,
    conf: float = 0.6,
    speaker_at: "callable | None" = None,
) -> list[tuple[float, float | None]]:
    """Return list of (t, face_center_x_norm) where x_norm is in [0, 1] or None.

    If speaker_at(t) is provided, it returns "left", "right", or None — used to
    pick the appropriate face when ≥2 faces are detected.
    """
    cap = cv2.VideoCapture(str(video_path))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"  source: {W}x{H} @ {fps:.2f}fps, {total} frames")

    det = cv2.FaceDetectorYN.create(str(ensure_model()), "", (W, H), conf, 0.3, 5000)
    step = max(1, int(round(fps / sample_fps)))

    points: list[tuple[float, float | None]] = []
    n = 0
    while True:
        cap.set(cv2.CAP_PROP_POS_FRAMES, n)
        ok, frame = cap.read()
        if not ok:
            break
        t = n / fps
        _, faces = det.detect(frame)
        cx = None
        if faces is not None and len(faces) > 0:
            faces_sorted = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)[:2]
            biggest = faces_sorted[0][2] * faces_sorted[0][3]
            kept = [f for f in faces_sorted if (f[2] * f[3]) >= 0.3 * biggest]
            if len(kept) >= 2 and speaker_at is not None:
                side = speaker_at(t)
                if side in ("left", "right"):
                    by_x = sorted(kept, key=lambda f: f[0])
                    chosen = by_x[0] if side == "left" else by_x[-1]
                    cx = float(chosen[0] + chosen[2] / 2) / W
                else:
                    centers = [float(f[0] + f[2] / 2) for f in kept]
                    cx = float(np.mean(centers)) / W
            else:
                centers = [float(f[0] + f[2] / 2) for f in kept]
                cx = float(np.mean(centers)) / W
        points.append((t, cx))
        n += step
        if n >= total:
            break
    cap.release()
    return points


def build_speaker_at(edl_path: Path, transcript_path: Path, position_map: dict) -> "callable":
    """Build speaker_at(output_time) → 'left' | 'right' | None.

    Walks EDL ranges, maps each transcript word into the output timeline,
    then for any output_time returns the position assigned to the active speaker.
    """
    edl = json.loads(edl_path.read_text())
    tr = json.loads(transcript_path.read_text())
    words = [w for w in tr["words"] if w.get("type") == "word"]

    intervals: list[tuple[float, float, str]] = []  # (out_start, out_end, side)
    out_offset = 0.0
    for r in edl["ranges"]:
        seg_start, seg_end = float(r["start"]), float(r["end"])
        seg_dur = seg_end - seg_start
        for w in words:
            ws, we = w.get("start"), w.get("end")
            if ws is None or we is None:
                continue
            if we <= seg_start or ws >= seg_end:
                continue
            spk = w.get("speaker")
            side = position_map.get(spk)
            if side not in ("left", "right"):
                continue
            local_s = max(seg_start, ws) - seg_start + out_offset
            local_e = min(seg_end, we) - seg_start + out_offset
            intervals.append((local_s, local_e, side))
        out_offset += seg_dur

    intervals.sort()
    starts = [iv[0] for iv in intervals]
    import bisect

    def speaker_at(t: float) -> str | None:
        i = bisect.bisect_right(starts, t) - 1
        if i < 0:
            return None
        s, e, side = intervals[i]
        # Allow brief look-back: if t is between this word and next within 0.4s, keep current side
        if t <= e + 0.4:
            return side
        return None

    return speaker_at


def smooth_track(
    points: list[tuple[float, float | None]],
    window_s: float,
    sample_fps: float,
    max_velocity_norm: float = 0.05,  # max fraction of frame width per second
) -> list[tuple[float, float]]:
    """Smooth the crop trajectory:
      1. No-face frames get target=0.5 (center) — broll center-crops itself
      2. Gaussian filter with sigma = window_s/2 (no boxcar artifacts)
      3. Velocity clamp — crop can't pan faster than max_velocity_norm/s
    """
    # Replace nones with center (so broll segments naturally center-crop, not
    # carry forward a stale host position).
    raw: list[float] = [(0.5 if x is None else x) for _, x in points]
    arr = np.array(raw, dtype=np.float64)

    # Gaussian smoothing — sigma in samples
    sigma_samples = max(1.0, (window_s * sample_fps) / 2.0)
    radius = int(np.ceil(3 * sigma_samples))
    kx = np.arange(-radius, radius + 1)
    kernel = np.exp(-0.5 * (kx / sigma_samples) ** 2)
    kernel /= kernel.sum()
    # Pad edges with edge values so smoothing doesn't pull toward 0
    padded = np.concatenate([np.full(radius, arr[0]), arr, np.full(radius, arr[-1])])
    smoothed = np.convolve(padded, kernel, mode="valid")

    # Velocity clamp — limit per-sample delta
    dt = 1.0 / sample_fps
    max_step = max_velocity_norm * dt
    out = np.empty_like(smoothed)
    out[0] = smoothed[0]
    for i in range(1, len(smoothed)):
        delta = smoothed[i] - out[i - 1]
        if delta > max_step:
            delta = max_step
        elif delta < -max_step:
            delta = -max_step
        out[i] = out[i - 1] + delta

    return [(t, float(s)) for (t, _), s in zip(points, out)]


def write_sendcmd(track: list[tuple[float, float]], scaled_w: int, dst_w: int, out_path: Path) -> None:
    """Write ffmpeg sendcmd file: x is in POST-SCALE coordinates (the frame the crop sees)."""
    max_x = scaled_w - dst_w
    lines = []
    for t, cx_norm in track:
        face_x = cx_norm * scaled_w  # cx_norm was computed as a fraction; same in any coord system
        crop_x = max(0, min(max_x, int(round(face_x - dst_w / 2))))
        lines.append(f"{t:.3f} crop@v x {crop_x};")
    out_path.write_text("\n".join(lines))


def render(input_path: Path, output_path: Path, sendcmd_path: Path, dst_w: int, dst_h: int, src_h: int) -> None:
    crop_y = (src_h - dst_h) // 2 if src_h > dst_h else 0
    if src_h < dst_h:
        # Source not tall enough — scale up first to match dst_h, recompute src_w via scale=-2:dst_h
        scale_filter = f"scale=-2:{dst_h}"
        crop_y_expr = "0"
    else:
        scale_filter = None
        crop_y_expr = str(crop_y)

    sendcmd_arg = str(sendcmd_path).replace(":", r"\:").replace(",", r"\,")
    fc_parts = []
    if scale_filter:
        fc_parts.append(scale_filter)
    fc_parts.append(f"sendcmd=f={sendcmd_arg}")
    fc_parts.append(f"crop@v={dst_w}:{dst_h}:0:{crop_y_expr}")

    fc = ",".join(fc_parts)
    cmd = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-vf", fc,
        "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "copy", "-movflags", "+faststart",
        str(output_path),
    ]
    print(f"  $ ffmpeg ... -vf \"{fc[:80]}...\"")
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    ap.add_argument("--sample-fps", type=float, default=4.0, help="Face detection rate (Hz)")
    ap.add_argument("--smooth", type=float, default=4.0, help="Smoothing window (seconds, Gaussian sigma = window/2)")
    ap.add_argument("--max-velocity", type=float, default=0.05, help="Max pan speed as fraction of frame width per second")
    ap.add_argument("--edl", type=Path, help="Path to EDL JSON (for speaker-aware tracking)")
    ap.add_argument("--transcript", type=Path, help="Path to transcript JSON with word-level speakers")
    ap.add_argument("--speaker-position", type=str, help='JSON map: speaker_id → "left"/"right" e.g. \'{"speaker_2":"left","speaker_0":"right"}\'')
    ap.add_argument("--width", type=int, default=1080)
    ap.add_argument("--height", type=int, default=1920)
    ap.add_argument("--ffmpeg", type=str, default="ffmpeg")
    args = ap.parse_args()

    cap = cv2.VideoCapture(str(args.input))
    src_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    src_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    speaker_at = None
    if args.edl and args.transcript and args.speaker_position:
        pos_map = json.loads(args.speaker_position)
        speaker_at = build_speaker_at(args.edl, args.transcript, pos_map)
        print(f"  speaker-aware: {pos_map}")

    print(f"[1/3] face detection on {args.input.name} (every {1/args.sample_fps:.2f}s)")
    points = detect_track(args.input, args.sample_fps, speaker_at=speaker_at)
    n_with_face = sum(1 for _, x in points if x is not None)
    print(f"  {len(points)} samples, {n_with_face} with faces ({100*n_with_face/max(1,len(points)):.0f}%)")

    print(f"[2/3] smoothing trajectory (window {args.smooth}s)")
    track = smooth_track(points, args.smooth, args.sample_fps, args.max_velocity)

    # The crop runs AFTER scale=-2:dst_h, so compute the post-scale width
    # and use that as the coordinate space for crop_x.
    scaled_w = int(round(src_w * args.height / src_h)) if src_h < args.height else src_w
    if src_h >= args.height:
        scaled_w = src_w
    sendcmd_path = args.output.with_suffix(".sendcmd.txt")
    write_sendcmd(track, scaled_w, args.width, sendcmd_path)

    print(f"[3/3] rendering {args.width}x{args.height} → {args.output.name}")
    # Update ffmpeg call with custom binary
    global_render = render
    if args.ffmpeg != "ffmpeg":
        # monkey-patch the ffmpeg binary into the render function call
        def render_with(input_path, output_path, sendcmd_path, dst_w, dst_h, src_h):
            crop_y = (src_h - dst_h) // 2 if src_h > dst_h else 0
            if src_h < dst_h:
                scale_filter = f"scale=-2:{dst_h}"
                crop_y_expr = "0"
            else:
                scale_filter = None
                crop_y_expr = str(crop_y)
            sendcmd_arg = str(sendcmd_path).replace(":", r"\:").replace(",", r"\,")
            fc_parts = []
            if scale_filter:
                fc_parts.append(scale_filter)
            fc_parts.append(f"sendcmd=f={sendcmd_arg}")
            fc_parts.append(f"crop@v={dst_w}:{dst_h}:0:{crop_y_expr}")
            fc = ",".join(fc_parts)
            cmd = [args.ffmpeg, "-y", "-i", str(input_path), "-vf", fc,
                   "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p",
                   "-c:a", "copy", "-movflags", "+faststart", str(output_path)]
            print(f"  $ {args.ffmpeg} ... -vf \"{fc[:80]}...\"")
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        render_with(args.input, args.output, sendcmd_path, args.width, args.height, src_h)
    else:
        render(args.input, args.output, sendcmd_path, args.width, args.height, src_h)

    print(f"done: {args.output}")


if __name__ == "__main__":
    main()
