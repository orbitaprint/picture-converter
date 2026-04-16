import json
import os

from config import BASE_DIR

SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")

DEFAULT_SETTINGS = {
    "theme": "light",
    "last_output_folder": "",
    "pdf_export_format": "jpg",
    "jpg_quality": 90,
}


def load_settings():
    if not os.path.isfile(SETTINGS_FILE):
        return dict(DEFAULT_SETTINGS)
    try:
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)
    except Exception:
        return dict(DEFAULT_SETTINGS)

    merged = dict(DEFAULT_SETTINGS)
    merged.update(data)
    return merged


def save_settings(settings):
    payload = dict(DEFAULT_SETTINGS)
    payload.update(settings or {})
    with open(SETTINGS_FILE, "w") as f:
        json.dump(payload, f, indent=2)
