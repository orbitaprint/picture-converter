import os

from pypdf import PdfReader, PdfWriter

from app.utils.file_utils import ensure_directory, unique_path
from app.utils.page_ranges import parse_page_ranges


class PdfToolsError(Exception):
    pass


def merge_pdfs(input_files, output_file):
    if not input_files:
        raise PdfToolsError("Please add PDF files to merge.")

    writer = PdfWriter()
    for path in input_files:
        reader = PdfReader(path)
        for page in reader.pages:
            writer.add_page(page)

    _write_pdf(writer, output_file)
    return output_file


def split_pdf(pdf_path, output_folder, mode, ranges_text=""):
    reader = PdfReader(pdf_path)
    ensure_directory(output_folder)

    created = []
    if mode == "every":
        for i, page in enumerate(reader.pages):
            writer = PdfWriter()
            writer.add_page(page)
            out = unique_path(os.path.join(output_folder, "page_%03d.pdf" % (i + 1)))
            _write_pdf(writer, out)
            created.append(out)
        return created

    indexes = parse_page_ranges(ranges_text, len(reader.pages))
    if mode == "ranges":
        for idx in indexes:
            writer = PdfWriter()
            writer.add_page(reader.pages[idx])
            out = unique_path(os.path.join(output_folder, "page_%03d.pdf" % (idx + 1)))
            _write_pdf(writer, out)
            created.append(out)
        return created

    raise PdfToolsError("Unknown split mode.")


def extract_pages(pdf_path, output_file, ranges_text):
    reader = PdfReader(pdf_path)
    indexes = parse_page_ranges(ranges_text, len(reader.pages))

    writer = PdfWriter()
    for idx in indexes:
        writer.add_page(reader.pages[idx])

    _write_pdf(writer, output_file)
    return output_file


def rotate_pages(pdf_path, output_file, degrees, ranges_text=""):
    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    indexes = set(parse_page_ranges(ranges_text, len(reader.pages))) if ranges_text.strip() else set(range(len(reader.pages)))

    for idx, page in enumerate(reader.pages):
        if idx in indexes:
            page = page.rotate(degrees)
        writer.add_page(page)

    _write_pdf(writer, output_file)
    return output_file


def delete_pages(pdf_path, output_file, ranges_text):
    reader = PdfReader(pdf_path)
    delete_indexes = set(parse_page_ranges(ranges_text, len(reader.pages)))

    writer = PdfWriter()
    for idx, page in enumerate(reader.pages):
        if idx in delete_indexes:
            continue
        writer.add_page(page)

    if len(writer.pages) == 0:
        raise PdfToolsError("Cannot save empty PDF. You removed all pages.")

    _write_pdf(writer, output_file)
    return output_file


def unlock_pdf(pdf_path, output_file, password):
    reader = PdfReader(pdf_path)
    if reader.is_encrypted:
        result = reader.decrypt(password or "")
        if result == 0:
            raise PdfToolsError("Wrong password or unsupported encryption.")

    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    _write_pdf(writer, output_file)
    return output_file


def get_metadata(pdf_path):
    reader = PdfReader(pdf_path)
    meta = reader.metadata or {}
    return {
        "pages": len(reader.pages),
        "title": meta.get("/Title", ""),
        "author": meta.get("/Author", ""),
        "subject": meta.get("/Subject", ""),
        "keywords": meta.get("/Keywords", ""),
    }


def update_metadata(pdf_path, output_file, title, author, subject, keywords):
    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    metadata = {
        "/Title": title or "",
        "/Author": author or "",
        "/Subject": subject or "",
        "/Keywords": keywords or "",
    }
    writer.add_metadata(metadata)

    _write_pdf(writer, output_file)
    return output_file


def _write_pdf(writer, output_file):
    folder = os.path.dirname(output_file)
    if folder:
        ensure_directory(folder)
    with open(output_file, "wb") as f:
        writer.write(f)
