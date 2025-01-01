from PIL import Image, ExifTags
import os
import shutil
from tqdm import tqdm

def compress_image(image_path, output_path, quality):
    with Image.open(image_path) as img:
        # Fix orientation using EXIF data
        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == "Orientation":
                    break
            exif = img._getexif()
            if exif and orientation in exif:
                orientation_value = exif[orientation]
                if orientation_value == 3:
                    img = img.rotate(180, expand=True)
                elif orientation_value == 6:
                    img = img.rotate(270, expand=True)
                elif orientation_value == 8:
                    img = img.rotate(90, expand=True)
        except (AttributeError, KeyError, IndexError):
            # If the image has no EXIF data or the orientation tag is missing
            pass
        img.save(output_path, optimize=True, quality=quality)

if __name__ == "__main__":
    image_folder_path = './Images_Backup/Nov-Dec'
    output_path = './Images_Backup/Compressed'

    # Clear possible last run from output folder
    if os.path.exists(output_path):
        shutil.rmtree(output_path)
    os.makedirs(output_path, exist_ok=True)

    images = [img for img in os.listdir(image_folder_path) if img.lower().endswith('jpeg')]
    for img in tqdm(images):
        compress_image(os.path.join(image_folder_path, img), os.path.join(output_path, img), 25) #Manually change quality as desired
        