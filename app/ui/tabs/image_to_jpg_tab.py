import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from config import (
    DEFAULT_JPG_QUALITY,
    MAX_JPG_QUALITY,
    MIN_JPG_QUALITY,
    SUPPORTED_IMAGE_TO_JPG_INPUTS,
)
from app.components.queue_model import FileQueueModel
from app.components.ui_kit import DropZone, FileListPanel
from app.services.image_converter import convert_images_to_jpg
from app.styles.theme import Theme
from app.utils.dnd import parse_drop_paths
from app.utils.file_utils import is_supported_extension


class ImageToJpgTab(object):
    def __init__(self, parent, dnd_enabled, start_job_callback, notifications):
        self.frame = ttk.Frame(parent, style="Surface.TFrame", padding=Theme.S12)
        self.dnd_enabled = dnd_enabled
        self.start_job_callback = start_job_callback
        self.notifications = notifications
        self.queue = FileQueueModel()

        self.quality_var = tk.IntVar(value=DEFAULT_JPG_QUALITY)
        self.output_var = tk.StringVar(value="")
        self.same_folder_var = tk.BooleanVar(value=True)

        self._build_ui()

    def _build_ui(self):
        self.drop_zone = DropZone(
            self.frame,
            "Drop PNG/WEBP files here, or click to add files",
            on_click=self._add_files,
        )
        self.drop_zone.pack(fill="x", pady=(0, Theme.S12))

        if self.dnd_enabled:
            self.drop_zone.label.drop_target_register("DND_Files")
            self.drop_zone.label.dnd_bind("<<Drop>>", self._on_drop)

        list_row = ttk.Frame(self.frame, style="Surface.TFrame")
        list_row.pack(fill="both", expand=True)

        self.panel = FileListPanel(list_row, "Queue")
        self.panel.pack(side="left", fill="both", expand=True)

        actions = ttk.Frame(list_row, style="Surface.TFrame")
        actions.pack(side="right", fill="y", padx=(Theme.S12, 0))
        ttk.Button(actions, text="Add", style="Secondary.TButton", command=self._add_files).pack(fill="x")
        ttk.Button(actions, text="Remove", style="Secondary.TButton", command=self._remove_selected).pack(fill="x", pady=(Theme.S8, 0))
        ttk.Button(actions, text="Clear", style="Secondary.TButton", command=self._clear).pack(fill="x", pady=(Theme.S8, 0))

        settings = ttk.LabelFrame(self.frame, text="Output", style="Card.TLabelframe", padding=10)
        settings.pack(fill="x", pady=(Theme.S12, Theme.S8))

        ttk.Checkbutton(
            settings,
            text="Save next to source file",
            variable=self.same_folder_var,
            command=self._toggle_output_state,
        ).grid(row=0, column=0, columnspan=3, sticky="w")

        ttk.Label(settings, text="Output folder").grid(row=1, column=0, sticky="w", pady=(Theme.S8, 0))
        self.output_entry = ttk.Entry(settings, textvariable=self.output_var)
        self.output_entry.grid(row=1, column=1, sticky="ew", padx=Theme.S8, pady=(Theme.S8, 0))
        self.output_btn = ttk.Button(settings, text="Browse", style="Secondary.TButton", command=self._pick_output)
        self.output_btn.grid(row=1, column=2, pady=(Theme.S8, 0))

        ttk.Label(settings, text="JPG quality").grid(row=2, column=0, sticky="w", pady=(Theme.S8, 0))
        ttk.Spinbox(settings, from_=MIN_JPG_QUALITY, to=MAX_JPG_QUALITY, textvariable=self.quality_var, width=8).grid(row=2, column=1, sticky="w", pady=(Theme.S8, 0))
        settings.columnconfigure(1, weight=1)

        footer = ttk.Frame(self.frame, style="Surface.TFrame")
        footer.pack(fill="x")
        self.progress = ttk.Progressbar(footer, mode="determinate", maximum=100)
        self.progress.pack(fill="x")
        ttk.Button(footer, text="Convert to JPG", style="Primary.TButton", command=self._start).pack(anchor="e", pady=(Theme.S8, 0))

        self._toggle_output_state()

    def _on_drop(self, event):
        paths = parse_drop_paths(event.data)
        for path in paths:
            self._add_path(path)
        self._refresh()

    def _add_files(self):
        paths = filedialog.askopenfilenames(filetypes=[("Images", "*.png *.webp"), ("All files", "*.*")])
        for path in paths:
            self._add_path(path)
        self._refresh()

    def _add_path(self, path):
        path = path.strip()
        if not os.path.isfile(path):
            return
        if not is_supported_extension(path, SUPPORTED_IMAGE_TO_JPG_INPUTS):
            return
        self.queue.add(path)

    def _refresh(self):
        self.panel.set_items(self.queue.items())
        self.notifications.notify("Queued files: %s" % len(self.queue.items()), "info")

    def _remove_selected(self):
        self.queue.remove_indexes(self.panel.listbox.curselection())
        self._refresh()

    def _clear(self):
        self.queue.clear()
        self._refresh()

    def _toggle_output_state(self):
        state = "disabled" if self.same_folder_var.get() else "normal"
        self.output_entry.configure(state=state)
        self.output_btn.configure(state=state)

    def _pick_output(self):
        folder = filedialog.askdirectory(title="Choose output folder")
        if folder:
            self.output_var.set(folder)

    def _set_progress(self, current, total):
        value = int((float(current) / float(total)) * 100.0) if total else 0
        self.progress["value"] = value

    def _progress_callback(self, current, total):
        self.frame.after(0, self._set_progress, current, total)

    def _start(self):
        files = self.queue.items()
        if not files:
            messagebox.showwarning("No files", "Please add at least one image.")
            return

        quality = self.quality_var.get()
        if quality < MIN_JPG_QUALITY or quality > MAX_JPG_QUALITY:
            messagebox.showwarning("Invalid quality", "Use a value from 1 to 100.")
            return

        save_in_source = self.same_folder_var.get()
        output_folder = self.output_var.get().strip()
        if not save_in_source and not output_folder:
            messagebox.showwarning("Output folder", "Please choose output folder.")
            return

        self.progress["value"] = 0
        self.notifications.notify("Converting images...", "info")

        def worker():
            return convert_images_to_jpg(files, output_folder, quality, save_in_source, self._progress_callback)

        def on_success(result):
            converted, errors = result
            self.progress["value"] = 100
            if errors:
                self.notifications.notify("Converted %s files, %s failed." % (len(converted), len(errors)), "warning")
                messagebox.showwarning("Some files failed", "\n".join(errors[:10]))
            else:
                self.notifications.notify("Converted %s files." % len(converted), "success")

        def on_error(exc):
            self.notifications.notify("Image conversion failed.", "error")
            messagebox.showerror("Error", str(exc))

        self.start_job_callback(worker, on_success, on_error)
