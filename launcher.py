import os
import sys
import subprocess
from pathlib import Path

# Paths
BASE = Path(__file__).parent
AUDIO_DIR = BASE / "audio"
IMAGES_DIR = BASE / "images"
PROMPT_DIR = BASE / "prompt"
TOOLS_DIR = BASE / "tools"

# Active configuration state (resets on restart, defaults here)
config = {
    "subtitles": True,
    "zoom": False,
    "resolution": "1920x1080",
    "model": "turbo",
    "threads": 0
}

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def check_setup():
    """Verify setup integrity."""
    issues = []
    
    # Check FFmpeg
    ffmpeg_on_path = subprocess.run("where ffmpeg", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True).returncode == 0
    ffmpeg_in_tools = (TOOLS_DIR / "ffmpeg.exe").exists()
    
    if not (ffmpeg_on_path or ffmpeg_in_tools):
        issues.append("FFmpeg is missing from path/tools (Run 1_SETUP.bat)")
        
    return len(issues) == 0, issues

def scan_files():
    """Scan directory contents for project assets."""
    status = {
        "audio_count": 0,
        "audio_name": "None",
        "image_count": 0,
        "script_exists": False,
        "script_len": 0,
        "prompts_exists": False,
    }
    
    # Scan audio
    if AUDIO_DIR.exists():
        audio_files = []
        for ext in ["*.mp3", "*.wav", "*.m4a", "*.aac", "*.flac", "*.ogg"]:
            audio_files.extend(list(AUDIO_DIR.glob(ext)))
        status["audio_count"] = len(audio_files)
        if audio_files:
            status["audio_name"] = audio_files[0].name
            
    # Scan images
    if IMAGES_DIR.exists():
        image_files = []
        for ext in ["*.png", "*.jpg", "*.jpeg", "*.webp"]:
            image_files.extend(list(IMAGES_DIR.glob(ext)))
        status["image_count"] = len(image_files)
        
    # Scan script
    script_path = PROMPT_DIR / "script.txt"
    if script_path.exists():
        status["script_exists"] = True
        status["script_len"] = script_path.stat().st_size
        
    # Scan prompts
    prompts_path = PROMPT_DIR / "image_prompts.txt"
    if prompts_path.exists():
        status["prompts_exists"] = True
        
    return status

def run_sanitizer():
    print("\n--- Running Filename Sanitizer ---")
    try:
        from clean_images import clean_image_filenames
        clean_image_filenames()
    except ImportError:
        print("[ERROR] Could not import clean_images.py. Running as subprocess...")
        subprocess.run([sys.executable, "clean_images.py"])
    input("\nPress Enter to return to menu...")

def run_tts():
    print("\n--- Running Text-To-Speech Generator ---")
    try:
        from generate_tts import main as tts_main
        tts_main()
    except ImportError:
        subprocess.run([sys.executable, "generate_tts.py"])
    input("\nPress Enter to return to menu...")

def run_prompt_gen():
    print("\n--- Running Image Prompt Generator ---")
    try:
        from generate_prompts import main as prompt_main
        prompt_main()
    except ImportError:
        subprocess.run([sys.executable, "generate_prompts.py"])
    input("\nPress Enter to return to menu...")

def configure_settings():
    import multiprocessing
    max_cores = multiprocessing.cpu_count()
    while True:
        clear_screen()
        print("==================================================")
        print("         VideoMaker AI - Settings Configuration   ")
        print("==================================================")
        print(f"[1] Burn Subtitles:      {'ENABLED' if config['subtitles'] else 'DISABLED'}")
        print(f"[2] Pan & Zoom (Motion):  {'ENABLED' if config['zoom'] else 'DISABLED'}")
        print(f"[3] Resolution:          {config['resolution']}")
        print(f"[4] Whisper Model:       {config['model']}")
        print(f"[5] CPU Render Cores:    {'Auto (All minus 1)' if config['threads'] == 0 else f'{config['threads']} Cores'} (Max: {max_cores})")
        print("[6] Back to Main Menu")
        print("==================================================")
        
        choice = input("Select setting to toggle/change [1-6]: ").strip()
        
        if choice == "1":
            config["subtitles"] = not config["subtitles"]
        elif choice == "2":
            config["zoom"] = not config["zoom"]
        elif choice == "3":
            print("\nSelect Output Resolution:")
            print("[1] Landscape 16:9 (1920x1080)")
            print("[2] Vertical 9:16 (1080x1920) - For Shorts/Reels")
            print("[3] Square 1:1 (1080x1080)")
            res_choice = input("Select option [1-3]: ").strip()
            if res_choice == "1":
                config["resolution"] = "1920x1080"
            elif res_choice == "2":
                config["resolution"] = "1080x1920"
            elif res_choice == "3":
                config["resolution"] = "1080x1080"
        elif choice == "4":
            print("\nSelect Whisper Transcription Model:")
            print("Options: tiny, base, small, medium, large, turbo")
            model_choice = input("Type model name [Default: turbo]: ").strip().lower()
            if model_choice in ["tiny", "base", "small", "medium", "large", "turbo"]:
                config["model"] = model_choice
            else:
                config["model"] = "turbo"
        elif choice == "5":
            print(f"\nEnter number of CPU cores to use (0 = Auto-detect all minus 1, Max: {max_cores}):")
            try:
                cores_choice = int(input(f"Enter cores [0-{max_cores}]: ").strip())
                if 0 <= cores_choice <= max_cores:
                    config["threads"] = cores_choice
                else:
                    print(f"[WARNING] Invalid core count. Must be between 0 and {max_cores}.")
                    input("Press Enter to continue...")
            except ValueError:
                print("[WARNING] Invalid input. Must be an integer.")
                input("Press Enter to continue...")
        elif choice == "6":
            break

