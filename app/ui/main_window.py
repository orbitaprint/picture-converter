import os
import threading
try:
    import Queue as queue
except ImportError:
    import queue
import tkinter as tk
from tkinter import ttk

from config import APP_NAME, APP_VERSION, WINDOW_MIN_HEIGHT, WINDOW_MIN_WIDTH
from app.ui.tabs.image_to_jpg_tab import ImageToJpgTab
from app.ui.tabs.images_to_pdf_tab import ImagesToPdfTab
from app.ui.tabs.pdf_to_jpg_tab import PdfToJpgTab
from app.utils.logger import LOGGER


def _build_root_window():
    dnd_enabled = False

    try:
        from tkinterdnd2 import TkinterDnD
        root = TkinterDnD.Tk()
        dnd_enabled = True
    except Exception:
        root = tk.Tk()

    return root, dnd_enabled


class MainWindow(object):
    def __init__(self, root, dnd_enabled):
        self.root = root
        self.dnd_enabled = dnd_enabled
        self.work_queue = queue.Queue()

        self._configure_window()
        self._configure_style()
        self._build_layout()
        self._poll_queue()

    def _configure_window(self):
        self.root.title("%s %s" % (APP_NAME, APP_VERSION))
        self.root.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.root.geometry("980x700")

    def _configure_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        base_font = ("Segoe UI", 10)
        heading_font = ("Segoe UI", 11, "bold")

        self.root.option_add("*Font", base_font)

        style.configure("App.TFrame", background="#f4f6f8")
        style.configure("Card.TFrame", background="#ffffff", relief="flat")
        style.configure("TNotebook", background="#f4f6f8", borderwidth=0)
        style.configure("TNotebook.Tab", padding=(12, 8))
        style.configure("Title.TLabel", background="#f4f6f8", font=heading_font)
        style.configure("Hint.TLabel", background="#f4f6f8", foreground="#5c6b73")
        style.configure("Status.TLabel", background="#f4f6f8", foreground="#2f3e46")

    def _build_layout(self):
        container = ttk.Frame(self.root, style="App.TFrame", padding=14)
        container.pack(fill="both", expand=True)

        header = ttk.Frame(container, style="App.TFrame")
        header.pack(fill="x", pady=(0, 10))

        ttk.Label(header, text=APP_NAME, style="Title.TLabel").pack(anchor="w")

        dnd_text = (
            "Drag-and-drop is enabled."
            if self.dnd_enabled
            else "Drag-and-drop helper is not installed. Use Add Files buttons."
        )
        ttk.Label(header, text=dnd_text, style="Hint.TLabel").pack(anchor="w", pady=(2, 0))

        notebook = ttk.Notebook(container)
        notebook.pack(fill="both", expand=True)

        image_tab = ImageToJpgTab(notebook, self.dnd_enabled, self.start_job)
        pdf_create_tab = ImagesToPdfTab(notebook, self.dnd_enabled, self.start_job)
        pdf_to_jpg_tab = PdfToJpgTab(notebook, self.dnd_enabled, self.start_job)

        notebook.add(image_tab.frame, text="Image to JPG")
        notebook.add(pdf_create_tab.frame, text="Images to PDF")
        notebook.add(pdf_to_jpg_tab.frame, text="PDF to JPG")

    def start_job(self, worker, on_success, on_error):
        def _run_worker():
            try:
                result = worker()
                self.work_queue.put(("success", on_success, result))
            except Exception as exc:
                LOGGER.exception("Background task failed")
                self.work_queue.put(("error", on_error, exc))

        thread = threading.Thread(target=_run_worker)
        thread.daemon = True
        thread.start()

    def _poll_queue(self):
        try:
            while True:
                status, callback, payload = self.work_queue.get_nowait()
                callback(payload)
        except queue.Empty:
            pass
        self.root.after(100, self._poll_queue)


def run_app():
    root, dnd_enabled = _build_root_window()
    MainWindow(root, dnd_enabled)
    LOGGER.info("Application started. CWD=%s", os.getcwd())
    root.mainloop()
