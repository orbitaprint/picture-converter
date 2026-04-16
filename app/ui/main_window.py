import threading
try:
    import Queue as queue
except ImportError:
    import queue
import tkinter as tk
from tkinter import ttk

from config import APP_NAME, APP_VERSION, WINDOW_MIN_HEIGHT, WINDOW_MIN_WIDTH
from app.components.notifications import NotificationCenter
from app.components.ui_kit import InlineNotice
from app.styles.theme import Theme, apply_theme
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
        self.jobs_queue = queue.Queue()
        self.notifications = NotificationCenter()

        self._build_window()
        self._poll_jobs()

    def _build_window(self):
        apply_theme(self.root)
        self.root.title("%s %s" % (APP_NAME, APP_VERSION))
        self.root.geometry("1020x720")
        self.root.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        page = ttk.Frame(self.root, style="App.TFrame", padding=Theme.S16)
        page.pack(fill="both", expand=True)

        header = ttk.Frame(page, style="App.TFrame")
        header.pack(fill="x", pady=(0, Theme.S12))

        ttk.Label(header, text=APP_NAME, style="PageTitle.TLabel").pack(anchor="w")
        helper = "Drag-and-drop enabled." if self.dnd_enabled else "Drag-and-drop unavailable. Use file pickers."
        ttk.Label(header, text=helper, style="Muted.TLabel").pack(anchor="w", pady=(2, 0))

        content = ttk.Frame(page, style="Surface.TFrame", padding=Theme.S12)
        content.pack(fill="both", expand=True)

        notebook = ttk.Notebook(content)
        notebook.pack(fill="both", expand=True)

        tabs = [
            ("Image → JPG", ImageToJpgTab),
            ("Images → PDF", ImagesToPdfTab),
            ("PDF → JPG", PdfToJpgTab),
        ]
        for title, klass in tabs:
            tab = klass(notebook, self.dnd_enabled, self.start_job, self.notifications)
            notebook.add(tab.frame, text=title)

        footer = ttk.Frame(page, style="App.TFrame")
        footer.pack(fill="x", pady=(Theme.S8, 0))

        self.status_line = InlineNotice(footer)
        self.status_line.pack(fill="x")
        self.notifications.subscribe(self._on_notification)

    def _on_notification(self, message, level):
        self.status_line.show(message, level)
        if level in ("success", "warning"):
            self.root.after(3200, lambda: self.status_line.show("Ready", "info"))

    def start_job(self, worker, on_success, on_error):
        def _run_worker():
            try:
                result = worker()
                self.jobs_queue.put((on_success, result, None))
            except Exception as exc:
                LOGGER.exception("Background task failed")
                self.jobs_queue.put((on_error, None, exc))

        t = threading.Thread(target=_run_worker)
        t.daemon = True
        t.start()

    def _poll_jobs(self):
        try:
            while True:
                callback, result, error = self.jobs_queue.get_nowait()
                payload = error if error else result
                callback(payload)
        except queue.Empty:
            pass
        self.root.after(80, self._poll_jobs)


def run_app():
    root, dnd_enabled = _build_root_window()
    MainWindow(root, dnd_enabled)
    LOGGER.info("Application started")
    root.mainloop()
