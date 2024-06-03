import logging
from datetime import datetime
from dynaconf import Dynaconf
from flask import Flask
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

image_files = glob_images(config.paths.images)
slideshow = Slideshow(image_files, config.slideshow.delay)


@app.route("/")
def home():
    if slideshow.should_advance(int(datetime.now().timestamp())):
        slideshow.next()
    image_bytes = render_image(slideshow.image_file, config)
    return build_response(image_bytes)


if __name__ == "__main__":
    app.run(host=config.web.host, port=config.web.port, debug=config.general.debug)
