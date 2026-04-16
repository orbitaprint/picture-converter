import os

from PIL import Image

from app.utils.file_utils import ensure_directory, unique_path
from app.utils.logger import LOGGER


class ImageConversionError(Exception):
    pass


def convert_images_to_jpg(
    input_files,
    output_folder,
    quality,
    save_in_source,
    progress_callback=None,
):
    if not input_files:
        raise ImageConversionError("No input files selected.")

    converted_files = []
    errors = []
    total = len(input_files)

    for index, src_path in enumerate(input_files, start=1):
        try:
            src_dir = os.path.dirname(src_path)
            src_name = os.path.splitext(os.path.basename(src_path))[0]

            target_dir = src_dir if save_in_source else output_folder
            ensure_directory(target_dir)

            target_path = os.path.join(target_dir, "%s.jpg" % src_name)
            target_path = unique_path(target_path)

            with Image.open(src_path) as img:
                rgb_image = img.convert("RGB")
                rgb_image.save(target_path, format="JPEG", quality=int(quality), optimize=True)

            converted_files.append(target_path)
            LOGGER.info("Image converted: %s -> %s", src_path, target_path)
        except Exception as exc:
            error_message = "%s | %s" % (src_path, str(exc))
            errors.append(error_message)
            LOGGER.exception("Failed to convert image: %s", src_path)

        if progress_callback:
            progress_callback(index, total)

    return converted_files, errors
