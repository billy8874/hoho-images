import os
from PIL import Image, ImageOps
import pillow_heif

# Register HEIF opener
pillow_heif.register_heif_opener()

SOURCE_FOLDER = "raw"

def convert_heic_to_jpg():
    """
    Scans the 'raw' folder for HEIC/HEIF files and converts them to JPG format.
    The JPG files are saved in the same directory as the original HEIC files.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    source_dir = os.path.join(base_dir, SOURCE_FOLDER)

    if not os.path.exists(source_dir):
        print(f"❌ Source folder '{SOURCE_FOLDER}' not found!")
        return

    print(f"🚀 Starting HEIC to JPG conversion in '{SOURCE_FOLDER}'...")

    converted_count = 0
    skipped_count = 0

    for root, dirs, files in os.walk(source_dir):
        for filename in files:
            if filename.lower().endswith(('.heic', '.heif')):
                source_path = os.path.join(root, filename)
                
                # Target filename
                name_no_ext = os.path.splitext(filename)[0]
                new_filename = f"{name_no_ext}.jpg"
                target_path = os.path.join(root, new_filename)

                # Check if file already exists
                if os.path.exists(target_path):
                    # print(f"⏩ Skipped (already exists): {new_filename}")
                    skipped_count += 1
                    continue
                
                try:
                    with Image.open(source_path) as img:
                        # Fix orientation based on EXIF data
                        img = ImageOps.exif_transpose(img)
                        
                        # Convert to RGB (required for saving as JPEG)
                        if img.mode in ("RGBA", "P"):
                            img = img.convert("RGB")
                        
                        # Save as JPEG
                        img.save(target_path, "JPEG", quality=95)
                        print(f"✅ Converted: {filename} -> {new_filename}")
                        converted_count += 1
                except Exception as e:
                    print(f"❌ Error converting {filename}: {e}")

    print(f"\n📊 Summary: {converted_count} images converted, {skipped_count} skipped.")

if __name__ == "__main__":
    convert_heic_to_jpg()
