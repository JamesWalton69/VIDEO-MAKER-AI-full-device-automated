# 🎬 VideoMaker AI (Full Device Automated)

An elegant, fully automated pipeline that transcribes audio using OpenAI's Whisper model, matches captions to sequential images, and renders fully synchronized videos. Everything runs locally on your device with direct cloud integration!

---

## ✨ Features

- 🖥️ **Central Control Panel Dashboard**: Manage the entire pipeline interactively using a single launchpad file (`START.bat`).
- ✍️ **AI Script Writer & Generator**: Generate high-quality script texts based on a topic and exact target runtime in seconds.
- 🎙️ **Whisper AI Integration**: Automatic transcription with timestamped subtitles (`.srt`).
- 💬 **Karaoke-Style Subtitles**: Renders high-quality subtitles directly onto the video frames with active spoken word highlighting (yellow) and black shadows/outlines.
- 🗣️ **Realistic Text-To-Speech (TTS)**: Convert scripts in `prompt/script.txt` into natural-sounding voiceovers using warm neural voices (Andrew, Emma, Brian, Ava, William).
- 🖼️ **Pan & Zoom Transitions (Ken Burns)**: Give static slide images subtle, cinematic motion effects.
- 🤖 **Direct CLI Image Generation (Imagen 3 & Gemini 3.1)**: Generate and download high-quality **1k resolution** images directly from your terminal using your Google AI API key, matching your target aspect ratio.
- 🔗 **Google Flow Automation**: Auto-generate sequential prompts from your script with style boosters (Pixar, Cinematic, Anime, Custom, Educational Vector Explainer) for bulk creation.
- ⚡ **CPU Turbo Boost**: Run rendering with High Priority process allocation to utilize your CPU's maximum turbo frequency (up to 4.5 GHz).
- 🧹 **Filename Sanitizer**: Instantly clean messy filenames (e.g. `001_abcxyz.webp` ➔ `001.webp`) to keep formatting aligned.
- 🗑️ **Clean & Reset Utility**: Easily delete temp files, generated scripts, rendered videos, or perform a full workspace reset.

---

## 📁 Folder Structure

```text
VideoMaker/
 ├── START.bat                      # The interactive Dashboard Launcher (Double-click!)
 ├── 1_SETUP.bat                    # Setup virtual environment & dependencies
 ├── 2_RUN.bat                      # Run default video rendering directly
 ├── make_video.py                  # Core video rendering engine
 ├── launcher.py                    # Dashboard launcher source script
 ├── clean_images.py                # Image filename cleanup tool
 ├── generate_script.py             # Script generator from topic & runtime
 ├── generate_tts.py                # Neural TTS audio generator script
 ├── generate_prompts.py            # Prompt splitting and style booster script
 ├── generate_images_api.py         # Direct CLI image generator using Google GenAI API
 ├── FlowAutomator_MasterPrompt.docx# Prompt script for Google Flow Agent
 ├── audio/                         # Put your source audio here
 ├── images/                        # Put your numbered images here
 ├── captions/                      # Auto-generated SRT subtitles and word timestamps
 └── output/                        # Final synced video outputs
```

---

## 🚀 Step-by-Step Guide

### **Step 1: First-Time Setup**
Double-click **`1_SETUP.bat`**. This will:
* Set up a lightweight local Python virtual environment (`.venv`).
* Install all required dependencies (`openai-whisper`, `moviepy`, `pillow`, `edge-tts`, `google-genai`, etc.).
* Download a portable version of FFmpeg into the `tools/` folder.

---

### **Step 2: Launch the Control Panel**
Double-click **`START.bat`**. This launches the central console:
* It scans your setup and folders to display a live status update (audio found, script present, image counts, etc.).
* Offers an interactive menu where you can configure options, run helpers, or render videos.

---

### **Step 3: Write Script & Generate Voiceover**
If you want to build a video from scratch:
1. Select Option **`[2] Write / Generate Video Script`**. Enter your topic and target runtime in seconds.
2. The script computes the necessary length and automatically generates a narration script using your Gemini/OpenAI API key (or falls back to a template).
3. Select Option **`[3] Generate Audio via Text-To-Speech`**. Choose your preferred voice. A natural voiceover will be generated as `audio/voiceover.mp3`.
4. Select Option **`[4] Generate Image Prompts for Google Flow`** to generate image prompts, select a style (e.g. Cinematic, Pixar, or Educational Vector Explainer), and save them to `prompt/image_prompts.txt`.

---

### **Step 4: Generate Images (Google Cloud vs. Google Flow)**
You have two choices to generate images:

* **Choice A: Direct CLI Cloud Generation (Recommended)**
  1. Select Option **`[5] Generate Images via Google AI (Imagen 3) directly`**.
  2. Paste your Gemini API key (or it will reuse the one saved from Step 3).
  3. Select your aspect ratio and choice of model (e.g., Gemini 3.1 Flash Image, Gemini 3 Pro Image).
  4. The CLI will automatically generate and download high-quality **1k resolution** images directly to `images/` as `001.png`, `002.png`, etc.

* **Choice B: Google Flow Browser Automation**
  1. Open your **Google Flow** agent.
  2. Open **`FlowAutomator_MasterPrompt.docx`**, copy its system prompt instructions, and paste them into your Flow Agent's instructions box.
  3. Paste the prompts from `prompt/image_prompts.txt` and download the generated images.
  4. Place the images in the `images/` folder and select Option **`[1] Clean Image Filenames`** to clean the names to `001.png`, `002.png`, etc.

---

### **Step 5: Configure Settings & Render Video**
1. Select Option **`[6] Configure Rendering Settings`**:
   * Toggle **Burnt-in Subtitles** (On/Off)
   * Toggle **Pan & Zoom** motion effects (On/Off)
   * Set **Resolution** (Landscape 16:9, Vertical 9:16 for YouTube Shorts, or Square 1:1)
   * Choose **Whisper Model**
   * Toggle **Is Prompt Given** (On/Off) - *Synchronizes transcriptions line-by-line using similarity alignment.*
   * Toggle **CPU Turbo Boost** (On/Off) - *Runs at High Priority to hit max frequency (up to 4.5 GHz).*
2. Select Option **`[7] Render Video (Build output)`** to compile and export your finished video! Once rendering finishes, find it in:
   📁 `output/`

---

## ❔ Handling Different Extensions

Our pipeline natively supports a mixture of image formats (**`.png`**, **`.jpg`**, **`.jpeg`**, and **`.webp`**). The filename clean tool will sanitize their names while keeping their original extensions. The rendering engine will automatically resize, letterbox, and transition between them smoothly!

---

## ⚙️ Customization

For instructions on tweaking subtitle styling, changing transitions, swapping Whisper models, or enabling GPU acceleration, please refer to the **[Customization Guide](file:///e:/Python%20Programs/Vdo%20maker%20AI/custom.md)**.
