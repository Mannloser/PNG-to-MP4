# 🎬 PNG → MP4 Converter

A beautiful, interactive terminal tool to convert PNG image sequences into MP4 videos.
Built for VFX artists, 3D animators, and anyone rendering out frame-by-frame sequences from tools like Blender, After Effects, or DaVinci Resolve.

---

## ✦ What It Does

When you render an animation in Blender (or any 3D/VFX software), you get hundreds of individual PNG frames instead of one video file. This script takes all those frames and stitches them into a proper `.mp4` video — with full control over resolution, frame rate, bitrate, and even AI upscaling.

Everything runs through a clean, color-coded interactive terminal menu. No command-line flags to memorize, no config files to edit.

**Features at a glance:**

- Auto-detects PNG folders in your project directory
- Numerical frame sorting — no more choppy playback from wrong order
- Resolution presets: 720p, 1080p, 1440p, 4K, or keep original
- FPS options: 24, 25, 30, 60
- Bitrate control: Low / Medium / High presets per resolution
- Optional AI upscaling via Real-ESRGAN (2× or 4×)
- Custom output file naming with overwrite protection
- Live progress bar with ETA while encoding
- Re-encodes to H.264 via FFmpeg for maximum compatibility
- Beautiful color-coded terminal output throughout

---

## ✦ Requirements

### Python

