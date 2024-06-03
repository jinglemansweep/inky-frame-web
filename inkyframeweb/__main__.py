import logging
from datetime import datetime
from dynaconf import Dynaconf
from flask import Flask, jsonify, redirect
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
        (int(output.width), int(output.height)),
        output.delay,
        output.show_date,
        output.show_time,
        output.show_watermark,
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
    output_idx = int(output)
    output_display = output_displays[output_idx]
    if output_display.should_advance(int(datetime.now().timestamp())):
        logger.info(f"Advancing Display: {output_display}")
        output_display.next()
    image_bytes = render_image(
        output_display.image_file,
        config,
        output_display.image_size,
        output_display.show_date,
        output_display.show_time,
        output_display.show_watermark,
    )
    return build_response(image_bytes)


@app.route("/status/health")
def health():
    healthy = True
    return jsonify({"healthy": healthy})


if __name__ == "__main__":
    app.run(host=config.web.host, port=config.web.port, debug=config.general.debug)
