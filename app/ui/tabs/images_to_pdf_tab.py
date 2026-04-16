import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from config import SUPPORTED_IMAGE_INPUTS
from app.components.queue_model import FileQueueModel
from app.components.ui_kit import DropZone, FileListPanel
from app.services.pdf_converter import create_pdf_from_images
from app.styles.theme import Theme
from app.utils.dnd import parse_drop_paths
from app.utils.file_utils import is_supported_extension


class ImagesToPdfTab(object):
    def __init__(self, parent, dnd_enabled, start_job_callback, notifications):
        self.frame = ttk.Frame(parent, style="Surface.TFrame", padding=Theme.S12)
        self.dnd_enabled = dnd_enabled
        self.start_job_callback = start_job_callback
        self.notifications = notifications
        self.queue = FileQueueModel()

        self.output_var = tk.StringVar(value="")
        self._build_ui()

    def _build_ui(self):
        self.drop_zone = DropZone(
            self.frame,
            "Drop JPG/JPEG/PNG/WEBP files here, or click to add files",
            on_click=self._add_files,
        )
        self.drop_zone.pack(fill="x", pady=(0, Theme.S12))

        if self.dnd_enabled:
            self.drop_zone.label.drop_target_register("DND_Files")
            self.drop_zone.label.dnd_bind("<<Drop>>", self._on_drop)

        row = ttk.Frame(self.frame, style="Surface.TFrame")
        row.pack(fill="both", expand=True)

        self.panel = FileListPanel(row, "Pages order")
        self.panel.pack(side="left", fill="both", expand=True)

        controls = ttk.Frame(row, style="Surface.TFrame")
        controls.pack(side="right", fill="y", padx=(Theme.S12, 0))
        ttk.Button(controls, text="Add", style="Secondary.TButton", command=self._add_files).pack(fill="x")
        ttk.Button(controls, text="Remove", style="Secondary.TButton", command=self._remove_selected).pack(fill="x", pady=(Theme.S8, 0))
        ttk.Button(controls, text="Move Up", style="Secondary.TButton", command=self._move_up).pack(fill="x", pady=(Theme.S8, 0))
        ttk.Button(controls, text="Move Down", style="Secondary.TButton", command=self._move_down).pack(fill="x", pady=(Theme.S8, 0))
        ttk.Button(controls, text="Clear", style="Secondary.TButton", command=self._clear).pack(fill="x", pady=(Theme.S8, 0))

        output = ttk.LabelFrame(self.frame, text="Output", style="Card.TLabelframe", padding=10)
        output.pack(fill="x", pady=(Theme.S12, Theme.S8))

        ttk.Label(output, text="PDF file").grid(row=0, column=0, sticky="w")
        ttk.Entry(output, textvariable=self.output_var).grid(row=0, column=1, sticky="ew", padx=Theme.S8)
        ttk.Button(output, text="Browse", style="Secondary.TButton", command=self._pick_output).grid(row=0, column=2)
        output.columnconfigure(1, weight=1)

        footer = ttk.Frame(self.frame, style="Surface.TFrame")
        footer.pack(fill="x")
        self.progress = ttk.Progressbar(footer, mode="determinate", maximum=100)
        self.progress.pack(fill="x")
        ttk.Button(footer, text="Create PDF", style="Primary.TButton", command=self._start).pack(anchor="e", pady=(Theme.S8, 0))

    def _on_drop(self, event):
        for path in parse_drop_paths(event.data):
            self._add_path(path)
        self._refresh()

    def _add_files(self):
        paths = filedialog.askopenfilenames(filetypes=[("Images", "*.jpg *.jpeg *.png *.webp"), ("All files", "*.*")])
        for path in paths:
            self._add_path(path)
        self._refresh()

    def _add_path(self, path):
        path = path.strip()
        if not os.path.isfile(path):
            return
        if not is_supported_extension(path, SUPPORTED_IMAGE_INPUTS):
            return
        self.queue.add(path)

    def _refresh(self):
        self.panel.set_items(self.queue.items())
        self.notifications.notify("PDF queue: %s files" % len(self.queue.items()), "info")

    def _remove_selected(self):
        self.queue.remove_indexes(self.panel.listbox.curselection())
        self._refresh()

    def _move_up(self):
        selected = self.panel.listbox.curselection()
        if not selected:
            return
        idx = self.queue.move_up(selected[0])
        self._refresh()
        self.panel.listbox.selection_set(idx)

    def _move_down(self):
        selected = self.panel.listbox.curselection()
        if not selected:
            return
        idx = self.queue.move_down(selected[0])
        self._refresh()
        self.panel.listbox.selection_set(idx)

    def _clear(self):
        self.queue.clear()
        self._refresh()

    def _pick_output(self):
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF", "*.pdf")])
        if path:
            self.output_var.set(path)

    def _set_progress(self, current, total):
        value = int((float(current) / float(total)) * 100.0) if total else 0
        self.progress["value"] = value

    def _progress_callback(self, current, total):
        self.frame.after(0, self._set_progress, current, total)

    def _start(self):
        files = self.queue.items()
        output_pdf = self.output_var.get().strip()

        if not files:
            messagebox.showwarning("No files", "Please add at least one image.")
            return
        if not output_pdf:
            messagebox.showwarning("Output file", "Please select output PDF.")
            return

        self.progress["value"] = 0
        self.notifications.notify("Creating PDF...", "info")

        def worker():
            return create_pdf_from_images(files, output_pdf, self._progress_callback)

        def on_success(_):
            self.progress["value"] = 100
            self.notifications.notify("PDF created successfully.", "success")

        def on_error(exc):
            self.notifications.notify("PDF creation failed.", "error")
            messagebox.showerror("Error", str(exc))

        self.start_job_callback(worker, on_success, on_error)
