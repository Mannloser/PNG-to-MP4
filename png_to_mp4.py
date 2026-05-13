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
import time
import subprocess


# ╔══════════════════════════════════════════════════════════════════╗
# ║                     CONFIGURATION VARIABLES                     ║
# ╚══════════════════════════════════════════════════════════════════╝

CODEC         = "mp4v"
RESIZE_FILTER = cv2.INTER_LANCZOS4

ESRGAN_MODELS = {
    "2": {"label": "2×  — doubles resolution",   "scale": 2, "path": "RealESRGAN_x2plus.pth"},
    "4": {"label": "4×  — quadruples resolution", "scale": 4, "path": "RealESRGAN_x4plus.pth"},
}


# ╔══════════════════════════════════════════════════════════════════╗
# ║                        MENU DEFINITIONS                         ║
# ╚══════════════════════════════════════════════════════════════════╝

RESOLUTIONS = {
    "1": {"label": "720p   HD       1280 × 720",   "size": (1280,  720)},
    "2": {"label": "1080p  Full HD  1920 × 1080",  "size": (1920, 1080)},
    "3": {"label": "1440p  2K QHD   2560 × 1440",  "size": (2560, 1440)},
    "4": {"label": "4K     UHD      3840 × 2160",  "size": (3840, 2160)},
    "5": {"label": "Original  (keep source size)", "size": None},
}

FPS_OPTIONS = {
    "1": 24,
    "2": 25,
    "3": 30,
    "4": 60,
}

BITRATE_PRESETS = {
    "1": {"1": 2_000_000,  "2": 3_500_000,  "3": 5_000_000  },
    "2": {"1": 5_000_000,  "2": 8_000_000,  "3": 10_000_000 },
    "3": {"1": 10_000_000, "2": 15_000_000, "3": 20_000_000 },
    "4": {"1": 35_000_000, "2": 50_000_000, "3": 68_000_000 },
    "5": {"1": 5_000_000,  "2": 8_000_000,  "3": 10_000_000 },
}

BITRATE_LABELS = {
    "1": "Low     smaller file · good for static content",
    "2": "Medium  balanced quality & size",
    "3": "High    best quality · larger file · fast motion",
}


# ╔══════════════════════════════════════════════════════════════════╗
# ║                       TERMINAL STYLING                          ║
# ╚══════════════════════════════════════════════════════════════════╝

class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"

    BLACK   = "\033[30m"
    WHITE   = "\033[97m"
    GRAY    = "\033[90m"

    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"

    BG_BLACK  = "\033[40m"
    BG_BLUE   = "\033[44m"
    BG_CYAN   = "\033[46m"

W = 58   # total width

def clr(text, *codes):
    return "".join(codes) + text + C.RESET

def line(char="─"):
    print(clr("  " + char * (W - 2), C.GRAY))

def blank():
    print()

def header():
    blank()
    print(clr("  ╭" + "─" * (W - 4) + "╮", C.CYAN))
    title = "PNG  →  MP4  CONVERTER"
    pad   = (W - 4 - len(title)) // 2
    print(clr("  │", C.CYAN) +
          " " * pad + clr(title, C.BOLD, C.WHITE) + " " * (W - 4 - pad - len(title)) +
          clr("│", C.CYAN))
    print(clr("  ╰" + "─" * (W - 4) + "╯", C.CYAN))
    blank()

def section(title):
    blank()
    label = f"  ◈  {title}"
    print(clr(label, C.BOLD, C.CYAN))
    line()

def opt(key, label, tag="", ok=True):
    key_str  = clr(f"  [{key}]", C.BOLD, C.YELLOW)
    tag_str  = ("  " + clr(tag, C.GREEN if ok else C.RED, C.DIM)) if tag else ""
    print(f"{key_str}  {label}{tag_str}")

def success(msg):
    print(clr(f"\n  ✦  {msg}", C.GREEN, C.BOLD))

def warn(msg):
    print(clr(f"  ⚠  {msg}", C.YELLOW))

def error(msg):
    print(clr(f"\n  ✖  {msg}", C.RED, C.BOLD))

def info(msg):
    print(clr(f"  ·  {msg}", C.GRAY))

def ask(prompt, valid_keys):
    prompt_str = clr(f"\n  ❯ {prompt} ", C.BOLD, C.WHITE)
    while True:
        choice = input(prompt_str).strip()
        if choice in valid_keys:
            return choice
        warn(f"Enter one of: {', '.join(valid_keys)}")


# ╔══════════════════════════════════════════════════════════════════╗
# ║                        MENU FUNCTIONS                           ║
# ╚══════════════════════════════════════════════════════════════════╝

