from dynaconf import Validator
from pathlib import Path

VALIDATORS = [
    # General
    Validator("GENERAL__DEVICE_ID", default=None),
    Validator("GENERAL__DEBUG", default=False, cast=bool),
    Validator("GENERAL__LOG_LEVEL", default="info"),  # error, warning, info, debug
    # Display
    Validator(
        "DISPLAY__WIDTH",
        default=768,
        cast=int,
    ),
    Validator(
        "DISPLAY__HEIGHT",
        default=64,
        cast=int,
    ),
    # Slideshow
    Validator(
        "SLIDESHOW__DELAY",
        default=5,
        cast=int,
    ),
    # MQTT
    Validator(
        "MQTT__HOST",
        required=True,
        cast=str,
    ),
    Validator(
        "MQTT__PORT",
        default=1883,
        cast=int,
    ),
    Validator(
        "MQTT__TOPIC_PREFIX__APP",
        default="inkyframeweb",
        cast=str,
    ),
    Validator(
        "MQTT__TOPIC_PREFIX__HOMEASSISTANT__DEFAULT",
        default="homeassistant",
        cast=str,
    ),
    Validator(
        "MQTT__TOPIC_PREFIX__HOMEASSISTANT__STATESTREAM",
        default="homeassistant/statestream",
        cast=str,
    ),
    Validator(
        "MQTT__USER",
        default=None,
        cast=str,
    ),
    Validator(
        "MQTT__PASSWORD",
        default=None,
        cast=str,
    ),
    Validator(
        "MQTT__KEEPALIVE",
        default=60,
        cast=int,
    ),
    Validator(
        "MQTT__LOG_MESSAGES",
        default=False,
        cast=bool,
    ),
    # PATHS
    Validator(
        "PATHS__IMAGES",
        default="images",
        cast=Path,
    ),
]
