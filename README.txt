============================================
  VideoMaker - Auto Video Generator
  Everything runs inside THIS folder only.
============================================

FIRST TIME SETUP (do this once):
---------------------------------
1. Double-click  1_SETUP.bat
   - Creates a local Python environment
   - Installs Whisper, MoviePy, Pillow
   - Downloads FFmpeg into the tools/ folder
   - Nothing touches the rest of your laptop!

HOW TO USE (every time):
--------------------------
STEP 1 — Drop your AUDIO file into:
         audio\
         (mp3, wav, m4a, aac, flac, ogg all work)

STEP 2 — Drop your IMAGES into:
         images\
         Name them in order: 001.png, 002.png, 003.png ...
         The order of images = order they appear in the video.
         Image 001 = Caption 1, Image 002 = Caption 2, etc.

STEP 3 — Double-click  2_RUN.bat
         It will:
         → Auto-transcribe your audio with Whisper (makes SRT)
         → Save the SRT file in captions\ (you can edit it!)
         → Match each image to its caption timestamp
         → Render the final video into output\

STEP 4 — Find your video in:
         output\

============================================
TIPS:
============================================
- If Whisper's auto-captions are slightly off, edit the
  .srt file in captions\ and re-run 2_RUN.bat.
  It will skip re-transcribing and use your edited SRT.

- Image naming: 001, 002, 003 ... 099, 100
  (use leading zeros so they sort correctly)

- If you have MORE images than captions, extras are ignored.
- If you have FEWER images than captions, the last image
  repeats for remaining captions.

- Output video is 1920x1080 (Full HD), 24fps.
  To change this, open make_video.py and edit:
    VIDEO_SIZE = (1920, 1080)
    FPS = 24

============================================
FOLDER STRUCTURE:
============================================
VideoMaker/
 ├── 1_SETUP.bat       ← Run once to install
 ├── 2_RUN.bat         ← Run every time to make video
 ├── make_video.py     ← Main script (don't delete)
 ├── README.txt        ← This file
 ├── audio/            ← Put your audio file here
 ├── images/           ← Put your numbered images here
 ├── captions/         ← SRT files appear here automatically
 ├── output/           ← Final video appears here
 └── tools/            ← FFmpeg lives here (auto-installed)
