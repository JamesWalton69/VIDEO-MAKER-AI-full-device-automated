import os
import sys
import json
import urllib.request
from pathlib import Path

BASE = Path(__file__).parent
PROMPT_DIR = BASE / "prompt"
API_KEY_FILE = PROMPT_DIR / ".api_key"

def load_api_key():
    if "GEMINI_API_KEY" in os.environ:
        return "gemini", os.environ["GEMINI_API_KEY"]
    if "OPENAI_API_KEY" in os.environ:
        return "openai", os.environ["OPENAI_API_KEY"]
    
    if API_KEY_FILE.exists():
        try:
            with open(API_KEY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("type"), data.get("key")
        except Exception:
            pass
    return None, None

def save_api_key(api_type, api_key):
    PROMPT_DIR.mkdir(exist_ok=True)
    try:
        with open(API_KEY_FILE, "w", encoding="utf-8") as f:
            json.dump({"type": api_type, "key": api_key}, f)
    except Exception:
        pass

def generate_script_gemini(topic, runtime_sec, api_key):
    target_words = int(runtime_sec * 2.5)
    prompt = (
        f"Write a very detailed video narration script on the topic: '{topic}'. "
        f"The target duration is {runtime_sec} seconds, which requires approximately {target_words} words. "
        f"The tone should be engaging. Write ONLY the spoken script text itself, with each scene/paragraph on a new line. "
        f"Do NOT include any scene descriptions, bracketed notes, character names, headers, or timestamps. "
        f"Just the final narration text to be read by Text-to-Speech."
    )
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    body = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            script_text = res_data["candidates"][0]["content"]["parts"][0]["text"]
            return script_text.strip()
    except Exception as e:
        print(f"[Error calling Gemini API] {e}")
        return None

def generate_script_openai(topic, runtime_sec, api_key):
    target_words = int(runtime_sec * 2.5)
    prompt = (
        f"Write a very detailed video narration script on the topic: '{topic}'. "
        f"The target duration is {runtime_sec} seconds, which requires approximately {target_words} words. "
        f"The tone should be engaging. Write ONLY the spoken script text itself, with each scene/paragraph on a new line. "
        f"Do NOT include any scene descriptions, bracketed notes, character names, headers, or timestamps. "
        f"Just the final narration text to be read by Text-to-Speech."
    )
    
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    body = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }
    
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            script_text = res_data["choices"][0]["message"]["content"]
            return script_text.strip()
    except Exception as e:
        print(f"[Error calling OpenAI API] {e}")
        return None

def generate_fallback_template(topic, runtime_sec):
    target_words = int(runtime_sec * 2.5)
    paragraphs = []
    paragraphs.append(f"[INTRO - Hook the viewer about '{topic}' here. Estimated words: {int(target_words * 0.2)}]")
    
    body_count = max(1, int(runtime_sec / 30))
    for i in range(body_count):
        paragraphs.append(f"[BODY PART {i+1} - Elaborate on a key aspect of '{topic}' here. Estimated words: {int(target_words * 0.6 / body_count)}]")
        
    paragraphs.append(f"[OUTRO - Call to action, wrap up the video on '{topic}'. Estimated words: {int(target_words * 0.2)}]")
    
    script_text = "\n\n".join(paragraphs)
    return script_text

def main():
    print("==================================================")
    print("        VideoMaker AI - Script Generator          ")
    print("==================================================")
    
    PROMPT_DIR.mkdir(exist_ok=True)
    script_path = PROMPT_DIR / "script.txt"
    
    if script_path.exists() and script_path.stat().st_size > 0:
        overwrite = input("[WARNING] script.txt already exists. Overwrite? (y/n): ").strip().lower()
        if overwrite != 'y':
            print("Operation cancelled.")
            return

    try:
        runtime_sec = int(input("Enter target video runtime (in seconds): ").strip())
        if runtime_sec <= 0:
            print("[ERROR] Runtime must be greater than 0.")
            return
    except ValueError:
        print("[ERROR] Invalid runtime. Must be an integer.")
        return
        
    topic = input("Enter video topic/theme (e.g. 'History of Rome'): ").strip()
    if not topic:
        print("[ERROR] Topic cannot be empty.")
        return

    api_type, api_key = load_api_key()
    
    if not api_key:
        print("\nAuto-generation requires a Google Gemini or OpenAI API Key.")
        print("[1] Enter Gemini API Key (Recommended - Free / Low cost)")
        print("[2] Enter OpenAI API Key")
        print("[3] Use template script fallback (Manual entry)")
        key_choice = input("Select option [1-3, Default: 3]: ").strip()
        
        if key_choice == "1":
            api_key = input("Enter your Gemini API Key: ").strip()
            if api_key:
                api_type = "gemini"
                save_api_key(api_type, api_key)
        elif key_choice == "2":
            api_key = input("Enter your OpenAI API Key: ").strip()
            if api_key:
                api_type = "openai"
                save_api_key(api_type, api_key)
                
    script_text = None
    if api_key:
        print(f"\n[AI] Requesting script generation from {api_type.capitalize()} on topic '{topic}'...")
        if api_type == "gemini":
            script_text = generate_script_gemini(topic, runtime_sec, api_key)
        elif api_type == "openai":
            script_text = generate_script_openai(topic, runtime_sec, api_key)
            
    if script_text:
        print("\n[SUCCESS] AI Script generated successfully!")
    else:
        print("\n[INFO] Generating template script fallback...")
        script_text = generate_fallback_template(topic, runtime_sec)
        print("Please edit the script.txt file manually to complete your script details.")
        
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_text)
        
    print(f"\nSaved script to: {script_path.name}")
    print("Script Preview:")
    print("--------------------------------------------------")
    print(script_text[:500] + ("\n..." if len(script_text) > 500 else ""))
    print("--------------------------------------------------")
    input("\nPress Enter to return to menu...")

if __name__ == "__main__":
    main()
