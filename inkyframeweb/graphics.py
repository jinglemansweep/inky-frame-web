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
    directory: Path, patterns: List[str] = ["*.jpg", "*.jpeg", "*.png", "*.gif"]
) -> List[Path]:
    # Glob all image files in the directory
    image_files: List[Path] = []
    for pattern in patterns:
        image_files.extend(directory.glob(pattern))
    return image_files


def load_and_resize_image(image_path: Path, size: tuple[int, int]) -> Image.Image:
    image = Image.open(image_path)
    image = resize_image_aspect(image, size)
    image = image.convert("RGB")
    return image


def resize_image_aspect(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    original_width, original_height = image.size
    aspect_ratio = original_width / original_height

    target_width, target_height = size
    target_aspect_ratio = target_width / target_height

    if target_aspect_ratio > aspect_ratio:
        # The target image is wider than the original image, so we need to add black areas on the sides
        new_width = target_height * aspect_ratio
        new_height = target_height
        left = (target_width - new_width) // 2
        top = 0
    else:
        # The target image is taller than the original image, so we need to add black areas on the top and bottom
        new_width = target_width
        new_height = int(target_width / aspect_ratio)
        left = 0
        top = (target_height - new_height) // 2

    new_image = Image.new("RGB", size, color="black")
    new_image.paste(
        image.resize((int(new_width), int(new_height)), Image.LANCZOS),  # type: ignore[attr-defined]
        (int(left), int(top)),
    )
    return new_image


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
    image = load_and_resize_image(image_file, size)
    # Build overlay

    print("OVERLAY FORMAT", overlay_format)
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
