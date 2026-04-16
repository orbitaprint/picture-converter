import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from config import DEFAULT_JPG_QUALITY, MAX_JPG_QUALITY, MIN_JPG_QUALITY
from app.components.ui_kit import DropZone
from app.services.pdf_converter import convert_pdf_to_images
from app.styles.theme import Theme
from app.utils.dnd import parse_drop_paths


class PdfToJpgTab(object):
    def __init__(self, parent, dnd_enabled, start_job_callback, notifications):
        self.frame = ttk.Frame(parent, style="Surface.TFrame", padding=Theme.S12)
        self.dnd_enabled = dnd_enabled
        self.start_job_callback = start_job_callback
        self.notifications = notifications

        self.pdf_var = tk.StringVar(value="")
        self.output_var = tk.StringVar(value="")
        self.quality_var = tk.IntVar(value=DEFAULT_JPG_QUALITY)
        self.format_var = tk.StringVar(value="jpg")
        self.range_var = tk.StringVar(value="")
        self.pattern_var = tk.StringVar(value="page_{page:03d}")

        self._build_ui()

    def _build_ui(self):
        self.drop_zone = DropZone(self.frame, "Drop one PDF file here, or click to browse", on_click=self._pick_pdf)
        self.drop_zone.pack(fill="x", pady=(0, Theme.S12))

        if self.dnd_enabled:
            self.drop_zone.label.drop_target_register("DND_Files")
            self.drop_zone.label.dnd_bind("<<Drop>>", self._on_drop)

        card = ttk.LabelFrame(self.frame, text="Export options", style="Card.TLabelframe", padding=10)
        card.pack(fill="x")

        ttk.Label(card, text="PDF file").grid(row=0, column=0, sticky="w")
        ttk.Entry(card, textvariable=self.pdf_var).grid(row=0, column=1, sticky="ew", padx=Theme.S8)
        ttk.Button(card, text="Browse", style="Secondary.TButton", command=self._pick_pdf).grid(row=0, column=2)

        ttk.Label(card, text="Output folder").grid(row=1, column=0, sticky="w", pady=(Theme.S8, 0))
        ttk.Entry(card, textvariable=self.output_var).grid(row=1, column=1, sticky="ew", padx=Theme.S8, pady=(Theme.S8, 0))
        ttk.Button(card, text="Browse", style="Secondary.TButton", command=self._pick_output).grid(row=1, column=2, pady=(Theme.S8, 0))

        ttk.Label(card, text="Format").grid(row=2, column=0, sticky="w", pady=(Theme.S8, 0))
        ttk.Combobox(card, textvariable=self.format_var, values=["jpg", "png"], state="readonly", width=8).grid(row=2, column=1, sticky="w", pady=(Theme.S8, 0))

        ttk.Label(card, text="JPG quality").grid(row=3, column=0, sticky="w", pady=(Theme.S8, 0))
        ttk.Spinbox(card, from_=MIN_JPG_QUALITY, to=MAX_JPG_QUALITY, textvariable=self.quality_var, width=8).grid(row=3, column=1, sticky="w", pady=(Theme.S8, 0))

        ttk.Label(card, text="Page range").grid(row=4, column=0, sticky="w", pady=(Theme.S8, 0))
        ttk.Entry(card, textvariable=self.range_var).grid(row=4, column=1, sticky="ew", padx=Theme.S8, pady=(Theme.S8, 0))
        ttk.Label(card, text="Example: 1-3,5,8-10", style="Muted.TLabel").grid(row=4, column=2, sticky="w", pady=(Theme.S8, 0))

        ttk.Label(card, text="Naming pattern").grid(row=5, column=0, sticky="w", pady=(Theme.S8, 0))
        ttk.Entry(card, textvariable=self.pattern_var).grid(row=5, column=1, sticky="ew", padx=Theme.S8, pady=(Theme.S8, 0))
        ttk.Label(card, text="Use {page}, e.g. page_{page:03d}", style="Muted.TLabel").grid(row=5, column=2, sticky="w", pady=(Theme.S8, 0))

        card.columnconfigure(1, weight=1)

        footer = ttk.Frame(self.frame, style="Surface.TFrame")
        footer.pack(fill="x", pady=(Theme.S12, 0))

        self.progress = ttk.Progressbar(footer, mode="determinate", maximum=100)
        self.progress.pack(fill="x")
        ttk.Button(footer, text="Export PDF pages", style="Primary.TButton", command=self._start).pack(anchor="e", pady=(Theme.S8, 0))

    def _on_drop(self, event):
        paths = parse_drop_paths(event.data)
        if not paths:
            return
        first = paths[0].strip()
        if os.path.isfile(first) and first.lower().endswith(".pdf"):
            self.pdf_var.set(first)

    def _pick_pdf(self):
        path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if path:
            self.pdf_var.set(path)

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
        pdf_path = self.pdf_var.get().strip()
        output_folder = self.output_var.get().strip()
        quality = self.quality_var.get()

        if not pdf_path:
            messagebox.showwarning("PDF file", "Please select a PDF file.")
            return
        if not output_folder:
            messagebox.showwarning("Output folder", "Please select output folder.")
            return
        if quality < MIN_JPG_QUALITY or quality > MAX_JPG_QUALITY:
            messagebox.showwarning("Invalid quality", "Use a value from 1 to 100.")
            return

        self.progress["value"] = 0
        self.notifications.notify("Exporting pages...", "info")

        def worker():
            return convert_pdf_to_images(
                pdf_path=pdf_path,
                output_folder=output_folder,
                image_format=self.format_var.get(),
                quality=quality,
                naming_pattern=self.pattern_var.get().strip() or "page_{page:03d}",
                page_ranges=self.range_var.get().strip(),
                progress_callback=self._progress_callback,
            )

        def on_success(output_files):
            self.progress["value"] = 100
            self.notifications.notify("Exported %s image(s)." % len(output_files), "success")

        def on_error(exc):
            self.notifications.notify("PDF export failed.", "error")
            messagebox.showerror("Error", str(exc))

        self.start_job_callback(worker, on_success, on_error)
