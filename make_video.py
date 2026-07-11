"""
VideoMaker - Auto Video Generator
----------------------------------
1. Reads audio from /audio folder
2. Uses Whisper to auto-generate SRT captions with timestamps
3. Matches each caption to a numbered image in /images folder
4. Renders final video synced to audio → saved in /output folder
"""

import os
import sys
import argparse
import platform
from pathlib import Path
from tqdm import tqdm
from PIL import Image, ImageDraw, ImageFont
import whisper
from moviepy import (
    ImageClip, AudioFileClip, concatenate_videoclips, vfx
)

# ── Folder paths (all relative to this script) ────────────────────────────────
BASE         = Path(__file__).parent
AUDIO_DIR    = BASE / "audio"
IMAGES_DIR   = BASE / "images"
CAPTIONS_DIR = BASE / "captions"
OUTPUT_DIR   = BASE / "output"

# Add local tools directory to PATH so FFmpeg is always found
tools_dir = str(BASE / "tools")
os.environ["PATH"] = tools_dir + os.pathsep + os.environ["PATH"]

# ── Default Settings ──────────────────────────────────────────────────────────
WHISPER_MODEL  = "turbo"       # Options: tiny, base, small, medium, large, turbo
VIDEO_SIZE     = (1920, 1080)  # Output resolution (Width, Height)
FPS            = 24
FADE_DURATION  = 0.3           # Seconds of crossfade between images (0 = none)

# ──────────────────────────────────────────────────────────────────────────────

def find_audio_file():
    """Find the first audio file in the audio folder."""
    for ext in ["*.mp3", "*.wav", "*.m4a", "*.aac", "*.flac", "*.ogg"]:
        files = list(AUDIO_DIR.glob(ext))
        if files:
            return files[0]
    return None


def parse_srt_time(t):
    """Convert SRT timestamp string to seconds."""
    h, m, rest = t.strip().split(":")
    s, ms = rest.replace(",", ".").split(".")
    return int(h)*3600 + int(m)*60 + int(s) + float("0." + ms)


def parse_srt(srt_path):
    """Parse SRT file into list of (start, end, text) tuples."""
    entries = []
    with open(srt_path, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = content.strip().split("\n\n")
    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) < 3:
            continue
        try:
            times = lines[1].split(" --> ")
            start = parse_srt_time(times[0])
            end   = parse_srt_time(times[1])
            text  = " ".join(lines[2:]).strip()
            entries.append((start, end, text))
        except Exception:
            continue
    return entries


