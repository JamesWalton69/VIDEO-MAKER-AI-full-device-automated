import os
import sys
import json
import subprocess
import tempfile
import shutil
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
    print("      VideoMaker AI - Multi-Model Image Generator ")
    print("==================================================")
    
    # Model Selection Options first
    print("\nSelect AI Image Generation Model:")
    print("[1] Gemini 3.1 Flash Image (Bana 2 - Paid Developer API Key required)")
    print("[2] Gemini 3 Pro Image (Bana 2 Pro - Paid Developer API Key required)")
    print("[3] Pollinations AI (100% Free - No API Key, Flux Model)")
    print("[4] Google Flow - Nano Banana 2 (gflow-cli - Free subscription credits)")
    print("[5] Google Flow - Nano Banana Pro (gflow-cli - Free subscription credits)")
    print("[6] Google Flow - Authenticate / Login Account (gflow auth login)")
    model_choice = input("Select option [1-6, Default: 3]: ").strip()
    if not model_choice:
        model_choice = "3"
        
    gflow_bin = str(BASE / ".venv" / "Scripts" / "gflow.exe")
    if not Path(gflow_bin).exists():
        gflow_bin = "gflow"
        
    if model_choice == "6":
        print("\n[GFlow] Launching browser login. Please sign in to your Google Account in the browser window that opens...")
        try:
            subprocess.run([gflow_bin, "auth", "login"], check=True)
            print("\n[OK] Authentication process finished. You can now generate images using options [4] or [5].")
        except Exception as e:
            print(f"\n[ERROR] Authentication failed: {e}")
        input("\nPress Enter to return to menu...")
        return
        
    # Load prompts
    prompts_path = PROMPT_DIR / "image_prompts.txt"
    if not prompts_path.exists():
        prompts_path = BASE / "captions" / "script_prompts.txt"
        
    if not prompts_path.exists():
        print(f"[ERROR] No prompts found. Please generate prompts first.")
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
    
    is_free = (model_choice == "3")
    is_gflow = (model_choice in ["4", "5"])
    
    model_name = "gemini-3.1-flash-image"
    is_multimodal = True
    
    if model_choice == "1":
        model_name = "gemini-3.1-flash-image"
    elif model_choice == "2":
        model_name = "gemini-3-pro-image"
    elif model_choice == "3":
        model_name = "Pollinations Flux (Free)"
    elif model_choice == "4":
        model_name = "Google Flow Nano 2"
    elif model_choice == "5":
        model_name = "Google Flow Nano Pro"
        
    print(f"[Info] Model selected: {model_name}")
    
    api_key = None
    if not is_free and not is_gflow:
        # Check API key
        api_key = load_api_key()
        if not api_key:
            print("\n[ERROR] No Gemini API Key found.")
            print("Please set the GEMINI_API_KEY environment variable, or enter it below.")
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
    
    # Initialize Google GenAI client if using Developer API
    client = None
    if not is_free and not is_gflow:
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
            if is_free:
                # Use Pollinations AI (Flux Model)
                import urllib.parse
                import urllib.request
                
                # Determine dimensions for 1k resolution
                width, height = 1024, 1024
                if aspect_ratio == "16:9":
                    width, height = 1024, 576
                elif aspect_ratio == "9:16":
                    width, height = 576, 1024
                    
                encoded_prompt = urllib.parse.quote(prompt_with_config)
                url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&model=flux&nologo=true&private=true"
                
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=30) as response:
                    image_bytes = response.read()
                    with open(output_path, "wb") as f:
                        f.write(image_bytes)
                success_count += 1
                
            elif is_gflow:
                # Use gflow-cli to pull from Google Flow Veo credits
                model_arg = "nano2" if model_choice == "4" else "nano-pro"
                with tempfile.TemporaryDirectory() as temp_dir:
                    cmd = [
                        gflow_bin, "image", "t2i",
                        prompt_with_config,
                        "--model", model_arg,
                        "--aspect", aspect_ratio,
                        "--out", temp_dir,
                        "--json"
                    ]
                    
                    # Run the gflow-cli command
                    run_res = subprocess.run(cmd, capture_output=True, text=True)
                    
                    # Find and move generated file
                    generated_files = list(Path(temp_dir).glob("*.png")) + list(Path(temp_dir).glob("*.jpg"))
                    if generated_files:
                        shutil.move(str(generated_files[0]), str(output_path))
                        success_count += 1
                    else:
                        raise Exception(f"gflow-cli failed to produce an image. Error output:\n{run_res.stderr}\nStdout:\n{run_res.stdout}")
                        
            elif is_multimodal:
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
