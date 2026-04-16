import os

APP_NAME = "Picture Converter"
APP_VERSION = "1.1.0"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "app.log")

DEFAULT_JPG_QUALITY = 90
MIN_JPG_QUALITY = 1
MAX_JPG_QUALITY = 100

WINDOW_MIN_WIDTH = 980
WINDOW_MIN_HEIGHT = 680

SUPPORTED_IMAGE_INPUTS = (".png", ".webp", ".jpg", ".jpeg")
SUPPORTED_IMAGE_TO_JPG_INPUTS = (".png", ".webp")
