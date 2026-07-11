# 🎬 VideoMaker AI (Full Device Automated)

An elegant, fully automated pipeline that transcribes audio using OpenAI's Whisper model, matches captions to sequential images, and renders fully synchronized videos. Everything runs locally on your device!

---

## ✨ Features

- 🖥️ **Central Control Panel Dashboard**: Manage the entire pipeline interactively using a single launchpad file.
- 🎙️ **Whisper AI Integration**: Automatic transcription with timestamped subtitles (`.srt`).
- 💬 **Zero-Dependency Burnt-in Subtitles**: Renders high-quality subtitles directly onto the video frames without needing ImageMagick.
- 🗣️ **Realistic Text-To-Speech (TTS)**: Convert script text in `prompt/script.txt` into natural-sounding voiceovers without paying for API keys.
- 🖼️ **Pan & Zoom Transitions (Ken Burns)**: Give static slide images subtle, cinematic motion effects.
- 🤖 **Google Flow Automation**: Auto-generate sequential prompts from your script with style boosters (Pixar, Cinematic, Anime) for bulk creation.
- 🧹 **Filename Sanitizer**: Instantly clean messy filenames (e.g. `001_abcxyz.webp` ➔ `001.webp`) to keep formatting aligned.

---

## 🛠️ Folder Structure

```text
VideoMaker/
 ├── START.bat                      # The interactive Dashboard Launcher (Double-click!)
 ├── 1_SETUP.bat                    # Setup virtual environment & dependencies
 ├── 2_RUN.bat                      # Run default video rendering directly
 ├── make_video.py                  # Core video rendering engine
 ├── launcher.py                    # Dashboard launcher source script
 ├── clean_images.py                # Image filename cleanup tool
 ├── generate_tts.py                # TTS audio generator script
 ├── generate_prompts.py            # Prompt splitting and generator script
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
* Install all required dependencies (`openai-whisper`, `moviepy`, `pillow`, `edge-tts`, etc.).
* Download a portable version of FFmpeg into the `tools/` folder.

---

### **Step 2: Launch the Control Panel**
Double-click **`START.bat`**. This launches the central console:
* It scans your setup and folders to display a live status update (audio found, script present, image counts, etc.).
* Offers an interactive menu where you can configure options, run helpers, or render videos.

---

### **Step 3: Write Script & Generate Voiceover/Prompts (Optional)**
If you want to build a video from scratch using a text script:
1. Put your text script in `prompt/script.txt`.
2. Launch `START.bat` and select Option **[2]** to generate speech. Choose your preferred voice. A natural voiceover will be generated as `audio/voiceover.mp3`.
3. Select Option **[3]** to generate image prompts. Select a visual style (e.g. Cinematic, Pixar). Your prompts will be saved to `prompt/image_prompts.txt`.

---

### **Step 4: Generate Images via Google Flow**
1. Open your **Google Flow** agent.
2. Open **`FlowAutomator_MasterPrompt.docx`** in this directory, copy its system prompt instructions, and paste them into your Flow Agent's instructions box.
3. Paste the prompts from `prompt/image_prompts.txt`. The agent will automatically generate images sequentially.
4. Download the generated files using a bulk downloader browser extension (like *Simple Mass Downloader*, *Tab Save*, etc.).

---

### **Step 5: Clean Up Image Names**
1. Place your downloaded images directly in the 📁 `images/` directory.
2. Launch `START.bat` and select Option **[1]** to clean filenames.
   *This extracts the leading number, pads it to 3 digits (e.g., `001`, `002`), removes all messy characters, and preserves the original file extension (even if there's a mix of PNG, JPG, JPEG, and WebP).*

---

### **Step 6: Render Your Video**
1. Select Option **[4]** in `START.bat` to configure options:
   * Toggle **Burnt-in Subtitles** (On/Off)
   * Toggle **Pan & Zoom** motion effects (On/Off)
   * Set **Resolution** (Landscape 16:9, Vertical 9:16 for YouTube Shorts, or Square 1:1)
   * Choose **Whisper Model**
2. Select Option **[5]** to compile and export your finished video! Once rendering finishes, find it in:
   📁 `output/`

---

## ❔ Handling Different Extensions

Our pipeline natively supports a mixture of image formats (**`.png`**, **`.jpg`**, **`.jpeg`**, and **`.webp`**). 
The `clean_images.py` script will clean their names (e.g. `002_image.jpg` ➔ `002.jpg`) while keeping their original extension. The rendering engine will automatically resize, letterbox, and transition between them smoothly regardless of format!

---

## ⚙️ Customization

For instructions on tweaking subtitle styling, changing transitions, swapping Whisper models, or enabling GPU acceleration, please refer to the **[Customization Guide](file:///e:/Python%20Programs/Vdo%20maker%20AI/custom.md)**.
