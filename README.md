# 🎬 VideoMaker AI (Full Device Automated)

An elegant, fully automated pipeline that transcribes audio using OpenAI's Whisper model, matches captions to sequential images, and renders fully synchronized videos. Everything runs locally on your device!

---

## ✨ Features

- 🔒 **Local & Private**: No cloud dependencies or API keys required for transcription and video generation.
- 🎙️ **Whisper AI Integration**: Automatic transcription with timestamped subtitles (`.srt`).
- 🖼️ **Flexible Image Support**: Supports `.png`, `.jpg`, `.jpeg`, and `.webp` extensions.
- 🤖 **Google Flow Automation**: Fully automated bulk image generation and sequential numbering.
- 🧹 **Filename Sanitization**: Built-in script to instantly clean up messy filenames (e.g. `001_abcxyz.webp` ➔ `001.webp`).

---

## 🛠️ Folder Structure

```text
VideoMaker/
 ├── 1_SETUP.bat                    # Setup virtual environment & dependencies
 ├── 2_RUN.bat                      # Transcribe audio and generate the video
 ├── make_video.py                  # Core video rendering engine
 ├── clean_images.py                # Image filename cleanup tool
 ├── FlowAutomator_MasterPrompt.docx# Prompt script for Google Flow Agent
 ├── audio/                         # Put your source audio here
 ├── images/                        # Put your numbered images here
 ├── captions/                      # Auto-generated SRT subtitles
 └── output/                        # Final synced video outputs
```

---

## 🚀 Step-by-Step Guide

### **Step 1: First-Time Setup**
Double-click **`1_SETUP.bat`**. This will:
* Set up a lightweight local Python virtual environment (`.venv`).
* Install all required dependencies (`openai-whisper`, `moviepy`, `pillow`, etc.).
* Download a portable version of FFmpeg into the `tools/` folder.

---

### **Step 2: Prepare Your Audio**
Place your background audio track (supports `mp3`, `wav`, `m4a`, `aac`, `flac`, `ogg`) in the audio folder:
📁 `audio/`

---

### **Step 3: Generate Images via Google Flow**
To automate image generation and numbering:
1. Open your **Google Flow** agent.
2. Open **`FlowAutomator_MasterPrompt.docx`** in this directory, copy its system prompt instructions, and paste them into your Flow Agent's instructions box.
3. Paste your line-separated image prompts. The agent will automatically generate images sequentially.
4. Use a bulk downloader browser extension (like *Simple Mass Downloader*, *Tab Save*, etc.) to download the files automatically.

---

### **Step 4: Clean Up Image Names**
If your downloaded images have extra characters in their names (e.g. `001_kbgbbgi.png` or `002_randomtext.webp`):
1. Place them directly in the 📁 `images/` directory.
2. Open a terminal in the project directory and run the cleanup script:
   ```bash
   python clean_images.py
   ```
   *This script extracts the leading number, pads it to 3 digits (e.g., `001`, `002`), removes all messy characters, and preserves the original file extension (even if there's a mix of PNG, JPG, JPEG, and WebP).*

---

### **Step 5: Render Your Video**
Double-click **`2_RUN.bat`**.
* The script transcribes the audio, builds subtitle tracks under `captions/`, and renders the final video.
* *(Optional)* If the subtitles need tiny edits, you can modify the generated `.srt` file inside `captions/` and run **`2_RUN.bat`** again.

---

### **Step 6: Get Your Video!**
Once rendering finishes, find your finished video in:
📁 `output/`

---

## ❔ Handling Different Extensions

Our pipeline natively supports a mixture of image formats (**`.png`**, **`.jpg`**, **`.jpeg`**, and **`.webp`**). 
The `clean_images.py` script will clean their names (e.g. `002_image.jpg` ➔ `002.jpg`) while keeping their original extension. The rendering engine will automatically resize, letterbox, and transition between them smoothly regardless of format!