def pick_folder():
    subfolders = sorted([
        d for d in os.listdir(".")
        if os.path.isdir(d) and glob.glob(os.path.join(d, "*.png"))
    ])

    section("SELECT INPUT FOLDER")

    if not subfolders:
        warn("No PNG folders found in current directory.")
        line()
        while True:
            folder = input(clr("\n  ❯ Folder path: ", C.BOLD, C.WHITE)).strip()
            if os.path.isdir(folder):
                pngs = glob.glob(os.path.join(folder, "*.png"))
                if pngs:
                    success(f"Found {len(pngs)} PNG frames in '{folder}'")
                    return folder
                else:
                    warn(f"No PNG files in: {folder}")
            else:
                warn(f"Folder not found: {folder}")

    for i, folder in enumerate(subfolders, 1):
        count = len(glob.glob(os.path.join(folder, "*.png")))
        count_str = clr(f"{count} frames", C.DIM, C.GRAY)
        opt(str(i), f"{clr(folder + '/', C.WHITE)}  {count_str}")

    manual_key = str(len(subfolders) + 1)
    opt(manual_key, clr("Enter path manually", C.DIM))
    line()

    valid_keys = [str(i) for i in range(1, len(subfolders) + 2)]
    choice = ask("Pick a folder", valid_keys)

    if choice == manual_key:
        while True:
            folder = input(clr("\n  ❯ Folder path: ", C.BOLD, C.WHITE)).strip()
            if os.path.isdir(folder):
                pngs = glob.glob(os.path.join(folder, "*.png"))
                if pngs:
                    success(f"Found {len(pngs)} PNG frames")
                    return folder
                else:
                    warn(f"No PNG files in: {folder}")
            else:
                warn(f"Folder not found: {folder}")
    else:
        return subfolders[int(choice) - 1]


def pick_output_name():
    section("OUTPUT FILE NAME")
    info("Just a name:     my_video")
    info("With a folder:   renders/my_video")
    info("Full path:       D:/Projects/renders/my_video")
    line()

    while True:
        name = input(clr("\n  ❯ Output name (no .mp4): ", C.BOLD, C.WHITE)).strip()
        if not name:
            name = "output"

        output_file = name + ".mp4"
        output_dir  = os.path.dirname(output_file)

        if output_dir and not os.path.exists(output_dir):
            create = input(clr(f"\n  ❯ Create folder '{output_dir}'? [Y/n]: ", C.BOLD, C.WHITE)).strip().lower()
            if create == "n":
                continue
            os.makedirs(output_dir, exist_ok=True)
            success(f"Created folder: {output_dir}")

        if os.path.exists(output_file):
            warn(f"'{output_file}' already exists — choose another name.")
        else:
            success(f"Will save as:  {clr(os.path.abspath(output_file), C.WHITE)}")
            return output_file


def pick_resolution():
    section("OUTPUT RESOLUTION")
    for key, val in RESOLUTIONS.items():
        opt(key, val["label"])
    line()
    return ask("Resolution", RESOLUTIONS.keys())


def pick_fps():
    section("FRAME RATE")
    for key, fps in FPS_OPTIONS.items():
        opt(key, clr(f"{fps} fps", C.WHITE))
    line()
    return ask("FPS", FPS_OPTIONS.keys())


def pick_bitrate(res_key):
    presets = BITRATE_PRESETS[res_key]
    section("BITRATE")
    for key, label in BITRATE_LABELS.items():
        mbps     = presets[key] // 1_000_000
        mbps_str = clr(f"{mbps} Mbps", C.CYAN)
        rec      = clr("  ← recommended", C.DIM, C.GRAY) if key == "2" else ""
        opt(key, f"{label}  {mbps_str}{rec}")
    line()
    return ask("Bitrate", presets.keys())


def pick_upscale():
    section("AI UPSCALING  (Real-ESRGAN)")
    opt("0", clr("No upscaling", C.WHITE))
    for key, val in ESRGAN_MODELS.items():
        found    = os.path.exists(val["path"])
        tag      = "model found" if found else "model not downloaded"
        opt(key, val["label"], tag, found)
    blank()
    info("Models go next to this script.")
    info("Download: github.com/xinntao/Real-ESRGAN/releases")
    line()
    choice = ask("Upscale", ["0", *ESRGAN_MODELS.keys()])
    return None if choice == "0" else ESRGAN_MODELS[choice]


# ╔══════════════════════════════════════════════════════════════════╗
# ║                        UPSCALER LOADER                          ║
# ╚══════════════════════════════════════════════════════════════════╝

