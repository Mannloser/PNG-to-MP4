#!/usr/bin/env python3
"""
PNG Sequence → MP4 Converter  (Interactive Mode)
Requires: pip install opencv-python realesrgan basicsr facexlib gfpgan
"""

import cv2
import os
import re
import sys
import glob
import subprocess


# ╔══════════════════════════════════════════════════════════════════╗
# ║                     CONFIGURATION VARIABLES                     ║
# ╚══════════════════════════════════════════════════════════════════╝

CODEC         = "mp4v"           # "mp4v" | "XVID"
RESIZE_FILTER = cv2.INTER_LANCZOS4

# Real-ESRGAN model paths (place .pth files next to this script)
ESRGAN_MODELS = {
    "2": {
        "label": "2x  (doubles resolution)",
        "scale": 2,
        "path":  "RealESRGAN_x2plus.pth",
    },
    "4": {
        "label": "4x  (quadruples resolution)",
        "scale": 4,
        "path":  "RealESRGAN_x4plus.pth",
    },
}


# ╔══════════════════════════════════════════════════════════════════╗
# ║                        MENU DEFINITIONS                         ║
# ╚══════════════════════════════════════════════════════════════════╝

RESOLUTIONS = {
    "1": {"label": "720p  HD      (1280 × 720)",         "size": (1280, 720)},
    "2": {"label": "1080p Full HD (1920 × 1080)",        "size": (1920, 1080)},
    "3": {"label": "1440p 2K QHD  (2560 × 1440)",        "size": (2560, 1440)},
    "4": {"label": "4K    UHD     (3840 × 2160)",        "size": (3840, 2160)},
    "5": {"label": "Original  (keep source resolution)", "size": None},
}

FPS_OPTIONS = {
    "1": 24,
    "2": 25,
    "3": 30,
    "4": 60,
}

BITRATE_PRESETS = {
    "1": {"1": 2_000_000,  "2": 3_500_000,  "3": 5_000_000  },  # 720p
    "2": {"1": 5_000_000,  "2": 8_000_000,  "3": 10_000_000 },  # 1080p
    "3": {"1": 10_000_000, "2": 15_000_000, "3": 20_000_000 },  # 1440p
    "4": {"1": 35_000_000, "2": 50_000_000, "3": 68_000_000 },  # 4K
    "5": {"1": 5_000_000,  "2": 8_000_000,  "3": 10_000_000 },  # Original
}

BITRATE_LABELS = {
    "1": "Low    (smaller file, good for static/slow content)",
    "2": "Medium (balanced quality & size)  ← recommended",
    "3": "High   (best quality, larger file, fast motion)",
}


# ╔══════════════════════════════════════════════════════════════════╗
# ║                        HELPER FUNCTIONS                         ║
# ╚══════════════════════════════════════════════════════════════════╝

def divider():
    print("─" * 52)

def ask(prompt, valid_keys):
    while True:
        choice = input(prompt).strip()
        if choice in valid_keys:
            return choice
        print(f"  ⚠  Invalid choice. Enter one of: {', '.join(valid_keys)}")


def pick_folder():
    subfolders = sorted([
        d for d in os.listdir(".")
        if os.path.isdir(d) and glob.glob(os.path.join(d, "*.png"))
    ])

    divider()
    print("  SELECT PNG SEQUENCE FOLDER")
    divider()

    if not subfolders:
        print("  ⚠  No subfolders with PNG files found in current directory.")
        print("  Enter the folder path manually.")
        divider()
        while True:
            folder = input("  Folder path: ").strip()
            if os.path.isdir(folder):
                pngs = glob.glob(os.path.join(folder, "*.png"))
                if pngs:
                    print(f"  ✔  Found {len(pngs)} PNG(s) in '{folder}'")
                    return folder
                else:
                    print(f"  ⚠  No PNG files found in: {folder}")
            else:
                print(f"  ⚠  Folder not found: {folder}")

    for i, folder in enumerate(subfolders, 1):
        count = len(glob.glob(os.path.join(folder, "*.png")))
        print(f"  [{i}]  {folder}/   ({count} PNG files)")

    manual_key = str(len(subfolders) + 1)
    print(f"  [{manual_key}]  Enter path manually")
    divider()

    valid_keys = [str(i) for i in range(1, len(subfolders) + 2)]
    choice = ask("  Your choice: ", valid_keys)

    if choice == manual_key:
        while True:
            folder = input("  Folder path: ").strip()
            if os.path.isdir(folder):
                pngs = glob.glob(os.path.join(folder, "*.png"))
                if pngs:
                    print(f"  ✔  Found {len(pngs)} PNG(s) in '{folder}'")
                    return folder
                else:
                    print(f"  ⚠  No PNG files found in: {folder}")
            else:
                print(f"  ⚠  Folder not found: {folder}")
    else:
        return subfolders[int(choice) - 1]


