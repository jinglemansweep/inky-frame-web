import logging
from dynaconf import Dynaconf
from flask import Flask, jsonify, redirect, request
from pathlib import Path
from typing import List
from . import _APP_NAME, _APP_TITLE, _APP_VERSION
from .config import VALIDATORS
from .graphics import (
    glob_images,
    render_image,
    build_response,
)
from .outputs import OutputDisplay
from .utils import setup_logger

config = Dynaconf(
    envvar_prefix=_APP_NAME.upper(),
    settings_files=["settings.toml", "settings.local.toml", "secrets.toml"],
    validators=VALIDATORS,
)

setup_logger(config)
logger = logging.getLogger(__name__)
logger.info(f"{_APP_TITLE} v{_APP_VERSION} starting up...")
logger.debug(f"Configuration: {config.as_dict()}")

app = Flask(__name__)

output_displays: List[OutputDisplay] = []

for output in config.outputs.values():
    image_files = glob_images(Path(output.image_path))
    output_display = OutputDisplay(
        image_files,
        output.get("overlay_x", config.default.overlay_x),
        output.get("overlay_y", config.default.overlay_y),
        output.get("overlay_size", config.default.overlay_size),
        output.get("overlay_format", config.default.overlay_format),
        output.get("overlay_color", config.default.overlay_color),
    )
    logger.info(f"Output Display: {output_display}")
    output_displays.append(output_display)


@app.route("/")
def index():
    return redirect("/outputs/0")


@app.route("/outputs/<output>")
def handle_output(output: str):
    global slideshows
    if output not in config.outputs:
        return "Output not found", 404
    width = int(request.args.get("w", config.default.image_width))
    height = int(request.args.get("h", config.default.image_height))
    image_size = (width, height)
    output_idx = int(output)
    output_display = output_displays[output_idx]
    output_display.next()
    image_bytes = render_image(
        output_display.image_file,
        config,
        image_size,
        output_display.image_iter,
        output_display.image_index,
        output_display.image_count,
        output_display.overlay_x,
        output_display.overlay_y,
        output_display.overlay_size,
        output_display.overlay_format,
        output_display.overlay_color,
    )
    return build_response(image_bytes)


@app.route("/status/health")
def health():
    healthy = True
    return jsonify({"healthy": healthy})


if __name__ == "__main__":
    app.run(host=config.web.host, port=config.web.port, debug=config.general.debug)