def transcribe_audio(audio_path, model_name=WHISPER_MODEL):
    """Run Whisper on the audio file and save SRT to captions folder."""
    srt_path = CAPTIONS_DIR / (audio_path.stem + ".srt")

    if srt_path.exists():
        print(f"[OK] Found existing SRT: {srt_path.name} — skipping transcription.")
        return srt_path

    print(f"\n[Whisper] Loading model '{model_name}'... (first run downloads it)")
    model = whisper.load_model(model_name)

    print(f"[Whisper] Transcribing: {audio_path.name}")
    result = model.transcribe(str(audio_path), word_timestamps=False)

    # Write SRT
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(result["segments"], 1):
            start = seg["start"]
            end   = seg["end"]
            text  = seg["text"].strip()

            def fmt(s):
                h = int(s // 3600)
                m = int((s % 3600) // 60)
                sec = int(s % 60)
                ms = int(round((s - int(s)) * 1000))
                return f"{h:02}:{m:02}:{sec:02},{ms:03}"

            f.write(f"{i}\n{fmt(start)} --> {fmt(end)}\n{text}\n\n")

    print(f"[OK] SRT saved -> {srt_path}")
    return srt_path


def get_sorted_images():
    """Get all images from /images sorted by filename."""
    exts = [".png", ".jpg", ".jpeg", ".webp"]
    files = [
        f for f in sorted(IMAGES_DIR.iterdir())
        if f.suffix.lower() in exts
    ]
    return files


def wrap_text(text, font, max_width):
    """Wrap text to fit within max_width pixels using PIL font."""
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = " ".join(current_line + [word])
        try:
            bbox = font.getbbox(test_line)
            w = bbox[2] - bbox[0]
        except AttributeError:
            w, h = font.getsize(test_line)
            
        if w <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
            
    if current_line:
        lines.append(" ".join(current_line))
    return lines


def draw_subtitles(canvas, text, font_size=42, bottom_padding=80):
    """Draw subtitles onto the PIL canvas with outline stroke."""
    draw = ImageDraw.Draw(canvas)
    
    # Choose standard font based on platform
    font_path = "arial.ttf"
    if platform.system() == "Windows":
        font_path = r"C:\Windows\Fonts\arial.ttf"
    elif platform.system() == "Darwin":
        font_path = "/Library/Fonts/Arial.ttf"
    else:
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        
    try:
        font = ImageFont.truetype(font_path, font_size)
    except Exception:
        try:
            # Fallback to standard arial
            font = ImageFont.truetype("arial.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()
            
    # Wrap text to fit screen width (leave 120px margin on sides)
    max_text_width = canvas.width - 240
    lines = wrap_text(text, font, max_text_width)
    
    # Calculate text heights and coordinates
    line_heights = []
    for line in lines:
        try:
            bbox = font.getbbox(line)
            line_heights.append(bbox[3] - bbox[1])
        except AttributeError:
            _, h = font.getsize(line)
            line_heights.append(h)
            
    total_text_height = sum(line_heights) + (12 * (len(lines) - 1))
    y = canvas.height - bottom_padding - total_text_height
    
    for line in lines:
        try:
            bbox = font.getbbox(line)
            line_w = bbox[2] - bbox[0]
            line_h = bbox[3] - bbox[1]
        except AttributeError:
            line_w, line_h = font.getsize(line)
            
        x = (canvas.width - line_w) // 2
        
        # Draw text with 4px black outline (native in newer PIL versions)
        try:
            draw.text((x, y), line, font=font, fill=(255, 255, 255), 
                      stroke_width=4, stroke_fill=(0, 0, 0))
        except Exception:
            # Manual outline fallback
            for dx in [-2, 0, 2]:
                for dy in [-2, 0, 2]:
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0))
            draw.text((x, y), line, font=font, fill=(255, 255, 255))
            
        y += line_h + 12


def resize_image(img_path, size, subtitle_text=None):
    """Resize image to fit target size with letterboxing, and optionally draw subtitles."""
    img = Image.open(img_path).convert("RGB")
    img.thumbnail(size, Image.LANCZOS)
    canvas = Image.new("RGB", size, (0, 0, 0))
    offset = ((size[0] - img.width) // 2, (size[1] - img.height) // 2)
    canvas.paste(img, offset)
    
    if subtitle_text:
        draw_subtitles(canvas, subtitle_text)
        
    tmp_path = BASE / "tools" / f"_tmp_{img_path.stem}.jpg"
    canvas.save(tmp_path, "JPEG", quality=95)
    return str(tmp_path)


def build_video(srt_entries, image_files, audio_path, show_subtitles=True, use_zoom=False, video_size=VIDEO_SIZE, fps=FPS, num_threads=0):
    """Build final video: each SRT entry maps to one image."""
    total_duration = AudioFileClip(str(audio_path)).duration

    print(f"\n[Video] {len(srt_entries)} captions | {len(image_files)} images")
    print(f"[Video] Subtitles: {'ENABLED' if show_subtitles else 'DISABLED'}")
    print(f"[Video] Pan & Zoom (Ken Burns): {'ENABLED' if use_zoom else 'DISABLED'}")

    if len(image_files) < len(srt_entries):
        print(f"[WARNING] Fewer images ({len(image_files)}) than captions ({len(srt_entries)}).")
        print("          Last image will be reused for remaining captions.")

    clips = []
    tmp_files = []

    for i, (start, end, text) in enumerate(tqdm(srt_entries, desc="Building clips")):
        img_path = image_files[i % len(image_files)]
        duration = end - start

        if duration <= 0:
            continue

        # Resize image, burn subtitle text if enabled
        sub_text = text if show_subtitles else None
        tmp = resize_image(img_path, video_size, subtitle_text=sub_text)
        tmp_files.append(tmp)

        clip = (
            ImageClip(tmp)
            .with_duration(duration)
            .with_start(start)
        )

        # Apply Zoom transition if enabled
        if use_zoom:
            # Subtle zoom-in from 1.0 to 1.07 over the clip's duration
            clip = clip.resized(lambda t, d=duration: 1.0 + 0.07 * (t / d))

        if FADE_DURATION > 0 and duration > FADE_DURATION * 2:
            clip = clip.with_effects([vfx.CrossFadeIn(FADE_DURATION)])

        clips.append(clip)

    # Handle gap between last caption and end of audio
    if srt_entries and srt_entries[-1][1] < total_duration:
        gap = total_duration - srt_entries[-1][1]
        last_img = image_files[-1]
        
        # No subtitle text on the outro gap
        tmp = resize_image(last_img, video_size, subtitle_text=None)
        tmp_files.append(tmp)
        
        clip = (
            ImageClip(tmp)
            .with_duration(gap)
            .with_start(srt_entries[-1][1])
        )
        if use_zoom:
            clip = clip.resized(lambda t, d=gap: 1.0 + 0.07 * (t / d))
            
        clips.append(clip)

    print("\n[Video] Concatenating clips...")
    final = concatenate_videoclips(clips, method="compose")

    print("[Audio] Adding audio...")
    audio = AudioFileClip(str(audio_path))
    final = final.with_audio(audio)

    output_path = OUTPUT_DIR / (audio_path.stem + "_video.mp4")
    import multiprocessing
    cpu_cores = multiprocessing.cpu_count()
    if num_threads > 0:
        render_threads = min(num_threads, cpu_cores)
    else:
        render_threads = max(1, cpu_cores - 1)
    
    print(f"[Render] Rendering -> {output_path.name} (Using {render_threads} CPU threads)")
    final.write_videofile(
        str(output_path),
        fps=fps,
        codec="libx264",
        audio_codec="aac",
        threads=render_threads,
        logger="bar"
    )

    # Cleanup temp files
    for f in tmp_files:
        try:
            os.remove(f)
        except Exception:
            pass

    print(f"\n[SUCCESS] Done! Video saved -> output/{output_path.name}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="VideoMaker AI - Render Engine")
    parser.add_argument("--subtitles", action="store_true", default=False, help="Burn subtitles onto the video")
    parser.add_argument("--no-subtitles", action="store_false", dest="subtitles", help="Do not burn subtitles")
    parser.set_defaults(subtitles=True) # Default is subtitles enabled
    
    parser.add_argument("--zoom", action="store_true", default=False, help="Apply Ken Burns zoom transitions")
    parser.add_argument("--no-zoom", action="store_false", dest="zoom", help="Do not apply zoom transitions")
    
    parser.add_argument("--resolution", type=str, default="1920x1080", help="Output resolution (e.g. 1920x1080 or 1080x1920)")
    parser.add_argument("--model", type=str, default=WHISPER_MODEL, help="Whisper model to use")
    parser.add_argument("--threads", type=int, default=0, help="Number of CPU threads for rendering (0 = auto)")
    
    args = parser.parse_args()

    # Parse resolution
    try:
        width, height = map(int, args.resolution.lower().split("x"))
        video_size = (width, height)
    except Exception:
        print(f"[WARNING] Invalid resolution format '{args.resolution}'. Using default 1920x1080.")
        video_size = VIDEO_SIZE

    # 1. Find audio
    audio_path = find_audio_file()
    if not audio_path:
        print("[ERROR] No audio file found in the 'audio' folder.")
        print("        Supported formats: mp3, wav, m4a, aac, flac, ogg")
        sys.exit(1)
    print(f"[OK] Audio: {audio_path.name}")

    # 2. Find images
    image_files = get_sorted_images()
    if not image_files:
        print("[ERROR] No images found in the 'images' folder.")
        print("        Supported formats: png, jpg, jpeg, webp")
        sys.exit(1)
    print(f"[OK] Images: {len(image_files)} found")

    # 3. Transcribe with Whisper → SRT
    srt_path = transcribe_audio(audio_path, model_name=args.model)

    # 4. Parse SRT
    srt_entries = parse_srt(srt_path)
    if not srt_entries:
        print("[ERROR] SRT file is empty or couldn't be parsed.")
        sys.exit(1)
    print(f"[OK] Captions: {len(srt_entries)} segments")

    # 5. Build video
    build_video(
        srt_entries=srt_entries, 
        image_files=image_files, 
        audio_path=audio_path,
        show_subtitles=args.subtitles,
        use_zoom=args.zoom,
        video_size=video_size,
        fps=FPS,
        num_threads=args.threads
    )


if __name__ == "__main__":
    main()
