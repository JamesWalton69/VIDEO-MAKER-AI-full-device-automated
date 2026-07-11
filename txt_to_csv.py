import os
import csv
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE = Path(__file__).parent
AUDIO_DIR = BASE / "audio"
PROMPT_DIR = BASE / "prompt"
CAPTIONS_DIR = BASE / "captions"

INPUT_TXT = AUDIO_DIR / "script.txt"
OUTPUT_CSV = CAPTIONS_DIR / "script.csv"
OUTPUT_TXT = CAPTIONS_DIR / "script_prompts.txt"
STYLE_PROMPT_FILE = PROMPT_DIR / "prompt.txt"

def main():
    print("============================================")
    print("      Script to CSV Converter Utility       ")
    print("============================================")

    # 1. Check if input script exists
    if not INPUT_TXT.exists():
        print(f"[ERROR] Input script not found: {INPUT_TXT}")
        print("Please place your voiceover script in 'audio/script.txt'.")
        return

    # 2. Read the script lines
    print(f"[Read] Loading script from: {INPUT_TXT.name}")
    with open(INPUT_TXT, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines()]
    
    # Filter out empty lines
    script_lines = [line for line in lines if line]
    if not script_lines:
        print("[ERROR] script.txt is empty!")
        return
    print(f"[OK] Loaded {len(script_lines)} script lines.")

    # 3. Read custom style prompt
    style_suffix = ""
    if STYLE_PROMPT_FILE.exists():
        print(f"[Read] Loading custom style prompt from: {STYLE_PROMPT_FILE.name}")
        with open(STYLE_PROMPT_FILE, "r", encoding="utf-8") as f:
            style_suffix = f.read().strip()
        if style_suffix:
            print(f"[OK] Custom prompt style: '{style_suffix}'")
        else:
            print("[Warning] prompt/prompt.txt is empty. No custom suffix will be attached.")
    else:
        print("[Info] prompt/prompt.txt not found. No custom suffix will be attached.")

    # Clean up old audio/script.csv if it exists to avoid confusion
    old_csv = AUDIO_DIR / "script.csv"
    if old_csv.exists():
        try:
            os.remove(old_csv)
            print(f"[Cleanup] Removed outdated file: audio/{old_csv.name}")
        except Exception:
            pass

    # 4. Generate CSV entries and TXT lines
    print("[Process] Mapping script lines to image prompts...")
    csv_rows = []
    txt_lines = []
    for idx, caption in enumerate(script_lines, 1):
        image_name = f"{idx:03d}.png"  # e.g., 001.png, 002.png...
        
        # Build prompt by attaching the custom prompt style at the end
        if style_suffix:
            # Check if there is already a comma or ending punctuation
            separator = ", " if not caption.endswith(",") else " "
            full_prompt = f"{caption}{separator}{style_suffix}"
        else:
            full_prompt = caption
            
        csv_rows.append({
            "Image": image_name,
            "Caption": caption,
            "Prompt": full_prompt
        })
        txt_lines.append(full_prompt)

    # Make sure captions dir exists
    CAPTIONS_DIR.mkdir(parents=True, exist_ok=True)

    # 5. Write to CSV file
    print(f"[Write] Writing to CSV: captions/{OUTPUT_CSV.name}")
    try:
        with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["Image", "Caption", "Prompt"])
            writer.writeheader()
            writer.writerows(csv_rows)
        print(f"[SUCCESS] CSV saved to: captions/{OUTPUT_CSV.name}")
    except Exception as e:
        print(f"[ERROR] Failed to write CSV file: {e}")

    # 6. Write to TXT file
    print(f"[Write] Writing to TXT: captions/{OUTPUT_TXT.name}")
    try:
        with open(OUTPUT_TXT, "w", encoding="utf-8") as f:
            for prompt in txt_lines:
                f.write(prompt + "\n")
        print(f"[SUCCESS] Prompts TXT saved to: captions/{OUTPUT_TXT.name}")
    except Exception as e:
        print(f"[ERROR] Failed to write TXT file: {e}")

if __name__ == "__main__":
    main()
