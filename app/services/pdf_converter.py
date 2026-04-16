import os

from PIL import Image

from app.utils.file_utils import ensure_directory, unique_path
from app.utils.logger import LOGGER


class PdfConversionError(Exception):
    pass


def create_pdf_from_images(image_paths, output_pdf_path, progress_callback=None):
    if not image_paths:
        raise PdfConversionError("No images selected.")

    if not output_pdf_path:
        raise PdfConversionError("Output PDF path is required.")

    images = []
    try:
        total = len(image_paths)
        for index, path in enumerate(image_paths, start=1):
            with Image.open(path) as img:
                images.append(img.convert("RGB"))
            if progress_callback:
                progress_callback(index, total)

        first = images[0]
        rest = images[1:]

        first.save(output_pdf_path, save_all=True, append_images=rest)
        LOGGER.info("PDF created: %s", output_pdf_path)
    except Exception:
        LOGGER.exception("Failed creating PDF: %s", output_pdf_path)
        raise
    finally:
        for img in images:
            try:
                img.close()
            except Exception:
                pass


def convert_pdf_to_jpg(pdf_path, output_folder, quality, progress_callback=None):
    if not pdf_path:
        raise PdfConversionError("PDF path is required.")

    if not output_folder:
        raise PdfConversionError("Output folder is required.")

    ensure_directory(output_folder)

    try:
        import fitz
    except ImportError:
        message = (
            "PyMuPDF is not installed. Install it with: pip install PyMuPDF==1.24.10"
        )
        LOGGER.error(message)
        raise PdfConversionError(message)

    output_files = []

    try:
        doc = fitz.open(pdf_path)
        total = doc.page_count

        for page_index in range(total):
            page = doc.load_page(page_index)
            pix = page.get_pixmap(alpha=False)

            base_name = "page_%03d.jpg" % (page_index + 1)
            output_path = os.path.join(output_folder, base_name)
            output_path = unique_path(output_path)

            pix.save(output_path, jpg_quality=int(quality))
            output_files.append(output_path)

            if progress_callback:
                progress_callback(page_index + 1, total)

        doc.close()
        LOGGER.info("PDF converted: %s -> %s", pdf_path, output_folder)
    except Exception:
        LOGGER.exception("Failed converting PDF: %s", pdf_path)
        raise

    return output_files