def pick_output_name():
    divider()
    print("  OUTPUT FILE NAME")
    divider()
    while True:
        name = input("  Enter output name (without .mp4): ").strip()
        if not name:
            name = "output"
        output_file = name + ".mp4"
        if os.path.exists(output_file):
            print(f"  ⚠  '{output_file}' already exists! Choose a different name.")
        else:
            print(f"  ✔  Will save as: {output_file}")
            return output_file


def pick_resolution():
    divider()
    print("  SELECT OUTPUT RESOLUTION")
    divider()
    for key, val in RESOLUTIONS.items():
        print(f"  [{key}]  {val['label']}")
    divider()
    return ask("  Your choice: ", RESOLUTIONS.keys())

def pick_fps():
    divider()
    print("  SELECT FRAME RATE (FPS)")
    divider()
    for key, fps in FPS_OPTIONS.items():
        print(f"  [{key}]  {fps} FPS")
    divider()
    return ask("  Your choice: ", FPS_OPTIONS.keys())

def pick_bitrate(res_key):
    presets = BITRATE_PRESETS[res_key]
    divider()
    print("  SELECT BITRATE")
    divider()
    for key, label in BITRATE_LABELS.items():
        mbps = presets[key] // 1_000_000
        print(f"  [{key}]  {label}  →  {mbps} Mbps")
    divider()
    return ask("  Your choice: ", presets.keys())


def pick_upscale():
    divider()
    print("  AI UPSCALING  (Real-ESRGAN)")
    divider()
    print("  [0]  No upscaling  (use selected output resolution as-is)")
    for key, val in ESRGAN_MODELS.items():
        model_found = "✔ model found" if os.path.exists(val["path"]) else "⚠ model not downloaded"
        print(f"  [{key}]  {val['label']}   [{model_found}]")
    divider()
    print("  ℹ  Models must be placed next to this script.")
    print("  ℹ  Download: https://github.com/xinntao/Real-ESRGAN/releases")
    divider()
    choice = ask("  Your choice: ", ["0", *ESRGAN_MODELS.keys()])
    return None if choice == "0" else ESRGAN_MODELS[choice]


def load_upscaler(model_info):
    """Load Real-ESRGAN model. Returns upsampler or exits on failure."""
    try:
        from realesrgan import RealESRGANer
        from basicsr.archs.rrdbnet_arch import RRDBNet
    except ImportError:
        print("\n  [ERROR] Real-ESRGAN not installed.")
        print("  Run: pip install realesrgan basicsr facexlib gfpgan\n")
        sys.exit(1)

    model_path = model_info["path"]
    scale      = model_info["scale"]

    if not os.path.exists(model_path):
        print(f"\n  [ERROR] Model file not found: {model_path}")
        print(f"  Download it from: https://github.com/xinntao/Real-ESRGAN/releases")
        print(f"  and place it next to this script.\n")
        sys.exit(1)

    print(f"\n  🤖  Loading Real-ESRGAN {scale}x model...")

    model = RRDBNet(
        num_in_ch=3, num_out_ch=3,
        num_feat=64, num_block=23,
        num_grow_ch=32, scale=scale
    )

    upsampler = RealESRGANer(
        scale=scale,
        model_path=model_path,
        model=model,
        tile=512,        # tile size — lower if you get out-of-memory errors
        tile_pad=10,
        pre_pad=0,
        half=False,      # set True if you have a modern NVIDIA GPU (faster)
    )

    print(f"  ✔  Model loaded  (scale={scale}x)\n")
    return upsampler


# ╔══════════════════════════════════════════════════════════════════╗
# ║                         CONVERTER LOGIC                         ║
# ╚══════════════════════════════════════════════════════════════════╝

