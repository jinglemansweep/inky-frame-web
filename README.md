# Inky Frame Web

![Inky Frame Web](./docs/logos/logo-medium.png)

[![docker](https://github.com/jinglemansweep/inky-frame-web/actions/workflows/docker.yml/badge.svg)](https://github.com/jinglemansweep/inky-frame-web/actions/workflows/docker.yml) [![mypy](https://github.com/jinglemansweep/inky-frame-web/actions/workflows/mypy.yml/badge.svg)](https://github.com/jinglemansweep/inky-frame-web/actions/workflows/mypy.yml) [![flake8](https://github.com/jinglemansweep/inky-frame-web/actions/workflows/flake8.yml/badge.svg)](https://github.com/jinglemansweep/inky-frame-web/actions/workflows/flake8.yml) [![black](https://github.com/jinglemansweep/inky-frame-web/actions/workflows/black.yml/badge.svg)](https://github.com/jinglemansweep/inky-frame-web/actions/workflows/black.yml) [![codeql](https://github.com/jinglemansweep/inky-frame-web/actions/workflows/codeql.yml/badge.svg)](https://github.com/jinglemansweep/inky-frame-web/actions/workflows/codeql.yml) [![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Web-based remote photo frame slideshow and gallery manager for use with e-ink displays such as the [Inky Frame](https://learn.pimoroni.com/article/getting-started-with-inky-frame). It might also be useful for the [Inky Impression](https://shop.pimoroni.com/products/inky-impression-5-7?variant=32298701324371) and other simple e-ink displays.

## Features

- :camera: Photo and image slideshow management
- :cinema: Multiple display output support
- :calendar: Customisable date and time overlays
- :snake: Written with [Python](https://www.python.org/), [Flask](https://flask.palletsprojects.com/) and [MicroPython](https://micropython.org/)

## Coming Soon

- :radio_button: Hardware button support
- :sunny: Weather summary and next hour forecast
- :incoming_envelope: Announcements and notifications via [MQTT](https://en.wikipedia.org/wiki/MQTT)
- :satellite: Remote control via MQTT and [Home Assistant](https://www.home-assistant.io/)

## Configuration

Project configuration is provided using [Dynaconf](https://www.dynaconf.com/), meaning that configuration can be provided using one or more TOML files, but can also be overridden at runtime using environment variables. For more information, see [`config.py`](./inkyframeweb/config.py).

The provided [`settings.toml`](./settings.toml) details all the available options, but they are all commented out. The preferred method of configuration is to override any settings by creating a `settings.local.toml` and/or a `secrets.toml` (for sensitive values), or by setting the equivalent `INKYFRAMEWEB_` environment variables.

### Outputs

TODO: Explain multiple outputs

## Server (Python)

### Docker

Pull and start the container image specifying a port and a volume for your photos/images:

    docker run -d --name inkyframeweb \
      -v ${PWD}/images/samples:/data/images \
      -p 5665:5665 \
      ghcr.io/jinglemansweep/inky-frame-web:main

Multiple display outputs can be specified using envionment variables. Remember outputs are zero-based:

    docker run -it --name inkyframeweb \
      -v ${PWD}/images/samples:/data/images \
      -e INKYFRAMEWEB_GENERAL__DEMO_MODE=true \
      -e INKYFRAMEWEB_OUTPUTS__0__IMAGE_PATH=images/samples \
      -e INKYFRAMEWEB_OUTPUTS__0__SHOW_DATE=true \
      -e INKYFRAMEWEB_OUTPUTS__1__IMAGE_PATH=images/samples \
      -e INKYFRAMEWEB_OUTPUTS__1__SHOW_DATE=true \
      -e INKYFRAMEWEB_OUTPUTS__1__SHOW_TIME=true \
      -p 5665:5665 \
      ghcr.io/jinglemansweep/inky-frame-web:main

### Native (Non-Docker)

Create a Python 3.x virtual environment, and install project dependencies:

    python3 -m venv venv
    . venv/bin/activate
    pip install --upgrade pip poetry
    poetry install

Create a `settings.local.toml` configuration file overriding any values required, or set the equivalent environment variables.

To run the project:

    . venv/bin/activate
    python3 -m inkyframeweb

## Client (MicroPython)

TODO

## Acknowledgements

- Sample photos generated and provided by [Dall-E 2](https://openai.com/index/dall-e-2/)
