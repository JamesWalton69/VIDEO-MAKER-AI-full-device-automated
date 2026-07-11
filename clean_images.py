import os
import re
from pathlib import Path

# Folder path
BASE_DIR = Path(__file__).parent
IMAGES_DIR = BASE_DIR / "images"

def clean_image_filenames():
    """
    Cleans filenames in the 'images/' folder.
    - Extracts leading digits from the filename.
    - Pads them to 3 digits (e.g., 001, 002).
    - Preserves the original file extension (.png, .jpg, .jpeg, .webp, etc.).
    - Removes any extra characters between the digits and the extension.
    """
    if not IMAGES_DIR.exists():
        print(f"[ERROR] Directory '{IMAGES_DIR}' does not exist.")
        return

    print(f"Scanning '{IMAGES_DIR}' for images to clean up...\n")

    # Supported image extensions
    valid_extensions = {".png", ".jpg", ".jpeg", ".webp"}
    
    # List all files in the directory
    files = list(IMAGES_DIR.iterdir())
    
    renamed_count = 0
    skipped_count = 0
    
    # Process files
    for file_path in files:
        if file_path.is_dir():
            continue
            
        suffix = file_path.suffix.lower()
        if suffix not in valid_extensions:
            continue
            
        name = file_path.stem
        
        # Regex to find leading digits
        match = re.match(r"^(\d+)", name)
        if match:
            # Get the leading number and pad it to 3 digits
            num_str = match.group(1)
            padded_num = f"{int(num_str):03d}"
            
            # Construct the clean name
            new_filename = f"{padded_num}{suffix}"
            new_path = IMAGES_DIR / new_filename
            
            # If the name is already clean and correct, skip it
            if file_path.name == new_filename:
                skipped_count += 1
                continue
                
            # Handle collision: if the target name already exists, report it
            if new_path.exists():
                print(f"[WARNING] Cannot rename '{file_path.name}' to '{new_filename}' because '{new_filename}' already exists.")
                continue
                
            print(f"[RENAME] {file_path.name} -> {new_filename}")
            file_path.rename(new_path)
            renamed_count += 1
        else:
            print(f"[SKIP] No leading digits found in: '{file_path.name}'")
            skipped_count += 1

    print(f"\nDone! Renamed {renamed_count} files, skipped {skipped_count} files.")

if __name__ == "__main__":
    clean_image_filenames()
