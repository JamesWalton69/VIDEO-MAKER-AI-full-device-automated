import re
from pathlib import Path

BASE = Path(__file__).parent
PROMPT_DIR = BASE / "prompt"

def split_into_sentences(text):
    """Split text into sentences cleanly using regex."""
    # Split on periods, exclamation marks, or question marks followed by space or newline
    sentence_end = re.compile(r'(?<=[.!?])\s+')
    sentences = sentence_end.split(text)
    return [s.strip() for s in sentences if s.strip()]

def main():
    script_path = PROMPT_DIR / "script.txt"
    output_path = PROMPT_DIR / "image_prompts.txt"

    if not script_path.exists():
        print(f"[ERROR] No script found at '{script_path}'. Please run the TTS tool or create 'prompt/script.txt' first.")
        return

    with open(script_path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    if not content:
        print("[ERROR] script.txt is empty!")
        return

    # Split script into segments (by sentence or paragraph)
    print("\n--- Image Prompt Generation Options ---")
    print("[1] Split by paragraph (fewer, longer segments)")
    print("[2] Split by sentence (more segments, higher visual synchronization)")
    
    choice = input("\nSelect segmenting option [1-2, Default: 2]: ").strip()
    
    if choice == "1":
        segments = [p.strip() for p in content.split("\n\n") if p.strip()]
    else:
        # Split paragraphs into sentences
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        segments = []
        for p in paragraphs:
            segments.extend(split_into_sentences(p))

    print("\n--- Prompt Style Enhancement ---")
    print("[1] No style (raw sentences as prompts)")
    print("[2] Cinematic / Realistic (adds: 'photorealistic, cinematic lighting, 8k')")
    print("[3] 3D Pixar Style (adds: '3d cartoon style, pixar character style, vibrant colors')")
    print("[4] Digital Art / Anime (adds: 'digital art, anime illustration style, highly detailed')")
    
    style_choice = input("\nSelect a style multiplier [1-4, Default: 2]: ").strip()
    
    style_suffix = ""
    if style_choice == "1":
        style_suffix = ""
    elif style_choice == "3":
        style_suffix = ", 3d cartoon style, pixar character style, vibrant colors, highly detailed"
    elif style_choice == "4":
        style_suffix = ", digital art, anime illustration style, highly detailed, vivid"
    else: # Default is 2
        style_suffix = ", photorealistic, cinematic lighting, 8k resolution, highly detailed"

    # Generate prompts
    prompts = []
    for seg in segments:
        # Clean segment from special characters or double spaces
        clean_seg = re.sub(r'\s+', ' ', seg)
        prompts.append(f"{clean_seg}{style_suffix}")

    # Write prompts to output file
    with open(output_path, "w", encoding="utf-8") as f:
        for prompt in prompts:
            f.write(f"{prompt}\n")

    print(f"\n[SUCCESS] Generated {len(prompts)} prompts!")
    print(f"File saved to: prompt/image_prompts.txt")
    print("You can copy these prompts and paste them into your Google Flow image agent!")

if __name__ == "__main__":
    main()