def png_sequence_to_mp4(input_folder, output_file, out_size, fps, bitrate, upscale_info):

    # ── Collect & sort PNG files NUMERICALLY ─────────────────────
    frames = sorted(
        glob.glob(os.path.join(input_folder, "*.png")),
        key=lambda f: int(re.search(r'\d+', os.path.basename(f)).group())
    )

    if not frames:
        print(f"\n[ERROR] No PNG files found in: {input_folder}")
        sys.exit(1)

    print(f"\n[INFO] Found {len(frames)} PNG frame(s)")
    print(f"[INFO] First frame: {os.path.basename(frames[0])}")
    print(f"[INFO] Last frame : {os.path.basename(frames[-1])}")

    # ── Load upscaler if requested ────────────────────────────────
    upsampler = None
    if upscale_info:
        upsampler = load_upscaler(upscale_info)

    # ── Read first frame to get source size ──────────────────────
    first = cv2.imread(frames[0])
    if first is None:
        print(f"[ERROR] Could not read: {frames[0]}")
        sys.exit(1)

    src_h, src_w = first.shape[:2]

    # Work out what the actual output size will be
    if upscale_info:
        ai_w = src_w * upscale_info["scale"]
        ai_h = src_h * upscale_info["scale"]
        # If user also picked a target resolution, use that; otherwise use AI output size
        out_w, out_h = out_size if out_size else (ai_w, ai_h)
    else:
        out_w, out_h = out_size if out_size else (src_w, src_h)

    # ── Summary ───────────────────────────────────────────────────
    divider()
    print(f"  Input folder  : {input_folder}/")
    print(f"  Output file   : {output_file}")
    print(f"  Source res    : {src_w} x {src_h}")
    if upscale_info:
        ai_w = src_w * upscale_info["scale"]
        ai_h = src_h * upscale_info["scale"]
        print(f"  After AI upsc : {ai_w} x {ai_h}  ({upscale_info['scale']}x Real-ESRGAN)")
    print(f"  Output res    : {out_w} x {out_h}")
    print(f"  FPS           : {fps}")
    print(f"  Bitrate       : {bitrate // 1_000_000} Mbps  ({bitrate:,} bps)")
    print(f"  Codec         : {CODEC}  →  H.264 (via FFmpeg)")
    if upscale_info:
        print(f"\n  ⚠  AI upscaling is slow — expect ~5–30s per frame on CPU.")
        print(f"  ⚠  GPU with CUDA will be much faster.")
    divider()

    confirm = input("  Start encoding? [Y/n]: ").strip().lower()
    if confirm == "n":
        print("  Cancelled.")
        sys.exit(0)

    # ── Set up VideoWriter ────────────────────────────────────────
    fourcc = cv2.VideoWriter_fourcc(*CODEC)
    out    = cv2.VideoWriter(output_file, fourcc, fps, (out_w, out_h))

    if not out.isOpened():
        print("[ERROR] Could not open VideoWriter. Try changing CODEC to XVID.")
        sys.exit(1)

    out.set(cv2.VIDEOWRITER_PROP_QUALITY, 100)
    out.set(cv2.CAP_PROP_BITRATE, bitrate)

    # ── Write frames ──────────────────────────────────────────────
    print()
    for i, path in enumerate(frames, 1):
        frame = cv2.imread(path)
        if frame is None:
            print(f"[WARNING] Skipping unreadable file: {path}")
            continue

        # AI upscale
        if upsampler is not None:
            import numpy as np
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            upscaled, _ = upsampler.enhance(frame_rgb, outscale=upscale_info["scale"])
            frame = cv2.cvtColor(upscaled, cv2.COLOR_RGB2BGR)

        # Resize to target output resolution if needed
        if (frame.shape[1], frame.shape[0]) != (out_w, out_h):
            frame = cv2.resize(frame, (out_w, out_h), interpolation=RESIZE_FILTER)

        out.write(frame)

        if i % 10 == 0 or i == len(frames):
            pct = (i / len(frames)) * 100
            bar = ("█" * int(pct // 5)).ljust(20)
            print(f"  [{bar}] {pct:5.1f}%  ({i}/{len(frames)} frames)", end="\r")

    out.release()

    # ── Re-encode to H.264 via FFmpeg (mobile compatible) ────────
    print(f"\n\n  🔄  Re-encoding to H.264 for mobile compatibility...")
    temp_file = output_file.replace(".mp4", "_temp.mp4")
    os.rename(output_file, temp_file)
    subprocess.run([
        "ffmpeg", "-i", temp_file,
        "-vcodec", "libx264",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        output_file
    ], check=True)
    os.remove(temp_file)

    print(f"\n  ✅  Done!  →  {os.path.abspath(output_file)}\n")


# ╔══════════════════════════════════════════════════════════════════╗
# ║                            MAIN                                 ║
# ╚══════════════════════════════════════════════════════════════════╝

if __name__ == "__main__":
    print("\n  ╔══════════════════════════════════════╗")
    print("  ║      PNG SEQUENCE → MP4 CONVERTER    ║")
    print("  ╚══════════════════════════════════════╝")

    input_folder  = pick_folder()
    output_file   = pick_output_name()
    res_key       = pick_resolution()
    fps_key       = pick_fps()
    bit_key       = pick_bitrate(res_key)
    upscale_info  = pick_upscale()

    out_size = RESOLUTIONS[res_key]["size"]
    fps      = FPS_OPTIONS[fps_key]
    bitrate  = BITRATE_PRESETS[res_key][bit_key]

    png_sequence_to_mp4(input_folder, output_file, out_size, fps, bitrate, upscale_info)
