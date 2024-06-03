import io
from datetime import datetime
from dynaconf import Dynaconf
from pathlib import Path
from typing import List, Optional
from flask import send_file, make_response
from PIL import Image, ImageDraw, ImageFont
from werkzeug.http import generate_etag
from . import _APP_TITLE

DATE_POSITION = (20, 20)
TIME_POSITION = (20, 120)


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
    image = image.resize(size)
    image = image.convert("RGB")
    return image


def bytes_to_pil(image_bytes):
    return Image.open(io.BytesIO(image_bytes))


def pil_to_bytes(
    image: Image.Image, image_format: str, progressive: bool
) -> io.BytesIO:
    image_bytes = io.BytesIO()
    image.save(image_bytes, format=image_format, progressive=progressive)
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


def overlay_date(image: Image.Image, size: tuple[int, int], date_format: str) -> None:
    now = datetime.now()
    overlay_text(
        image,
        now.strftime(date_format),
        position=DATE_POSITION,
        font_size=48,
        align="center",
        color="white",
        stroke_color="black",
        stroke_width=4,
    )


def overlay_time(image: Image.Image, size: tuple[int, int], time_format: str) -> None:
    now = datetime.now()
    overlay_text(
        image,
        now.strftime(time_format),
        position=TIME_POSITION,
        font_size=72,
        align="center",
        color="white",
        stroke_color="black",
        stroke_width=4,
    )


def overlay_watermark(image: Image.Image, size: tuple[int, int]) -> None:
    # Overlay watermark
    overlay_text(
        image,
        _APP_TITLE,
        position=(size[0] - 120, size[1] - 18),
        font_size=14,
        color="yellow",
        stroke_color="black",
        stroke_width=2,
    )


def render_image(
    image_file: Path,
    config: Dynaconf,
    size: tuple[int, int],
    show_date: bool = True,
    show_time: bool = True,
    show_watermark: bool = True,
) -> io.BytesIO:
    # Load and resize image
    image = load_and_resize_image(image_file, size)
    # Overlay calendar and clock
    if show_date:
        overlay_date(image, size, config.locale.date_format)
    if show_time:
        overlay_time(image, size, config.locale.time_format)
    # Overlay watermark
    if show_watermark:
        overlay_watermark(image, size)
    # Return image bytes
    return pil_to_bytes(image, "JPEG", False)


def build_response(image_bytes: io.BytesIO, mimetype: str = "image/jpeg"):
    response = make_response(send_file(image_bytes, mimetype=mimetype))
    response.set_etag(generate_etag(image_bytes.getvalue()))
    return response
