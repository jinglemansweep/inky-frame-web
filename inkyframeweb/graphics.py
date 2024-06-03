import io
from pathlib import Path
from typing import List
from PIL import Image


def glob_images(directory: Path, patterns=["*.jpg", "*.jpeg", "*.png", "*.gif"]):
    # Glob all image files in the directory
    image_files: List[Path] = []
    for pattern in patterns:
        image_files.extend(directory.glob(pattern))
    return image_files


def load_and_resize_image(image_path, size):
    # Load image from disk
    image = Image.open(image_path)
    # Resize image
    image = image.resize(size)
    # Convert image to non-progressive JPEG
    image = image.convert("RGB")
    # Save image to memory
    image_bytes = io.BytesIO()
    image.save(image_bytes, format="JPEG", progressive=False)
    image_bytes.seek(0)
    return image_bytes
