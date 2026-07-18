import os
import sys
import asyncio
from pathlib import Path
import edge_tts

BASE = Path(__file__).parent
PROMPT_DIR = BASE / "prompt"
AUDIO_DIR = BASE / "audio"

# Available high-quality voices
VOICES = {
    "1": ("en-US-AndrewNeural", "US Male (Andrew) - Warm, Natural"),
    "2": ("en-US-EmmaNeural", "US Female (Emma) - Friendly, Natural"),
    "3": ("en-US-BrianNeural", "US Male (Brian) - Professional"),
    "4": ("en-US-AvaNeural", "US Female (Ava) - Clear, Natural"),
    "5": ("en-GB-RyanNeural", "UK Male (Ryan) - British Accent"),
    "6": ("en-GB-SoniaNeural", "UK Female (Sonia) - British Accent"),
    "7": ("en-AU-WilliamNeural", "AU Male (William) - Aussie Accent"),
    "8": ("en-US-GuyNeural", "US Male (Guy) - Legacy"),
    "9": ("en-US-JennyNeural", "US Female (Jenny) - Legacy"),
}

async def generate_speech(text, voice, output_path):
    """Call edge-tts to generate speech from text."""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

def main():
    PROMPT_DIR.mkdir(exist_ok=True)
    AUDIO_DIR.mkdir(exist_ok=True)
    
    script_path = PROMPT_DIR / "script.txt"
    
    # If script.txt does not exist, create a sample one
    if not script_path.exists():
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(
                "Welcome to VideoMaker AI. This is a sample script. "
                "Place your sentences here, each on a new paragraph. "
                "The system will automatically convert this text into speech "
                "and generate matching images for each paragraph."
            )
        print(f"\n[INFO] Created sample script at: {script_path.name}")
        print("Please edit this file with your desired video script and run again.")
        sys.exit(0)

    # Read script content
    with open(script_path, "r", encoding="utf-8") as f:
        text = f.read().strip()

    if not text:
        print("[ERROR] script.txt is empty! Please write your script content in it.")
        sys.exit(1)

    print("\n--- Text-To-Speech (TTS) Voice Selection ---")
    for key, (voice_id, desc) in VOICES.items():
        print(f"[{key}] {desc}")
        
    choice = input("\nSelect a voice option [1-9, Default: 1]: ").strip()
    selected_voice = VOICES.get(choice, VOICES["1"])[0]
    
    output_filename = "voiceover.mp3"
    output_path = AUDIO_DIR / output_filename
    
    print(f"\n[TTS] Generating voiceover using voice: {selected_voice}...")
    try:
        asyncio.run(generate_speech(text, selected_voice, str(output_path)))
        print(f"[SUCCESS] Voiceover saved to: audio/{output_filename}")
    except Exception as e:
        print(f"[ERROR] Error generating speech: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