Python 3.8 or higher.
Download from [python.org](https://www.python.org/downloads/) if you don't have it.

### Core dependency

```bash
pip install opencv-python
```

### For AI upscaling (optional)

Only needed if you want to use the Real-ESRGAN upscaling feature:

```bash
pip install realesrgan basicsr facexlib gfpgan
```

### FFmpeg

Required for the final H.264 re-encode step.

- **Windows** — Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add it to your system PATH
- **macOS** — `brew install ffmpeg`
- **Linux** — `sudo apt install ffmpeg`

To check if FFmpeg is already installed:

```bash
ffmpeg -version
```

---

## ✦ Folder Structure

Place the script inside your project folder:

```
PNG TO MP4/
├── PngSeq/                 ← put your PNG sequence here for faster processing
└── png_to_mp4.py           ← this script
```

> **Tip:** Place your PNG sequence inside the `PngSeq` folder before running the script. It seems to process faster this way — not entirely sure why, but it works, so it's recommended!

> The script auto-scans your current directory and lists only folders that contain PNG files. No need to hardcode paths.

---

## ✦ How to Use

### 1. Open a terminal in your project folder

**VS Code** → open the project, then press `` Ctrl + ` `` to open the integrated terminal.

**Windows Explorer** → click the address bar, type `cmd`, press Enter.

### 2. Run the script

```bash
python png_to_mp4.py
```

### 3. Follow the interactive menus

The script walks you through everything step by step:

---

**Step 1 — Select your PNG folder**

```
  ◈  SELECT INPUT FOLDER
  ──────────────────────────────────────────────────────
  [1]  PngSeq/    (shows total no. of frames)
  [2]  Enter path manually
```

Pick the folder that contains your PNG sequence. If your folder is somewhere else on disk, pick `Enter path manually` and type the full path.

---

**Step 2 — Name your output file**

```
  ◈  OUTPUT FILE NAME
  ──────────────────────────────────────────────────────
  · Just a name:     eg., my_video
  · With a folder:   eg., renders/my_video
  · Full path:       eg., C:/Desktop/my_video

  ❯ Output name (without .mp4): my_video
  ✦  Will save as: my_video.mp4
```

If a file with that name already exists, it will warn you and ask for a different name. No accidental overwrites.

- If you type just a name (e.g. `my_video`), the file will be saved in your current directory.
- If you type a name with a folder (e.g. `renders/my_video`), it will create a `renders` subfolder inside your current directory and save the file there.
- If you type a full path (e.g. `C:/Users/YourName/Videos/my_video`), the file will be saved at that exact location.

---

**Step 3 — Pick resolution**

```
  ◈  OUTPUT RESOLUTION
  ──────────────────────────────────────────────────────
  [1]  720p   HD       1280 × 720
  [2]  1080p  Full HD  1920 × 1080
  [3]  1440p  2K QHD   2560 × 1440
  [4]  4K     UHD      3840 × 2160
  [5]  Original  (keep source size)
```

If you pick a higher resolution than your source frames, they will be upscaled using Lanczos interpolation. For AI-quality upscaling, see Step 6.

---

**Step 4 — Pick frame rate**

```
  ◈  FRAME RATE
  ──────────────────────────────────────────────────────
  [1]  24 fps
  [2]  25 fps
  [3]  30 fps
  [4]  60 fps
```

Match this to whatever you set in Blender (or your render software) when you exported the frames.

---

**Step 5 — Pick bitrate**

```
  ◈  BITRATE
  ──────────────────────────────────────────────────────
  [1]  Low     smaller file · good for static content   2 Mbps
  [2]  Medium  balanced quality & size                  8 Mbps  ← recommended
  [3]  High    best quality · larger file · fast motion 10 Mbps
```

Medium is recommended for most use cases — it gets the job done without bloating the file size.

---

**Step 6 — AI Upscaling (optional)**

```
  ◈  AI UPSCALING  (Real-ESRGAN)
  ──────────────────────────────────────────────────────
  [0]  No upscaling
  [2]  2× — doubles resolution     [⚠ model not downloaded]
  [4]  4× — quadruples resolution  [⚠ model not downloaded]
```

To use AI upscaling:

1. Install the packages: `pip install realesrgan basicsr facexlib gfpgan`
2. Download the model `.pth` files from the [Real-ESRGAN releases page](https://github.com/xinntao/Real-ESRGAN/releases):
   - `RealESRGAN_x2plus.pth` for 2×
   - `RealESRGAN_x4plus.pth` for 4×
3. Place the `.pth` files in the same folder as `png_to_mp4.py`

Once models are present, the menu will show `✔ model found` next to each option.

> ⚠ AI upscaling runs on CPU by default and can take 5–30 seconds per frame. If you have an NVIDIA GPU, set `half=True` in the script for much faster processing.

---

**Step 7 — Confirm and encode**

The script shows a full summary before starting:

```
  ╭──────────────────────────────────────────────────────╮
  │  ENCODING SUMMARY                                    │
  ├──────────────────────────────────────────────────────┤
  │  Input folder    (input folder)                      │
  │  Output file     (output folder)                     │
  │  Source res      (source res)                        │
  │  Output res      (output res)                        │
  │  Frame rate      (fps)                               │
  │  Bitrate         (bitrate)                           │
  │  Codec           (codec)                             │
  ╰──────────────────────────────────────────────────────╯

  ❯ Start encoding? [Y/n]:
```

Press Enter (or `Y`) to start. A live progress bar will show while encoding:

When done:

```
  ╭──────────────────────────────────────────────────────╮
  │  ✦  RENDER COMPLETE                                  │
  ├──────────────────────────────────────────────────────┤
  │  Saved to        (output path)                       │
  │  Time taken      (time)                              │
  ╰──────────────────────────────────────────────────────╯
```

---

## ✦ Common Issues

**Choppy or out-of-order video**
Your frame filenames may not have zero-padded numbers (e.g. `frame-1` instead of `frame-001`). The script sorts numerically so it handles this correctly — but double-check your first and last frame names shown before encoding starts.

**`ffmpeg` not found error**
FFmpeg is not installed or not in your PATH. Install it from [ffmpeg.org](https://ffmpeg.org/download.html) and restart your terminal.

**VideoWriter won't open**
Try changing `CODEC = "mp4v"` to `CODEC = "XVID"` at the top of the script.

**AI upscaling out of memory**
Lower the `tile=512` value inside `load_upscaler()` in the script to something like `tile=256`.


**Any other issue**
Contact me on instagram - [@mannloser](https://www.instagram.com/mannloser) or
Email - [mannsakuratv](mailto:mannsakuratv@gmail.com)