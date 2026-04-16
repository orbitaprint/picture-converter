import re


class PageRangeError(ValueError):
    pass


def parse_page_ranges(text, max_pages):
    """
    Parse ranges like: 1-3,5,8-10
    Returns sorted unique zero-based indexes.
    """
    if max_pages <= 0:
        return []

    raw = (text or "").strip()
    if not raw:
        return list(range(max_pages))

    indexes = set()
    chunks = [c.strip() for c in raw.split(",") if c.strip()]
    if not chunks:
        raise PageRangeError("Page range is empty.")

    for chunk in chunks:
        if re.match(r"^\d+$", chunk):
            p = int(chunk)
            _validate_page_number(p, max_pages)
            indexes.add(p - 1)
            continue

        if re.match(r"^\d+\s*-\s*\d+$", chunk):
            left, right = [int(v.strip()) for v in chunk.split("-", 1)]
            _validate_page_number(left, max_pages)
            _validate_page_number(right, max_pages)
            if right < left:
                raise PageRangeError("Invalid range '%s': end is smaller than start." % chunk)
            for page in range(left, right + 1):
                indexes.add(page - 1)
            continue

        raise PageRangeError("Invalid token '%s'. Use format like 1-3,5,8-10." % chunk)

    return sorted(indexes)


def _validate_page_number(number, max_pages):
    if number < 1 or number > max_pages:
        raise PageRangeError("Page %s is out of bounds. PDF has %s pages." % (number, max_pages))
