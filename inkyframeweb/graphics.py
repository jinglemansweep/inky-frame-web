import io
from datetime import datetime
from dynaconf import Dynaconf
from pathlib import Path
from typing import List, Optional
from flask import send_file, make_response
from PIL import Image, ImageDraw, ImageFont
from werkzeug.http import generate_etag
from . import _APP_TITLE, _APP_VERSION

DATE_POSITION = (20, 20)
TIME_POSITION = (20, 80)


def glob_images(
    directory: Path,
    patterns: List[str] = ["*.jpg", "*.jpeg", "*.png", "*.gif"],
) -> List[Path]:
    # Glob all image files in the directory
    image_files: List[Path] = []
    for pattern in patterns:
        image_files.extend(directory.glob(pattern))
    return image_files


def load_and_resize_image(
    image_path: Path, size: tuple[int, int], aspect: str = "zoom"
) -> Image.Image:
    image = Image.open(image_path)
    if aspect == "zoom":
        image = resize_image_zoom(image, size)
    image = image.convert("RGB")
    return image


def resize_image_zoom(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    original_width, original_height = image.size
    new_width, new_height = size
    # Calculate aspect ratios
    original_aspect = original_width / original_height
    new_aspect = new_width / new_height
    # Determine scaling factor and resize
    if new_aspect > original_aspect:
        scale_factor = new_height / original_height
    else:
        scale_factor = new_width / original_width
    new_size = (int(original_width * scale_factor), int(original_height * scale_factor))
    image = image.resize(new_size, Image.LANCZOS)  # type: ignore[attr-defined]
    # Calculate coordinates for cropping
    left = int((new_size[0] - new_width) / 2)
    top = int((new_size[1] - new_height) / 2)
    right = left + new_width
    bottom = top + new_height
    # Crop the image to the desired size
    image = image.crop((left, top, right, bottom))
    return image


def bytes_to_pil(image_bytes):
    return Image.open(io.BytesIO(image_bytes))


def pil_to_bytes(
    image: Image.Image, image_format: str, progressive: bool, quality: int = 95
) -> io.BytesIO:
    image_bytes = io.BytesIO()
    image.save(
        image_bytes, format=image_format, progressive=progressive, quality=quality
    )
    image_bytes.seek(0)
    return image_bytes


def overlay_text(
    image: Image.Image,
    text: str,
    position: tuple[int, int] = (0, 0),
    font_path: str = "fonts/bitstream-vera.ttf",
    font_size: int = 24,
    anchor: str = "lt",
    align: str = "left",
    color: str = "black",
    stroke_color: Optional[str] = None,
    stroke_width: int = 0,
) -> None:
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_path, font_size)
    draw.text(
        position,
        text,
        font=font,
        anchor=anchor,
        align=align,
        fill=color,
        stroke_fill=stroke_color,
        stroke_width=stroke_width,
    )


def render_image(
    image_file: Path,
    config: Dynaconf,
    size: tuple[int, int],
    image_iter: int,
    image_index: int,
    image_count: int,
    overlay_x: int,
    overlay_y: int,
    overlay_size: int,
    overlay_format: str,
    overlay_color: str = "white",
) -> io.BytesIO:
    # Load and resize image
    image = load_and_resize_image(image_file, size, aspect="zoom")
    # Build overlay
    if not overlay_format == "":
        now = datetime.now()
        date_text = now.strftime(config.locale.date_format)
        time_text = now.strftime(config.locale.time_format)
        text = (
            overlay_format.replace("{date}", date_text)
            .replace("{time}", time_text)
            .replace("{loops}", str(image_iter + 1))
            .replace("{current}", str(image_index + 1))
            .replace("{total}", str(image_count))
        )
        overlay_text(
            image,
            text,
            (overlay_x, overlay_y),
            font_size=overlay_size,
            color=overlay_color,
            stroke_color="black",
            stroke_width=2,
        )
    # Return image bytes
    return pil_to_bytes(image, "JPEG", False, 50)


def build_response(image_bytes: io.BytesIO, mimetype: str = "image/jpeg"):
    response = make_response(send_file(image_bytes, mimetype=mimetype))
    response.set_etag(generate_etag(image_bytes.getvalue()))
    response.headers["X-Renderer"] = f"{_APP_TITLE} v{_APP_VERSION}"
    return response
