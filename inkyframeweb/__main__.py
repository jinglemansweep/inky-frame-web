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
from .slideshow import Slideshow
from .utils import setup_logger

config = Dynaconf(
    envvar_prefix=_APP_NAME.upper(),
    settings_files=["settings.toml", "settings.local.toml", "secrets.toml"],
    validators=VALIDATORS,
)

setup_logger(config)
logger = logging.getLogger(__name__)
logger.info(f"{_APP_TITLE} v{_APP_VERSION} starting up...")
logger.info(f"config: {config.as_dict()}")

app = Flask(__name__)

slideshows: List[Slideshow] = []

# image_files = glob_images(config.paths.images)
# slideshow = Slideshow(image_files, config.slideshow.delay)

for output in config.outputs.values():
    print(output.name, output)
    image_files = glob_images(Path(output.image_path))
    slideshows.append(
        Slideshow(
            image_files,
            (int(output.width), int(output.height)),
            output.delay,
            output.show_date,
            output.show_time,
            output.show_watermark,
        )
    )

show_date = True
show_time = True
show_watermark = True


@app.route("/")
def index():
    return redirect("/outputs/0")


@app.route("/outputs/<output>")
def handle_output(output: str):
    global slideshows
    if output not in config.outputs:
        return "Output not found", 404
    output_idx = int(output)
    slideshow = slideshows[output_idx]
    if slideshow.should_advance(int(datetime.now().timestamp())):
        slideshow.next()
    image_bytes = render_image(
        slideshow.image_file,
        config,
        slideshow.image_size,
        slideshow.show_date,
        slideshow.show_time,
        slideshow.show_watermark,
    )
    return build_response(image_bytes)


@app.route("/status/health")
def health():
    healthy = True
    return jsonify({"healthy": healthy})


if __name__ == "__main__":
    app.run(host=config.web.host, port=config.web.port, debug=config.general.debug)