def load_upscaler(model_info):
    try:
        from realesrgan import RealESRGANer
        from basicsr.archs.rrdbnet_arch import RRDBNet
    except ImportError:
        error("Real-ESRGAN not installed.")
        info("Run: pip install realesrgan basicsr facexlib gfpgan")
        sys.exit(1)

    if not os.path.exists(model_info["path"]):
        error(f"Model not found: {model_info['path']}")
        info("Download from: github.com/xinntao/Real-ESRGAN/releases")
        sys.exit(1)

    print(clr(f"\n  ◈  Loading Real-ESRGAN {model_info['scale']}× model…", C.CYAN, C.BOLD))
    scale = model_info["scale"]
    model = __import__("basicsr.archs.rrdbnet_arch", fromlist=["RRDBNet"]).RRDBNet(
        num_in_ch=3, num_out_ch=3, num_feat=64,
        num_block=23, num_grow_ch=32, scale=scale
    )
    upsampler = RealESRGANer(
        scale=scale, model_path=model_info["path"],
        model=model, tile=512, tile_pad=10, pre_pad=0, half=False,
    )
    success(f"Model loaded  ({scale}× scale)")
    return upsampler


# ╔══════════════════════════════════════════════════════════════════╗
# ║                      ENCODING SUMMARY                           ║
# ╚══════════════════════════════════════════════════════════════════╝

def print_summary(input_folder, output_file, src_w, src_h,
                  out_w, out_h, fps, bitrate, upscale_info):
    blank()
    print(clr("  ╭" + "─" * (W - 4) + "╮", C.BLUE))
    print(clr("  │", C.BLUE) +
          clr("  ENCODING SUMMARY", C.BOLD, C.WHITE) +
          " " * (W - 22) + clr("│", C.BLUE))
    print(clr("  ├" + "─" * (W - 4) + "┤", C.BLUE))

    rows = [
        ("Input folder", f"{input_folder}/"),
        ("Output file",  os.path.basename(output_file)),
        ("Source res",   f"{src_w} × {src_h}"),
    ]
    if upscale_info:
        rows.append(("AI upscale",
                     f"{src_w * upscale_info['scale']} × {src_h * upscale_info['scale']}"
                     f"  ({upscale_info['scale']}× Real-ESRGAN)"))
    rows += [
        ("Output res",  f"{out_w} × {out_h}"),
        ("Frame rate",  f"{fps} fps"),
        ("Bitrate",     f"{bitrate // 1_000_000} Mbps  ({bitrate:,} bps)"),
        ("Codec",       CODEC + "  →  H.264 via FFmpeg"),
    ]

    for label, value in rows:
        label_str = clr(f"  │  {label:<14}", C.BLUE) + clr("  ", C.RESET)
        value_str = clr(value, C.WHITE)
        pad = W - 4 - 16 - 2 - len(value)
        print(label_str + value_str + " " * max(pad, 0) + clr("  │", C.BLUE))

    print(clr("  ╰" + "─" * (W - 4) + "╯", C.BLUE))

    if upscale_info:
        blank()
        warn("AI upscaling is slow  — ~5–30s per frame on CPU.")
        warn("A CUDA-capable GPU will be much faster.")


# ╔══════════════════════════════════════════════════════════════════╗
# ║                       PROGRESS BAR                              ║
# ╚══════════════════════════════════════════════════════════════════╝

def render_progress(i, total, start_time):
    pct      = i / total
    filled   = int(pct * 28)
    bar      = clr("█" * filled, C.CYAN) + clr("░" * (28 - filled), C.GRAY)
    elapsed  = time.time() - start_time
    eta      = (elapsed / i * (total - i)) if i > 0 else 0
    eta_str  = f"{int(eta // 60):02d}:{int(eta % 60):02d}"
    pct_str  = clr(f"{pct * 100:5.1f}%", C.BOLD, C.WHITE)
    frame_str= clr(f"{i}/{total}", C.GRAY)
    print(f"  {bar}  {pct_str}  {frame_str}  ETA {clr(eta_str, C.YELLOW)}", end="\r")


# ╔══════════════════════════════════════════════════════════════════╗
# ║                         CONVERTER LOGIC                         ║
# ╚══════════════════════════════════════════════════════════════════╝

