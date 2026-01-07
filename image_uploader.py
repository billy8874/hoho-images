import os
import subprocess
from PIL import Image, ImageOps
from datetime import datetime

# --- Configuration ---
# Source and Destination folders
SOURCE_FOLDER = "raw"
UPLOAD_FOLDER = "upload"

# Image settings
MAX_WIDTH = 1200
QUALITY = 80

def process_and_upload():
    # Base directory (where the script is located)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    source_dir = os.path.join(base_dir, SOURCE_FOLDER)
    upload_dir = os.path.join(base_dir, UPLOAD_FOLDER)

    if not os.path.exists(source_dir):
        print(f"❌ Source folder '{SOURCE_FOLDER}' not found!")
        return

    print(f"🚀 Starting image processing from '{SOURCE_FOLDER}' to '{UPLOAD_FOLDER}'...")
    
    processed_count = 0
    
    # Walk through the raw directory
    for root, dirs, files in os.walk(source_dir):
        for filename in files:
            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                source_path = os.path.join(root, filename)
                
                # Calculate relative path to preserve structure
                rel_path = os.path.relpath(root, source_dir)
                target_subdir = os.path.join(upload_dir, rel_path)
                
                # Ensure target subdirectory exists
                os.makedirs(target_subdir, exist_ok=True)
                
                # New filename with .webp extension
                name_no_ext = os.path.splitext(filename)[0]
                new_filename = f"{name_no_ext}.webp"
                target_path = os.path.join(target_subdir, new_filename)
                
                # Process image
                try:
                    with Image.open(source_path) as img:
                        # Fix orientation based on EXIF data
                        img = ImageOps.exif_transpose(img)

                        # Convert to RGB (fixes PNG transparency issues)
                        if img.mode in ("RGBA", "P"):
                            img = img.convert("RGB")
                        
                        # Resize if larger than MAX_WIDTH
                        if img.width > MAX_WIDTH:
                            ratio = MAX_WIDTH / float(img.width)
                            new_height = int(float(img.height) * ratio)
                            img = img.resize((MAX_WIDTH, new_height), Image.Resampling.LANCZOS)
                        
                        # Save as WebP
                        img.save(target_path, "WEBP", quality=QUALITY)
                        print(f"✅ Processed: {os.path.join(rel_path, filename)} -> {new_filename}")
                        processed_count += 1
                except Exception as e:
                    print(f"❌ Error processing {filename}: {e}")

    if processed_count == 0:
        print("⚠️ No images found to process.")
        return

    # --- Git Automation ---
    print("\n📦 Syncing to git...")
    try:
        # Run git commands in the current directory
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", f"Upload photos: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("\n✨ All done! Images uploaded successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Git command failed: {e}")
    except Exception as e:
        print(f"❌ An error occurred during git sync: {e}")

if __name__ == "__main__":
    process_and_upload()