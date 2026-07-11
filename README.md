========================================================================
                      VideoMaker - Auto Video Generator
                         Step-by-Step Instructions
========================================================================

Everything runs locally inside this folder. Follow the clear steps below
to generate your automated videos.

------------------------------------------------------------------------
STEP 1: FIRST-TIME SETUP (Do this once)
------------------------------------------------------------------------
1. Double-click "1_SETUP.bat".
   - This sets up a local virtual environment (".venv") inside this folder.
   - Installs all dependencies (Whisper, MoviePy, Pillow, etc.).
   - Automatically downloads FFmpeg into the "tools/" folder.
   - No global software or configuration changes are made to your computer!

------------------------------------------------------------------------
STEP 2: PREPARE YOUR AUDIO
------------------------------------------------------------------------
1. Drop your single audio file (MP3, WAV, M4A, AAC, FLAC, etc.) into:
   📂 audio\

------------------------------------------------------------------------
STEP 3: AUTOMATE IMAGE GENERATION (Using Google Flow)
------------------------------------------------------------------------
To generate and download all your images automatically with matching names:

1. OPEN GOOGLE FLOW:
   Open Google Flow (or your designated AI Flow Builder environment).

2. SET UP THE AGENT:
   - Open the "FlowAutomator_MasterPrompt.docx" file in this directory.
   - Copy its text contents (the Master Prompt/System Instructions).
   - Paste those instructions into your Flow Agent's System Prompt field.
   - This programs the agent to automate sequential bulk generation.

3. GENERATE IMAGES:
   - Provide your line-separated image prompts to the agent.
   - The agent will generate each image one by one and name them strictly:
     001.png, 002.png, 003.png, 004.png ...
     matching the exact prompt order.

4. AUTOMATIC DOWNLOAD:
   - Use an automated bulk downloader tool/extension (e.g., Simple Mass Downloader, Tab Save, or Flow's built-in file downloader) to download all the generated images automatically.

5. PLACE THE IMAGES:
   - Move the downloaded files (001.png, 002.png, 003.png, etc.) directly into:
     📂 images\

------------------------------------------------------------------------
STEP 4: RENDER THE VIDEO
------------------------------------------------------------------------
1. Double-click "2_RUN.bat".
   - It will automatically transcribe your audio using Whisper.
   - Save the subtitle timestamps as an SRT file in:
     📂 captions\
     (Tip: You can manually open and edit the .srt file if any auto-captions
      need tweaking, then re-run "2_RUN.bat" to apply them.)
   - Match each sequential image (001.png, 002.png...) to the captions.
   - Render and export the final video.

------------------------------------------------------------------------
STEP 5: FIND YOUR COMPLETED VIDEO
------------------------------------------------------------------------
1. Open the output directory to find your finished video:
   📂 output\

========================================================================
FOLDER STRUCTURE OVERVIEW
========================================================================
VideoMaker/
 ├── 1_SETUP.bat                  ← Double-click to run first-time install
 ├── 2_RUN.bat                    ← Double-click to transcribe and build video
 ├── FlowAutomator_MasterPrompt.docx ← Copy prompt from here into Google Flow
 ├── make_video.py                ← Core video generation engine
 ├── README.txt                   ← This instructions file
 ├── audio/                       ← Place your source audio here
 ├── images/                      ← Place your generated images (001.png...) here
 ├── captions/                    ← Auto-generated SRT captions appear here
 ├── output/                      ← Your final exported video will appear here
 └── tools/                       ← Portable FFmpeg binaries
========================================================================