def png_sequence_to_mp4(input_folder, output_file, out_size, fps, bitrate, upscale_info):

    # ── Collect & sort numerically ────────────────────────────────
    frames = sorted(
        glob.glob(os.path.join(input_folder, "*.png")),
        key=lambda f: int(re.search(r'\d+', os.path.basename(f)).group())
    )

    if not frames:
        error(f"No PNG files found in: {input_folder}")
        sys.exit(1)

    blank()
    print(clr(f"  ◈  {len(frames)} frames detected", C.CYAN, C.BOLD))
    info(f"First  →  {os.path.basename(frames[0])}")
    info(f"Last   →  {os.path.basename(frames[-1])}")

    upsampler = None
    if upscale_info:
        upsampler = load_upscaler(upscale_info)

    first = cv2.imread(frames[0])
    if first is None:
        error(f"Could not read: {frames[0]}")
        sys.exit(1)

    src_h, src_w = first.shape[:2]

    if upscale_info:
        ai_w = src_w * upscale_info["scale"]
        ai_h = src_h * upscale_info["scale"]
        out_w, out_h = out_size if out_size else (ai_w, ai_h)
    else:
        out_w, out_h = out_size if out_size else (src_w, src_h)

    print_summary(input_folder, output_file, src_w, src_h,
                  out_w, out_h, fps, bitrate, upscale_info)

    blank()
    confirm = input(clr("  ❯ Start encoding? [Y/n]: ", C.BOLD, C.WHITE)).strip().lower()
    if confirm == "n":
        print(clr("\n  Cancelled.\n", C.GRAY))
        sys.exit(0)

    # ── VideoWriter setup ─────────────────────────────────────────
    fourcc = cv2.VideoWriter_fourcc(*CODEC)
    out    = cv2.VideoWriter(output_file, fourcc, fps, (out_w, out_h))
    if not out.isOpened():
        error("Could not open VideoWriter. Try CODEC = 'XVID'.")
        sys.exit(1)
    out.set(cv2.VIDEOWRITER_PROP_QUALITY, 100)
    out.set(cv2.CAP_PROP_BITRATE, bitrate)

    # ── Encode ────────────────────────────────────────────────────
    blank()
    print(clr("  ◈  Encoding…", C.CYAN, C.BOLD))
    blank()
    start = time.time()

    for i, path in enumerate(frames, 1):
        frame = cv2.imread(path)
        if frame is None:
            warn(f"Skipping unreadable: {os.path.basename(path)}")
            continue

        if upsampler is not None:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            upscaled, _ = upsampler.enhance(frame_rgb, outscale=upscale_info["scale"])
            frame = cv2.cvtColor(upscaled, cv2.COLOR_RGB2BGR)

        if (frame.shape[1], frame.shape[0]) != (out_w, out_h):
            frame = cv2.resize(frame, (out_w, out_h), interpolation=RESIZE_FILTER)

        out.write(frame)
        render_progress(i, len(frames), start)

    out.release()

    elapsed = time.time() - start
    mins, secs = divmod(int(elapsed), 60)

    # ── Re-encode to H.264 ────────────────────────────────────────
    blank()
    blank()
    print(clr("  ◈  Re-encoding to H.264…", C.CYAN, C.BOLD))
    temp_file = output_file.replace(".mp4", "_temp.mp4")
    os.rename(output_file, temp_file)
    subprocess.run([
        "ffmpeg", "-i", temp_file,
        "-vcodec", "libx264", "-crf", "18",
        "-pix_fmt", "yuv420p", output_file
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.remove(temp_file)

    # ── Done ──────────────────────────────────────────────────────
    blank()
    print(clr("  ╭" + "─" * (W - 4) + "╮", C.GREEN))
    print(clr("  │", C.GREEN) +
          clr("  ✦  RENDER COMPLETE", C.BOLD, C.GREEN) +
          " " * (W - 24) + clr("│", C.GREEN))
    print(clr("  ├" + "─" * (W - 4) + "┤", C.GREEN))
    path_val = os.path.abspath(output_file)
    time_val = f"{mins:02d}m {secs:02d}s"
    for label, value in [("Saved to", path_val), ("Time taken", time_val)]:
        pad = W - 4 - 16 - 2 - len(value)
        print(clr(f"  │  {label:<14}", C.GREEN) +
              clr(f"  {value}", C.WHITE) +
              " " * max(pad, 0) + clr("  │", C.GREEN))
    print(clr("  ╰" + "─" * (W - 4) + "╯", C.GREEN))
    blank()


# ╔══════════════════════════════════════════════════════════════════╗
# ║                            MAIN                                 ║
# ╚══════════════════════════════════════════════════════════════════╝

if __name__ == "__main__":
    header()

    input_folder = pick_folder()
    output_file  = pick_output_name()
    res_key      = pick_resolution()
    fps_key      = pick_fps()
    bit_key      = pick_bitrate(res_key)
    upscale_info = pick_upscale()

    out_size = RESOLUTIONS[res_key]["size"]
    fps      = FPS_OPTIONS[fps_key]
    bitrate  = BITRATE_PRESETS[res_key][bit_key]

    png_sequence_to_mp4(input_folder, output_file, out_size, fps, bitrate, upscale_info)