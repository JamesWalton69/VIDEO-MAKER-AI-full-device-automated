import os
import sys
import json
import subprocess
from pathlib import Path

# Try importing google-genai, install if missing
try:
    from google import genai
    from google.genai import types
except ImportError:
    print("[INFO] Google GenAI SDK is not installed. Installing google-genai using uv...")
    try:
        # Try using uv first
        subprocess.run(["uv", "pip", "install", "--python", sys.executable, "google-genai"], check=True)
    except Exception:
        # Fallback to standard pip
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "google-genai"], check=True)
        except Exception as e:
            print(f"[ERROR] Failed to install google-genai. Please run 'uv pip install google-genai' manually. Error: {e}")
            sys.exit(1)
            
    # Retry import
    from google import genai
    from google.genai import types

BASE = Path(__file__).parent
PROMPT_DIR = BASE / "prompt"
IMAGES_DIR = BASE / "images"
API_KEY_FILE = PROMPT_DIR / ".api_key"

def load_api_key():
    if "GEMINI_API_KEY" in os.environ:
        return os.environ["GEMINI_API_KEY"]
    
    if API_KEY_FILE.exists():
        try:
            with open(API_KEY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("type") == "gemini":
                    return data.get("key")
        except Exception:
            pass
    return None

def main():
    print("==================================================")
    print("        VideoMaker AI - Google Image Generator     ")
    print("==================================================")
    
    # Check API key
    api_key = load_api_key()
    if not api_key:
        print("\n[ERROR] No Gemini API Key found.")
        print("Please run option [2] (Write / Generate Video Script) first to enter your key,")
        print("or set the GEMINI_API_KEY environment variable.")
        api_key = input("\nEnter your Gemini API Key: ").strip()
        if not api_key:
            print("Operation cancelled.")
            return
        # Save key for future use
        PROMPT_DIR.mkdir(exist_ok=True)
        try:
            with open(API_KEY_FILE, "w", encoding="utf-8") as f:
                json.dump({"type": "gemini", "key": api_key}, f)
        except Exception:
            pass
            
    # Load prompts
    prompts_path = PROMPT_DIR / "image_prompts.txt"
    if not prompts_path.exists():
        prompts_path = BASE / "captions" / "script_prompts.txt"
        
    if not prompts_path.exists():
        print(f"[ERROR] No prompts found. Please generate prompts first (Option [5] or similar).")
        return
        
    with open(prompts_path, "r", encoding="utf-8") as f:
        prompts = [line.strip() for line in f.readlines() if line.strip()]
        
    if not prompts:
        print("[ERROR] Prompts file is empty.")
        return
        
    print(f"[OK] Loaded {len(prompts)} image prompts.")
    
    # Determine aspect ratio based on active config (we can read it or prompt the user)
    print("\nSelect Aspect Ratio for Generation:")
    print("[1] Landscape (16:9)")
    print("[2] Vertical (9:16)")
    print("[3] Square (1:1)")
    ratio_choice = input("Select option [1-3, Default: 2]: ").strip()
    
    aspect_ratio = "9:16"
    if ratio_choice == "1":
        aspect_ratio = "16:9"
    elif ratio_choice == "3":
        aspect_ratio = "1:1"
        
    print(f"[Info] Aspect Ratio: {aspect_ratio}")
    
    # Model Selection Options (Bana 2 - gemini-3.1-flash-image or gemini-3-pro-image)
    print("\nSelect Google AI Image Generation Model:")
    print("[1] Gemini 3.1 Flash Image (Bana 2 - Fast/Standard)")
    print("[2] Gemini 3 Pro Image (Bana 2 Pro - High Quality)")
    print("[3] Gemini 3.1 Flash Lite Image (Bana 2 Lite)")
    print("[4] Imagen 3 (Legacy - if enabled on project)")
    print("[5] Imagen 4 (Legacy - if enabled on project)")
    model_choice = input("Select option [1-5, Default: 1]: ").strip()
    
    model_name = "gemini-3.1-flash-image"
    is_multimodal = True
    if model_choice == "2":
        model_name = "gemini-3-pro-image"
    elif model_choice == "3":
        model_name = "gemini-3.1-flash-lite-image"
    elif model_choice == "4":
        model_name = "imagen-3.0-generate-002"
        is_multimodal = False
    elif model_choice == "5":
        model_name = "imagen-4.0-generate-001"
        is_multimodal = False
        
    print(f"[Info] Model selected: {model_name}")
    
    # Ask if user wants to clear the images directory first
    if IMAGES_DIR.exists() and any(IMAGES_DIR.iterdir()):
        clear_old = input("\nDo you want to delete existing images in 'images/' before starting? (y/n): ").strip().lower()
        if clear_old == 'y':
            for f in IMAGES_DIR.glob("*"):
                if f.name != ".gitkeep":
                    try:
                        f.unlink()
                    except Exception:
                        pass
            print("[Info] Cleaned 'images/' folder.")
            
    IMAGES_DIR.mkdir(exist_ok=True)
    
    # Initialize Google GenAI client
    print("\n[AI] Initializing Google GenAI Client...")
    client = genai.Client(api_key=api_key)
    
    # Generate images
    print(f"\nGenerating {len(prompts)} images using {model_name}...")
    
    try:
        from tqdm import tqdm
        iterator = tqdm(enumerate(prompts, 1), total=len(prompts), desc="Generating Images")
    except ImportError:
        iterator = enumerate(prompts, 1)
        
    success_count = 0
    
    for idx, prompt in iterator:
        filename = f"{idx:03d}.png"
        output_path = IMAGES_DIR / filename
        
        # Enforce 1k resolution and specified aspect ratio in prompt text
        prompt_with_config = f"{prompt}, 1k resolution, {aspect_ratio} aspect ratio"
        
        # If no tqdm, print progress
        if isinstance(iterator, enumerate):
            print(f"[{idx}/{len(prompts)}] Generating image for: '{prompt[:50]}...'")
            
        try:
            if is_multimodal:
                # Use generate_content for gemini-*-image models
                result = client.models.generate_content(
                    model=model_name,
                    contents=prompt_with_config,
                    config=types.GenerateContentConfig(
                        response_modalities=["IMAGE"]
                    )
                )
                
                # Extract image parts
                saved = False
                for part in result.candidates[0].content.parts:
                    if part.inline_data:
                        image_bytes = part.inline_data.data
                        with open(output_path, "wb") as f:
                            f.write(image_bytes)
                        success_count += 1
                        saved = True
                        break
                if not saved:
                    raise Exception("No image data found in response parts.")
            else:
                # Use generate_images for legacy imagen models
                result = client.models.generate_images(
                    model=model_name,
                    prompt=prompt_with_config,
                    config=types.GenerateImagesConfig(
                        number_of_images=1,
                        aspect_ratio=aspect_ratio,
                        output_mime_type="image/png"
                    )
                )
                for generated_image in result.generated_images:
                    generated_image.image.save(str(output_path))
                    success_count += 1
                
        except Exception as e:
            print(f"\n[ERROR] Failed to generate image {idx}: {e}")
            
    print(f"\n[SUCCESS] Successfully generated {success_count} / {len(prompts)} images!")
    print("Images are saved in the 'images/' folder.")
    input("\nPress Enter to return to menu...")

if __name__ == "__main__":
    main()
