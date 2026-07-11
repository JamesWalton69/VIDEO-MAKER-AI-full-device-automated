# ⚙️ Customizing the VideoMaker Rendering Engine

You can easily customize various settings of the video rendering engine to fit your needs, such as changing resolutions for YouTube Shorts vs. landscape videos, tweaking transitions, using different Whisper models, or enabling hardware acceleration.

All configuration variables are defined at the top of **[`make_video.py`](file:///e:/Python%20Programs/Vdo%20maker%20AI/make_video.py)**.

---

## 📌 Configurable Settings

### 1. Whisper Model (`WHISPER_MODEL`)
Controls the transcription speed and accuracy.
```python
WHISPER_MODEL = "turbo"
```
**Available options:**
* `"tiny"`: Fastest speed, lowest VRAM usage, lowest accuracy.
* `"base"`: Fast, low VRAM, basic accuracy.
* `"small"`: Good balance of speed and accuracy.
* `"medium"`: Highly accurate, slower, requires ~5GB VRAM.
* `"large"`: Best accuracy, very slow, requires ~10GB VRAM.
* `"turbo"`: *(Default)* Optimized speed-accuracy trade-off.

---

### 2. Video Resolution (`VIDEO_SIZE`)
Sets the output dimensions of the final MP4 video.
```python
VIDEO_SIZE = (1920, 1080)
```
* **Landscape (16:9 YouTube/Vimeo)**: `(1920, 1080)`
* **Vertical (9:16 Shorts/Reels/TikTok)**: `(1080, 1920)`
* **Square (1:1 Instagram)**: `(1080, 1080)`

---

### 3. Frame Rate (`FPS`)
Defines the smoothness of the video.
```python
FPS = 24
```
* `24` or `30` is recommended for standard slide-based automated videos.
* Increase to `60` only if you have high-frequency animations, though it will double the render time.

---

### 4. Crossfade Transition (`FADE_DURATION`)
Configures the duration (in seconds) of the crossfade transition between sequential images.
```python
FADE_DURATION = 0.3
```
* Set to `0.3` (default) for a smooth 0.3-second fade transition.
* Set to `0` to disable transitions completely (jump cuts).

---

### 5. CPU Rendering Cores (`--threads`)
Configures the number of CPU threads/cores utilized during video encoding.
* **Auto (Default / `0`)**: Automatically detects your CPU cores and uses all of them minus one (e.g. if you have 8 cores, it uses 7) to keep your computer responsive.
* **Custom Limit**: You can set a custom number (e.g., `4`, `8`) via `START.bat` option **[4]** or command line argument `--threads <count>`.

---

## 🖌️ Burnt-in Subtitle Customization

Subtitles are rendered directly on the images using Pillow. You can customize the look in the `draw_subtitles` function of `make_video.py`:

* **Font Size**: Change the `font_size` parameter (default is `42`).
* **Position**: Adjust the `bottom_padding` (default is `80`) to change how high the text sits.
* **Colors & Outline**:
  - Outlines are drawn in black (`stroke_fill=(0, 0, 0)`) with a thickness of `4` (`stroke_width=4`).
  - Text fill is white (`fill=(255, 255, 255)`).
  - To change styling, edit the drawing call:
    ```python
    draw.text((x, y), line, font=font, fill=(255, 255, 255), 
              stroke_width=4, stroke_fill=(0, 0, 0))
    ```

---

## 🛠️ Advanced Code Customizations

### Background Padding Color
When images do not match the target video aspect ratio, the engine adds black letterbox/pillarbox bars. You can change this color in the `resize_image` function in `make_video.py`:
```python
# Change the (0, 0, 0) RGB tuple to choose a different background color
canvas = Image.new("RGB", size, (0, 0, 0))
```

### Video Codec & Hardware Acceleration
By default, the engine uses the standard CPU-based `libx264` encoder. If you have a dedicated graphics card, you can modify `final.write_videofile` in `make_video.py` to use GPU-accelerated encoding:
* **NVIDIA GPUs**: Change `codec="libx264"` to `codec="h264_nvenc"`.
* **Intel QuickSync**: Change to `codec="h264_qsv"`.
* **Apple Silicon**: Change to `codec="h264_videotoolbox"`.
