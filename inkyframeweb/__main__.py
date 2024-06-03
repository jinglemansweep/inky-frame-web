from datetime import datetime
from dynaconf import Dynaconf
from flask import Flask, send_file, make_response
from werkzeug.http import generate_etag

from . import _APP_NAME
from .config import VALIDATORS
from .graphics import glob_images, load_and_resize_image

config = Dynaconf(
    envvar_prefix=_APP_NAME.upper(),
    settings_files=["settings.toml", "settings.local.toml", "secrets.toml"],
    validators=VALIDATORS,
)


print(config.as_dict())

app = Flask(__name__)

start_time = int(datetime.now().timestamp())
previous_time = start_time
delay_time = config.slideshow.delay

image_files = glob_images(config.paths.images)


class Slideshow:
    def __init__(self, image_files, delay_time=60):
        self.delay_time = delay_time
        self.image_files = image_files
        self.image_count = len(image_files)
        self.image_index = 0
        self.image_current = image_files[self.image_index]
        self.start_time = int(datetime.now().timestamp())
        self.previous_time = self.start_time

    def should_advance(self, now):
        advance = False
        diff = now - self.start_time
        if (diff % self.delay_time) == 0:
            if now != self.previous_time:
                self.previous_time = now
                advance = True
        return advance

    def next(self):
        self.image_index = (self.image_index + 1) % self.image_count

    @property
    def image_file(self):
        return self.image_files[self.image_index]


slideshow = Slideshow(image_files, config.slideshow.delay)


@app.route("/")
def home():
    now = int(datetime.now().timestamp())
    if slideshow.should_advance(now):
        slideshow.next()
    size = (800, 600)
    image_data = load_and_resize_image(slideshow.image_file, size)
    response = make_response(send_file(image_data, mimetype="image/jpeg"))
    response.set_etag(generate_etag(image_data.getvalue()))

    return response


if __name__ == "__main__":
    app.run()