def render_video(file_status):
    clear_screen()
    print("==================================================")
    print("         VideoMaker AI - Starting Render          ")
    print("==================================================")
    
    # Pre-checks
    if file_status["audio_count"] == 0:
        print("[ERROR] Cannot render: No audio files found in 'audio/'.")
        input("\nPress Enter to return...")
        return
        
    if file_status["image_count"] == 0:
        print("[ERROR] Cannot render: No images found in 'images/'.")
        input("\nPress Enter to return...")
        return
        
    # Build command arguments
    cmd = [
        sys.executable, 
        "make_video.py",
        "--resolution", config["resolution"],
        "--model", config["model"]
    ]
    
    if config["subtitles"]:
        cmd.append("--subtitles")
    else:
        cmd.append("--no-subtitles")
        
    if config["zoom"]:
        cmd.append("--zoom")
    else:
        cmd.append("--no-zoom")
        
    cmd.extend(["--threads", str(config["threads"])])
        
    print(f"Running command: {' '.join(cmd)}")
    print("Please wait, rendering your video...\n")
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Video generation failed: {e}")
    except KeyboardInterrupt:
        print("\n[INFO] Rendering interrupted by user.")
        
    input("\nPress Enter to return to menu...")

def main():
    while True:
        clear_screen()
        setup_ok, setup_issues = check_setup()
        files = scan_files()
        
        print("==================================================")
        print("     VideoMaker AI - Central Control Panel        ")
        print("==================================================")
        
        # System setup status
        if setup_ok:
            print("System Status:  [OK] READY (FFmpeg found)")
        else:
            print("System Status:  [WARNING] ISSUES DETECTED:")
            for issue in setup_issues:
                print(f"                - {issue}")
                
        # File status indicators
        print("--------------------------------------------------")
        print(f"Audio File:     {files['audio_name']} ({files['audio_count']} found)")
        print(f"Images:         {files['image_count']} files found")
        print(f"Script:         {'script.txt found (' + str(files['script_len']) + ' bytes)' if files['script_exists'] else '[Missing]'}")
        print(f"Image Prompts:  {'image_prompts.txt ready' if files['prompts_exists'] else '[Missing]'}")
        print("--------------------------------------------------")
        
        # Current active configurations
        print(f"Render Config:  Subtitles: {'ON' if config['subtitles'] else 'OFF'} | Motion: {'ON' if config['zoom'] else 'OFF'} | Res: {config['resolution']} | Cores: {'Auto' if config['threads'] == 0 else config['threads']}")
        print("--------------------------------------------------")
        print("OPTIONS:")
        print(" [1] Clean Image Filenames (Remove extra characters)")
        print(" [2] Generate Audio via Text-To-Speech (from script.txt)")
        print(" [3] Generate Image Prompts for Google Flow (from script.txt)")
        print(" [4] Configure Rendering Settings")
        print(" [5] Render Video (Build output)")
        print(" [6] Exit")
        print("==================================================")
        
        choice = input("Enter option [1-6]: ").strip()
        
        if choice == "1":
            run_sanitizer()
        elif choice == "2":
            run_tts()
        elif choice == "3":
            run_prompt_gen()
        elif choice == "4":
            configure_settings()
        elif choice == "5":
            render_video(files)
        elif choice == "6":
            print("\nExiting. Happy Video Making!")
            break

if __name__ == "__main__":
    main()
