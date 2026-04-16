import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from config import DEFAULT_JPG_QUALITY, MAX_JPG_QUALITY, MIN_JPG_QUALITY
from app.services.pdf_converter import convert_pdf_to_jpg
from app.utils.dnd import parse_drop_paths


class PdfToJpgTab(object):
    def __init__(self, parent, dnd_enabled, start_job_callback):
        self.frame = ttk.Frame(parent, padding=12)
        self.dnd_enabled = dnd_enabled
        self.start_job_callback = start_job_callback

        self.pdf_var = tk.StringVar(value="")
        self.output_var = tk.StringVar(value="")
        self.quality_var = tk.IntVar(value=DEFAULT_JPG_QUALITY)
        self.status_var = tk.StringVar(value="Ready")

        self._build_ui()

    def _build_ui(self):
        select_frame = ttk.LabelFrame(self.frame, text="PDF file", padding=8)
        select_frame.pack(fill="x")

        self.drop_label = ttk.Label(
            select_frame,
            text="Drag one PDF file here, or click Browse.",
            anchor="center",
            padding=14,
        )
        self.drop_label.grid(row=0, column=0, columnspan=3, sticky="ew")

        if self.dnd_enabled:
            try:
                self.drop_label.drop_target_register("DND_Files")
                self.drop_label.dnd_bind("<<Drop>>", self._on_drop)
            except Exception:
                pass

        ttk.Label(select_frame, text="PDF path:").grid(row=1, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(select_frame, textvariable=self.pdf_var).grid(row=1, column=1, sticky="ew", padx=6, pady=(8, 0))
        ttk.Button(select_frame, text="Browse", command=self._browse_pdf).grid(row=1, column=2, pady=(8, 0))

        ttk.Label(select_frame, text="Output folder:").grid(row=2, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(select_frame, textvariable=self.output_var).grid(row=2, column=1, sticky="ew", padx=6, pady=(8, 0))
        ttk.Button(select_frame, text="Browse", command=self._browse_output_folder).grid(row=2, column=2, pady=(8, 0))

        ttk.Label(select_frame, text="JPG quality (1-100):").grid(row=3, column=0, sticky="w", pady=(8, 0))
        ttk.Spinbox(
            select_frame,
            from_=MIN_JPG_QUALITY,
            to=MAX_JPG_QUALITY,
            textvariable=self.quality_var,
            width=8,
        ).grid(row=3, column=1, sticky="w", pady=(8, 0))

        select_frame.columnconfigure(1, weight=1)

        bottom = ttk.Frame(self.frame)
        bottom.pack(fill="x", pady=(12, 0))

        self.progress = ttk.Progressbar(bottom, mode="determinate", maximum=100)
        self.progress.pack(fill="x")

        ttk.Button(bottom, text="Convert PDF to JPG", command=self._start_conversion).pack(anchor="e", pady=(8, 0))
        ttk.Label(bottom, textvariable=self.status_var).pack(anchor="w")

    def _on_drop(self, event):
        paths = parse_drop_paths(event.data)
        if not paths:
            return
        first = paths[0].strip()
        if os.path.isfile(first) and first.lower().endswith(".pdf"):
            self.pdf_var.set(first)

    def _browse_pdf(self):
        path = filedialog.askopenfilename(title="Select PDF", filetypes=[("PDF", "*.pdf")])
        if path:
            self.pdf_var.set(path)

    def _browse_output_folder(self):
        folder = filedialog.askdirectory(title="Choose output folder")
        if folder:
            self.output_var.set(folder)

    def _update_progress(self, current, total):
        self.frame.after(0, self._set_progress, current, total)

    def _set_progress(self, current, total):
        percentage = int((float(current) / float(total)) * 100.0) if total else 0
        self.progress["value"] = percentage
        self.status_var.set("Converting... %s/%s" % (current, total))

    def _start_conversion(self):
        pdf_path = self.pdf_var.get().strip()
        output_folder = self.output_var.get().strip()
        quality = self.quality_var.get()

        if not pdf_path:
            messagebox.showwarning("PDF", "Please select a PDF file.")
            return

        if not output_folder:
            messagebox.showwarning("Output", "Please select an output folder.")
            return

        if quality < MIN_JPG_QUALITY or quality > MAX_JPG_QUALITY:
            messagebox.showwarning("Quality", "Quality must be between 1 and 100.")
            return

        self.progress["value"] = 0
        self.status_var.set("Starting conversion...")

        def worker():
            return convert_pdf_to_jpg(
                pdf_path=pdf_path,
                output_folder=output_folder,
                quality=quality,
                progress_callback=self._update_progress,
            )

        def on_success(output_files):
            self.progress["value"] = 100
            self.status_var.set("Done. %s page(s) exported." % len(output_files))
            messagebox.showinfo("Success", "PDF converted successfully.")

        def on_error(exc):
            self.status_var.set("Failed.")
            messagebox.showerror("Error", str(exc))

        self.start_job_callback(worker, on_success, on_error)
