import tkinter as tk


def parse_drop_paths(event_data):
    """
    Parse Windows drop payload from TkDND.
    Handles paths with spaces wrapped in braces.
    """
    parser = tk.Tcl()
    try:
        return list(parser.tk.splitlist(event_data))
    except Exception:
        text = event_data.strip().strip("{}")
        return [text] if text else []
