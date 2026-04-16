import os


def ensure_directory(path):
    if path and not os.path.isdir(path):
        os.makedirs(path)


def unique_path(path):
    """Return a non-colliding file path by appending _1, _2, ..."""
    if not os.path.exists(path):
        return path

    folder = os.path.dirname(path)
    filename = os.path.basename(path)
    base, ext = os.path.splitext(filename)

    index = 1
    while True:
        candidate = os.path.join(folder, "%s_%s%s" % (base, index, ext))
        if not os.path.exists(candidate):
            return candidate
        index += 1


def is_supported_extension(path, allowed_extensions):
    return os.path.splitext(path)[1].lower() in allowed_extensions
