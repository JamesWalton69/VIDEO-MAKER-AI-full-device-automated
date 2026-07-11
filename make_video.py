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
import glob
import whisper
from pathlib import Path
from tqdm import tqdm
from PIL import Image
from moviepy.editor import (
    ImageClip, AudioFileClip, concatenate_videoclips
)

# ── Folder paths (all relative to this script) ────────────────────────────────
BASE     = Path(__file__).parent
AUDIO_DIR    = BASE / "audio"
IMAGES_DIR   = BASE / "images"
CAPTIONS_DIR = BASE / "captions"
OUTPUT_DIR   = BASE / "output"

# ── Settings ──────────────────────────────────────────────────────────────────
WHISPER_MODEL  = "turbo"       # Options: tiny, base, small, medium, large, turbo
VIDEO_SIZE     = (1920, 1080)  # Output resolution
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


def transcribe_audio(audio_path):
    """Run Whisper on the audio file and save SRT to captions folder."""
    srt_path = CAPTIONS_DIR / (audio_path.stem + ".srt")

    if srt_path.exists():
        print(f"[OK] Found existing SRT: {srt_path.name} — skipping transcription.")
        return srt_path

    print(f"\n[Whisper] Loading model '{WHISPER_MODEL}'... (first run downloads it)")
    model = whisper.load_model(WHISPER_MODEL)

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

    print(f"[OK] SRT saved → {srt_path}")
    return srt_path


def get_sorted_images():
    """Get all images from /images sorted by filename."""
    exts = [".png", ".jpg", ".jpeg", ".webp"]
    files = [
        f for f in sorted(IMAGES_DIR.iterdir())
        if f.suffix.lower() in exts
    ]
    return files


def resize_image(img_path, size):
    """Resize image to fit target size with black bars (letterbox)."""
    img = Image.open(img_path).convert("RGB")
    img.thumbnail(size, Image.LANCZOS)
    canvas = Image.new("RGB", size, (0, 0, 0))
    offset = ((size[0] - img.width) // 2, (size[1] - img.height) // 2)
    canvas.paste(img, offset)
    tmp_path = BASE / "tools" / f"_tmp_{img_path.stem}.jpg"
    canvas.save(tmp_path, "JPEG", quality=95)
    return str(tmp_path)


def build_video(srt_entries, image_files, audio_path):
    """Build final video: each SRT entry maps to one image."""
    total_duration = AudioFileClip(str(audio_path)).duration

    print(f"\n[Video] {len(srt_entries)} captions | {len(image_files)} images")

    if len(image_files) < len(srt_entries):
        print(f"[WARNING] Fewer images ({len(image_files)}) than captions ({len(srt_entries)}).")
        print("          Last image will be reused for remaining captions.")

    clips = []
    tmp_files = []

    for i, (start, end, text) in enumerate(tqdm(srt_entries, desc="Building clips")):
        # Pick image — cycle if fewer images than captions
        img_path = image_files[i % len(image_files)]
        duration = end - start

        if duration <= 0:
            continue

        # Resize image
        tmp = resize_image(img_path, VIDEO_SIZE)
        tmp_files.append(tmp)

        clip = (
            ImageClip(tmp)
            .set_duration(duration)
            .set_start(start)
        )

        if FADE_DURATION > 0 and duration > FADE_DURATION * 2:
            clip = clip.crossfadein(FADE_DURATION)

        clips.append(clip)

    # Handle gap between last caption and end of audio
    if srt_entries and srt_entries[-1][1] < total_duration:
        gap = total_duration - srt_entries[-1][1]
        last_img = image_files[-1]
        tmp = resize_image(last_img, VIDEO_SIZE)
        tmp_files.append(tmp)
        clips.append(
            ImageClip(tmp)
            .set_duration(gap)
            .set_start(srt_entries[-1][1])
        )

    print("\n[Video] Concatenating clips...")
    final = concatenate_videoclips(clips, method="compose")

    print("[Audio] Adding audio...")
    audio = AudioFileClip(str(audio_path))
    final = final.set_audio(audio)

    output_path = OUTPUT_DIR / (audio_path.stem + "_video.mp4")
    print(f"[Render] Rendering → {output_path.name}  (this may take a while...)")
    final.write_videofile(
        str(output_path),
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        logger="bar"
    )

    # Cleanup temp files
    for f in tmp_files:
        try:
            os.remove(f)
        except Exception:
            pass

    print(f"\n✅ Done! Video saved → output/{output_path.name}")
    return output_path


def main():
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
    srt_path = transcribe_audio(audio_path)

    # 4. Parse SRT
    srt_entries = parse_srt(srt_path)
    if not srt_entries:
        print("[ERROR] SRT file is empty or couldn't be parsed.")
        sys.exit(1)
    print(f"[OK] Captions: {len(srt_entries)} segments")

    # 5. Build video
    build_video(srt_entries, image_files, audio_path)


if __name__ == "__main__":
    main()
