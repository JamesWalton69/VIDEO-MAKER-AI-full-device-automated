"""
Forced Alignment Script
------------------------
Reads:  audio\yourfile.mp3   (your audio)
        audio\script.txt     (your captions, one per line)

Outputs:
        captions\aligned.srt  (your exact captions with correct timestamps)
        captions\prompts.txt  (same captions as prompts for Google Flow)
"""

import sys
import whisperx
from pathlib import Path

BASE         = Path(__file__).parent
AUDIO_DIR    = BASE / "audio"
CAPTIONS_DIR = BASE / "captions"

WHISPER_MODEL = "small"
LANGUAGE      = "en"
COMPUTE_TYPE  = "int8"


def fmt_time(s):
    h   = int(s // 3600)
    m   = int((s % 3600) // 60)
    sec = int(s % 60)
    ms  = int(round((s - int(s)) * 1000))
    return f"{h:02}:{m:02}:{sec:02},{ms:03}"


def find_audio_file():
    for ext in ["*.mp3", "*.wav", "*.m4a", "*.aac", "*.flac", "*.ogg"]:
        files = list(AUDIO_DIR.glob(ext))
        if files:
            return files[0]
    return None


def load_script(script_path):
    with open(script_path, "r", encoding="utf-8") as f:
        lines = [l.strip() for l in f.readlines()]
    return [l for l in lines if l]


def get_word_timestamps(audio_path):
    print(f"\n[WhisperX] Loading model '{WHISPER_MODEL}' on CPU...")
    model = whisperx.load_model(
        WHISPER_MODEL,
        device="cpu",
        compute_type=COMPUTE_TYPE,
        language=LANGUAGE,
    )

    print(f"[WhisperX] Transcribing audio: {audio_path.name}...")
    audio  = whisperx.load_audio(str(audio_path))
    result = model.transcribe(audio, batch_size=4, language=LANGUAGE)

    print("[WhisperX] Aligning words to timestamps...")
    align_model, metadata = whisperx.load_align_model(
        language_code=LANGUAGE,
        device="cpu"
    )
    # Fixed: removed unsupported return_char_alignment argument
    result = whisperx.align(
        result["segments"],
        align_model,
        metadata,
        audio,
        device="cpu",
    )

    words = []
    for seg in result["segments"]:
        for w in seg.get("words", []):
            if "start" in w and "end" in w:
                words.append({
                    "word":  w["word"].strip().lower(),
                    "start": w["start"],
                    "end":   w["end"],
                })

    print(f"[WhisperX] Got {len(words)} word timestamps.")
    return words, result["segments"]


def match_lines_to_words(script_lines, words):
    results  = []
    word_idx = 0
    total    = len(words)

    for line_idx, line in enumerate(script_lines):
        line_words = [w.lower().strip(".,!?;:'\"") for w in line.split()]
        if not line_words:
            continue

        first_word  = line_words[0]
        found_idx   = None

        for i in range(word_idx, min(word_idx + 80, total)):
            candidate = words[i]["word"].lower().strip(".,!?;:'\"")
            if candidate == first_word:
                found_idx = i
                break

        if found_idx is None:
            for i in range(max(0, word_idx - 10), min(word_idx + 120, total)):
                candidate = words[i]["word"].lower().strip(".,!?;:'\"")
                if candidate == first_word:
                    found_idx = i
                    break

        if found_idx is not None:
            start_time = words[found_idx]["start"]
            end_time   = words[min(found_idx + len(line_words) - 1, total - 1)]["end"]
            word_idx   = found_idx + 1
        else:
            print(f"  [Warning] Line {line_idx+1} not matched: '{line[:50]}'")
            start_time = results[-1]["end"] + 0.1 if results else 0.0
            end_time   = start_time + len(line.split()) * 0.4

        results.append({"text": line, "start": start_time, "end": end_time})

    for i in range(len(results) - 1):
        results[i]["end"] = max(results[i]["end"], results[i+1]["start"] - 0.05)

    return results


def write_srt(entries, srt_path):
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, e in enumerate(entries, 1):
            f.write(f"{i}\n{fmt_time(e['start'])} --> {fmt_time(e['end'])}\n{e['text']}\n\n")
    print(f"[OK] SRT saved     -> captions\\{srt_path.name}")


def write_prompts(entries, prompts_path):
    with open(prompts_path, "w", encoding="utf-8") as f:
        for e in entries:
            f.write(e["text"] + "\n")
    print(f"[OK] Prompts saved -> captions\\{prompts_path.name}")


def main():
    audio_path = find_audio_file()
    if not audio_path:
        print("[ERROR] No audio file found in audio\\ folder.")
        sys.exit(1)
    print(f"[OK] Audio: {audio_path.name}")

    script_path = AUDIO_DIR / "script.txt"
    if not script_path.exists():
        print("[ERROR] No script.txt found in audio\\ folder.")
        sys.exit(1)

    script_lines = load_script(script_path)
    print(f"[OK] Script: {len(script_lines)} lines loaded")

    words, segments = get_word_timestamps(audio_path)

    print("\n[Align] Matching script lines to audio timestamps...")
    entries = match_lines_to_words(script_lines, words)

    srt_path     = CAPTIONS_DIR / (audio_path.stem + "_aligned.srt")
    prompts_path = CAPTIONS_DIR / (audio_path.stem + "_prompts.txt")

    write_srt(entries, srt_path)
    write_prompts(entries, prompts_path)

    print(f"\nDone! {len(entries)} captions aligned.")
    print(f"\n  captions\\{srt_path.name}     <- use in 2_RUN.bat")
    print(f"  captions\\{prompts_path.name} <- paste into Google Flow")
    print("\n  Check the SRT and edit any timestamps that look off.")


if __name__ == "__main__":
    main()
