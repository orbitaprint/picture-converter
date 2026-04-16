import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from pypdf import PdfReader

from app.components.queue_model import FileQueueModel
from app.components.ui_kit import DropZone, FileListPanel
from app.services.pdf_tools import (
    delete_pages,
    extract_pages,
    get_metadata,
    merge_pdfs,
    rotate_pages,
    split_pdf,
    unlock_pdf,
    update_metadata,
)
from app.styles.theme import Theme
from app.utils.dnd import parse_drop_paths


class PdfToolkitTab(object):
    def __init__(self, parent, dnd_enabled, start_job_callback, notifications):
        self.frame = ttk.Frame(parent, style="Surface.TFrame", padding=Theme.S12)
        self.dnd_enabled = dnd_enabled
        self.start_job_callback = start_job_callback
        self.notifications = notifications

        self.merge_queue = FileQueueModel()

        self.selected_pdf_var = tk.StringVar(value="")
        self.page_range_var = tk.StringVar(value="")
        self.output_var = tk.StringVar(value="")
        self.password_var = tk.StringVar(value="")
        self.rotate_var = tk.IntVar(value=90)
        self.split_mode_var = tk.StringVar(value="every")

        self.meta_title_var = tk.StringVar(value="")
        self.meta_author_var = tk.StringVar(value="")
        self.meta_subject_var = tk.StringVar(value="")
        self.meta_keywords_var = tk.StringVar(value="")

        self.info_var = tk.StringVar(value="No document selected.")

        self._build_ui()

    def _build_ui(self):
        top = ttk.Frame(self.frame, style="Surface.TFrame")
        top.pack(fill="x")
        ttk.Label(top, text="PDF Toolkit", style="PanelTitle.TLabel").pack(anchor="w")
        ttk.Label(top, text="Merge, split, extract, rotate, delete pages, unlock, metadata.", style="Muted.TLabel").pack(anchor="w")

        section = ttk.LabelFrame(self.frame, text="A) Merge PDFs", style="Card.TLabelframe", padding=10)
        section.pack(fill="both", expand=True, pady=(Theme.S12, Theme.S8))

        self.drop_zone = DropZone(section, "Drop PDF files for merge, or click to add", on_click=self._add_merge_files)
        self.drop_zone.pack(fill="x")

        if self.dnd_enabled:
            self.drop_zone.label.drop_target_register("DND_Files")
            self.drop_zone.label.dnd_bind("<<Drop>>", self._on_merge_drop)

        row = ttk.Frame(section, style="Surface.TFrame")
        row.pack(fill="both", expand=True, pady=(Theme.S8, 0))

        self.merge_panel = FileListPanel(row, "Merge queue")
        self.merge_panel.pack(side="left", fill="both", expand=True)

        controls = ttk.Frame(row, style="Surface.TFrame")
        controls.pack(side="right", fill="y", padx=(Theme.S12, 0))
        ttk.Button(controls, text="Add", style="Secondary.TButton", command=self._add_merge_files).pack(fill="x")
        ttk.Button(controls, text="Up", style="Secondary.TButton", command=self._merge_up).pack(fill="x", pady=(Theme.S8, 0))
        ttk.Button(controls, text="Down", style="Secondary.TButton", command=self._merge_down).pack(fill="x", pady=(Theme.S8, 0))
        ttk.Button(controls, text="Remove", style="Secondary.TButton", command=self._merge_remove).pack(fill="x", pady=(Theme.S8, 0))
        ttk.Button(controls, text="Clear", style="Secondary.TButton", command=self._merge_clear).pack(fill="x", pady=(Theme.S8, 0))

        merge_actions = ttk.Frame(section, style="Surface.TFrame")
        merge_actions.pack(fill="x", pady=(Theme.S8, 0))
        ttk.Button(merge_actions, text="Merge to PDF", style="Primary.TButton", command=self._merge_start).pack(anchor="e")

        op = ttk.LabelFrame(self.frame, text="B) Edit / Extract / Split", style="Card.TLabelframe", padding=10)
        op.pack(fill="x", pady=(0, Theme.S8))

        ttk.Label(op, text="Input PDF").grid(row=0, column=0, sticky="w")
        ttk.Entry(op, textvariable=self.selected_pdf_var).grid(row=0, column=1, sticky="ew", padx=Theme.S8)
        ttk.Button(op, text="Browse", style="Secondary.TButton", command=self._pick_pdf).grid(row=0, column=2)

        ttk.Label(op, text="Page range").grid(row=1, column=0, sticky="w", pady=(Theme.S8, 0))
        ttk.Entry(op, textvariable=self.page_range_var).grid(row=1, column=1, sticky="ew", padx=Theme.S8, pady=(Theme.S8, 0))
        ttk.Label(op, text="Example: 1-3,5,8-10", style="Muted.TLabel").grid(row=1, column=2, sticky="w", pady=(Theme.S8, 0))

        ttk.Label(op, text="Split mode").grid(row=2, column=0, sticky="w", pady=(Theme.S8, 0))
        ttk.Combobox(op, textvariable=self.split_mode_var, values=["every", "ranges"], state="readonly", width=10).grid(row=2, column=1, sticky="w", pady=(Theme.S8, 0))

        ttk.Label(op, text="Rotate°").grid(row=3, column=0, sticky="w", pady=(Theme.S8, 0))
        ttk.Combobox(op, textvariable=self.rotate_var, values=[90, 180, 270], state="readonly", width=10).grid(row=3, column=1, sticky="w", pady=(Theme.S8, 0))

        actions = ttk.Frame(op, style="Surface.TFrame")
        actions.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(Theme.S12, 0))
        ttk.Button(actions, text="Split", style="Secondary.TButton", command=self._split_start).pack(side="left")
        ttk.Button(actions, text="Extract", style="Secondary.TButton", command=self._extract_start).pack(side="left", padx=(Theme.S8, 0))
        ttk.Button(actions, text="Rotate", style="Secondary.TButton", command=self._rotate_start).pack(side="left", padx=(Theme.S8, 0))
        ttk.Button(actions, text="Delete pages", style="Secondary.TButton", command=self._delete_start).pack(side="left", padx=(Theme.S8, 0))
        ttk.Button(actions, text="Unlock", style="Secondary.TButton", command=self._unlock_start).pack(side="left", padx=(Theme.S8, 0))

        ttk.Label(op, text="Password (for Unlock)").grid(row=5, column=0, sticky="w", pady=(Theme.S8, 0))
        ttk.Entry(op, textvariable=self.password_var, show="*").grid(row=5, column=1, sticky="ew", padx=Theme.S8, pady=(Theme.S8, 0))
        op.columnconfigure(1, weight=1)

        meta = ttk.LabelFrame(self.frame, text="C) Metadata & Document info", style="Card.TLabelframe", padding=10)
        meta.pack(fill="x")

        ttk.Label(meta, textvariable=self.info_var, style="Muted.TLabel").grid(row=0, column=0, columnspan=4, sticky="w")
        ttk.Button(meta, text="Refresh info", style="Secondary.TButton", command=self._refresh_info).grid(row=0, column=4, sticky="e")

        ttk.Label(meta, text="Title").grid(row=1, column=0, sticky="w", pady=(Theme.S8, 0))
        ttk.Entry(meta, textvariable=self.meta_title_var).grid(row=1, column=1, sticky="ew", padx=Theme.S8, pady=(Theme.S8, 0))
        ttk.Label(meta, text="Author").grid(row=1, column=2, sticky="w", pady=(Theme.S8, 0))
        ttk.Entry(meta, textvariable=self.meta_author_var).grid(row=1, column=3, sticky="ew", padx=Theme.S8, pady=(Theme.S8, 0))

        ttk.Label(meta, text="Subject").grid(row=2, column=0, sticky="w", pady=(Theme.S8, 0))
        ttk.Entry(meta, textvariable=self.meta_subject_var).grid(row=2, column=1, sticky="ew", padx=Theme.S8, pady=(Theme.S8, 0))
        ttk.Label(meta, text="Keywords").grid(row=2, column=2, sticky="w", pady=(Theme.S8, 0))
        ttk.Entry(meta, textvariable=self.meta_keywords_var).grid(row=2, column=3, sticky="ew", padx=Theme.S8, pady=(Theme.S8, 0))

        ttk.Button(meta, text="Save metadata", style="Primary.TButton", command=self._save_metadata).grid(row=3, column=4, sticky="e", pady=(Theme.S12, 0))

        meta.columnconfigure(1, weight=1)
        meta.columnconfigure(3, weight=1)

    def _pick_pdf(self):
        path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if path:
            self.selected_pdf_var.set(path)
            self._refresh_info()

    def _refresh_info(self):
        path = self.selected_pdf_var.get().strip()
        if not path or not os.path.isfile(path):
            self.info_var.set("No document selected.")
            return

        try:
            info = get_metadata(path)
            size_mb = os.path.getsize(path) / (1024.0 * 1024.0)
            self.info_var.set("%s | Pages: %s | Size: %.2f MB" % (os.path.basename(path), info["pages"], size_mb))
            self.meta_title_var.set(info["title"])
            self.meta_author_var.set(info["author"])
            self.meta_subject_var.set(info["subject"])
            self.meta_keywords_var.set(info["keywords"])
        except Exception as exc:
            self.notifications.notify("Failed to read metadata: %s" % str(exc), "error")

    def _on_merge_drop(self, event):
        for path in parse_drop_paths(event.data):
            if os.path.isfile(path) and path.lower().endswith(".pdf"):
                self.merge_queue.add(path)
        self._refresh_merge()

    def _add_merge_files(self):
        paths = filedialog.askopenfilenames(filetypes=[("PDF", "*.pdf")])
        for path in paths:
            self.merge_queue.add(path)
        self._refresh_merge()

    def _refresh_merge(self):
        self.merge_panel.set_items(self.merge_queue.items())
        self.notifications.notify("Merge queue: %s file(s)" % len(self.merge_queue.items()), "info")

    def _merge_remove(self):
        self.merge_queue.remove_indexes(self.merge_panel.listbox.curselection())
        self._refresh_merge()

    def _merge_clear(self):
        self.merge_queue.clear()
        self._refresh_merge()

    def _merge_up(self):
        selected = self.merge_panel.listbox.curselection()
        if selected:
            index = self.merge_queue.move_up(selected[0])
            self._refresh_merge()
            self.merge_panel.listbox.selection_set(index)

    def _merge_down(self):
        selected = self.merge_panel.listbox.curselection()
        if selected:
            index = self.merge_queue.move_down(selected[0])
            self._refresh_merge()
            self.merge_panel.listbox.selection_set(index)

    def _merge_start(self):
        output = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile="merged_document.pdf", filetypes=[("PDF", "*.pdf")])
        if not output:
            return

        files = self.merge_queue.items()
        if not files:
            messagebox.showwarning("Merge", "Please add PDF files.")
            return

        self.notifications.notify("Merging PDFs...", "info")

        def worker():
            return merge_pdfs(files, output)

        def on_success(_):
            self.notifications.notify("PDF merge completed.", "success")

        def on_error(exc):
            self.notifications.notify("PDF merge failed.", "error")
            messagebox.showerror("Error", str(exc))

        self.start_job_callback(worker, on_success, on_error)

    def _require_pdf(self):
        path = self.selected_pdf_var.get().strip()
        if not path:
            messagebox.showwarning("PDF", "Please select input PDF first.")
            return None
        return path

    def _split_start(self):
        pdf_path = self._require_pdf()
        if not pdf_path:
            return
        folder = filedialog.askdirectory(title="Output folder for split")
        if not folder:
            return

        self.notifications.notify("Splitting PDF...", "info")

        def worker():
            return split_pdf(pdf_path, folder, self.split_mode_var.get(), self.page_range_var.get().strip())

        def on_success(paths):
            self.notifications.notify("Split completed. %s file(s) created." % len(paths), "success")

        def on_error(exc):
            self.notifications.notify("Split failed.", "error")
            messagebox.showerror("Error", str(exc))

        self.start_job_callback(worker, on_success, on_error)

    def _extract_start(self):
        pdf_path = self._require_pdf()
        if not pdf_path:
            return
        out = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile="extracted_pages.pdf", filetypes=[("PDF", "*.pdf")])
        if not out:
            return

        self.notifications.notify("Extracting pages...", "info")

        def worker():
            return extract_pages(pdf_path, out, self.page_range_var.get().strip())

        def on_success(_):
            self.notifications.notify("Page extraction completed.", "success")

        def on_error(exc):
            self.notifications.notify("Extract failed.", "error")
            messagebox.showerror("Error", str(exc))

        self.start_job_callback(worker, on_success, on_error)

    def _rotate_start(self):
        pdf_path = self._require_pdf()
        if not pdf_path:
            return
        out = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile="rotated.pdf", filetypes=[("PDF", "*.pdf")])
        if not out:
            return

        self.notifications.notify("Rotating pages...", "info")

        def worker():
            return rotate_pages(pdf_path, out, int(self.rotate_var.get()), self.page_range_var.get().strip())

        def on_success(_):
            self.notifications.notify("Rotation completed.", "success")

        def on_error(exc):
            self.notifications.notify("Rotation failed.", "error")
            messagebox.showerror("Error", str(exc))

        self.start_job_callback(worker, on_success, on_error)

    def _delete_start(self):
        pdf_path = self._require_pdf()
        if not pdf_path:
            return
        out = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile="pages_deleted.pdf", filetypes=[("PDF", "*.pdf")])
        if not out:
            return

        self.notifications.notify("Deleting pages...", "info")

        def worker():
            return delete_pages(pdf_path, out, self.page_range_var.get().strip())

        def on_success(_):
            self.notifications.notify("Pages deleted successfully.", "success")

        def on_error(exc):
            self.notifications.notify("Delete pages failed.", "error")
            messagebox.showerror("Error", str(exc))

        self.start_job_callback(worker, on_success, on_error)

    def _unlock_start(self):
        pdf_path = self._require_pdf()
        if not pdf_path:
            return
        out = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile="unlocked.pdf", filetypes=[("PDF", "*.pdf")])
        if not out:
            return

        self.notifications.notify("Unlocking PDF...", "info")

        def worker():
            return unlock_pdf(pdf_path, out, self.password_var.get())

        def on_success(_):
            self.notifications.notify("PDF unlocked successfully.", "success")

        def on_error(exc):
            self.notifications.notify("Unlock failed.", "error")
            messagebox.showerror("Error", str(exc))

        self.start_job_callback(worker, on_success, on_error)

    def _save_metadata(self):
        pdf_path = self._require_pdf()
        if not pdf_path:
            return
        out = filedialog.asksaveasfilename(defaultextension=".pdf", initialfile="metadata_updated.pdf", filetypes=[("PDF", "*.pdf")])
        if not out:
            return

        self.notifications.notify("Saving metadata...", "info")

        def worker():
            return update_metadata(
                pdf_path,
                out,
                self.meta_title_var.get(),
                self.meta_author_var.get(),
                self.meta_subject_var.get(),
                self.meta_keywords_var.get(),
            )

        def on_success(_):
            self.notifications.notify("Metadata updated.", "success")

        def on_error(exc):
            self.notifications.notify("Metadata update failed.", "error")
            messagebox.showerror("Error", str(exc))

        self.start_job_callback(worker, on_success, on_error)
