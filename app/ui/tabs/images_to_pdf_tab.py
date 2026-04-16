import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from config import SUPPORTED_IMAGE_INPUTS
from app.services.pdf_converter import create_pdf_from_images
from app.utils.dnd import parse_drop_paths
from app.utils.file_utils import is_supported_extension


class ImagesToPdfTab(object):
    def __init__(self, parent, dnd_enabled, start_job_callback):
        self.frame = ttk.Frame(parent, padding=12)
        self.dnd_enabled = dnd_enabled
        self.start_job_callback = start_job_callback
        self.files = []

        self.output_var = tk.StringVar(value="")
        self.status_var = tk.StringVar(value="Ready")

        self._build_ui()

    def _build_ui(self):
        top = ttk.LabelFrame(self.frame, text="Images", padding=8)
        top.pack(fill="x")

        self.drop_label = ttk.Label(
            top,
            text="Drag image files here, or click Add Images.",
            anchor="center",
            padding=14,
        )
        self.drop_label.pack(fill="x")

        if self.dnd_enabled:
            try:
                self.drop_label.drop_target_register("DND_Files")
                self.drop_label.dnd_bind("<<Drop>>", self._on_drop)
            except Exception:
                pass

        actions = ttk.Frame(top)
        actions.pack(fill="x", pady=(8, 0))
        ttk.Button(actions, text="Add Images", command=self._add_files).pack(side="left")
        ttk.Button(actions, text="Remove Selected", command=self._remove_selected).pack(side="left", padx=6)
        ttk.Button(actions, text="Move Up", command=self._move_up).pack(side="left")
        ttk.Button(actions, text="Move Down", command=self._move_down).pack(side="left", padx=6)
        ttk.Button(actions, text="Clear", command=self._clear_files).pack(side="left")

        self.file_list = tk.Listbox(self.frame, height=12)
        self.file_list.pack(fill="both", expand=True, pady=(10, 10))

        output_frame = ttk.LabelFrame(self.frame, text="Output", padding=8)
        output_frame.pack(fill="x")

        ttk.Label(output_frame, text="PDF file path:").grid(row=0, column=0, sticky="w")
        ttk.Entry(output_frame, textvariable=self.output_var).grid(row=0, column=1, sticky="ew", padx=6)
        ttk.Button(output_frame, text="Browse", command=self._browse_output_file).grid(row=0, column=2)
        output_frame.columnconfigure(1, weight=1)

        bottom = ttk.Frame(self.frame)
        bottom.pack(fill="x", pady=(10, 0))

        self.progress = ttk.Progressbar(bottom, mode="determinate", maximum=100)
        self.progress.pack(fill="x")

        ttk.Button(bottom, text="Create PDF", command=self._start_create_pdf).pack(anchor="e", pady=(8, 0))
        ttk.Label(bottom, textvariable=self.status_var).pack(anchor="w")

    def _on_drop(self, event):
        for path in parse_drop_paths(event.data):
            self._try_add_file(path)

    def _add_files(self):
        paths = filedialog.askopenfilenames(
            title="Select images",
            filetypes=[("Images", "*.jpg *.jpeg *.png *.webp"), ("All files", "*.*")],
        )
        for path in paths:
            self._try_add_file(path)

    def _try_add_file(self, path):
        path = path.strip()
        if not os.path.isfile(path):
            return
        if not is_supported_extension(path, SUPPORTED_IMAGE_INPUTS):
            return
        if path in self.files:
            return

        self.files.append(path)
        self.file_list.insert("end", path)

    def _remove_selected(self):
        selected = list(self.file_list.curselection())
        selected.reverse()
        for index in selected:
            self.file_list.delete(index)
            del self.files[index]

    def _clear_files(self):
        self.files = []
        self.file_list.delete(0, "end")

    def _move_up(self):
        selected = self.file_list.curselection()
        if not selected or selected[0] == 0:
            return
        index = selected[0]
        self.files[index - 1], self.files[index] = self.files[index], self.files[index - 1]
        self._refresh_listbox(index - 1)

    def _move_down(self):
        selected = self.file_list.curselection()
        if not selected or selected[0] >= len(self.files) - 1:
            return
        index = selected[0]
        self.files[index + 1], self.files[index] = self.files[index], self.files[index + 1]
        self._refresh_listbox(index + 1)

    def _refresh_listbox(self, selected_index):
        self.file_list.delete(0, "end")
        for item in self.files:
            self.file_list.insert("end", item)
        self.file_list.selection_set(selected_index)

    def _browse_output_file(self):
        path = filedialog.asksaveasfilename(
            title="Save PDF",
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
        )
        if path:
            self.output_var.set(path)

    def _update_progress(self, current, total):
        self.frame.after(0, self._set_progress, current, total)

    def _set_progress(self, current, total):
        percentage = int((float(current) / float(total)) * 100.0) if total else 0
        self.progress["value"] = percentage
        self.status_var.set("Processing... %s/%s" % (current, total))

    def _start_create_pdf(self):
        if not self.files:
            messagebox.showwarning("No images", "Please add at least one image.")
            return

        output_pdf = self.output_var.get().strip()
        if not output_pdf:
            messagebox.showwarning("Output path", "Please choose an output PDF path.")
            return

        self.progress["value"] = 0
        self.status_var.set("Creating PDF...")

        def worker():
            return create_pdf_from_images(
                image_paths=list(self.files),
                output_pdf_path=output_pdf,
                progress_callback=self._update_progress,
            )

        def on_success(_):
            self.progress["value"] = 100
            self.status_var.set("Done.")
            messagebox.showinfo("Success", "PDF created successfully.")

        def on_error(exc):
            self.status_var.set("Failed.")
            messagebox.showerror("Error", str(exc))

        self.start_job_callback(worker, on_success, on_error)
