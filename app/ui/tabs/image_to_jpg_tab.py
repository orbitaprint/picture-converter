import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from config import DEFAULT_JPG_QUALITY, MAX_JPG_QUALITY, MIN_JPG_QUALITY, SUPPORTED_IMAGE_TO_JPG_INPUTS
from app.services.image_converter import convert_images_to_jpg
from app.utils.dnd import parse_drop_paths
from app.utils.file_utils import is_supported_extension


class ImageToJpgTab(object):
    def __init__(self, parent, dnd_enabled, start_job_callback):
        self.frame = ttk.Frame(parent, padding=12)
        self.dnd_enabled = dnd_enabled
        self.start_job_callback = start_job_callback
        self.files = []

        self.quality_var = tk.IntVar(value=DEFAULT_JPG_QUALITY)
        self.output_var = tk.StringVar(value="")
        self.same_folder_var = tk.BooleanVar(value=True)
        self.status_var = tk.StringVar(value="Ready")

        self._build_ui()

    def _build_ui(self):
        drop_frame = ttk.LabelFrame(self.frame, text="Input files", padding=8)
        drop_frame.pack(fill="x")

        self.drop_label = ttk.Label(
            drop_frame,
            text="Drag .png/.webp files here, or click Add Files.",
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

        actions = ttk.Frame(drop_frame)
        actions.pack(fill="x", pady=(8, 0))

        ttk.Button(actions, text="Add Files", command=self._add_files).pack(side="left")
        ttk.Button(actions, text="Remove Selected", command=self._remove_selected).pack(side="left", padx=6)
        ttk.Button(actions, text="Clear", command=self._clear_files).pack(side="left")

        self.file_list = tk.Listbox(self.frame, height=10)
        self.file_list.pack(fill="both", expand=True, pady=(10, 10))

        options = ttk.LabelFrame(self.frame, text="Output options", padding=8)
        options.pack(fill="x")

        ttk.Checkbutton(
            options,
            text="Save in same folder as source",
            variable=self.same_folder_var,
            command=self._toggle_output_folder_state,
        ).grid(row=0, column=0, columnspan=3, sticky="w")

        ttk.Label(options, text="Output folder:").grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.output_entry = ttk.Entry(options, textvariable=self.output_var)
        self.output_entry.grid(row=1, column=1, sticky="ew", pady=(8, 0), padx=6)
        self.output_button = ttk.Button(options, text="Browse", command=self._browse_output_folder)
        self.output_button.grid(row=1, column=2, pady=(8, 0))

        ttk.Label(options, text="JPG quality (1-100):").grid(row=2, column=0, sticky="w", pady=(8, 0))
        ttk.Spinbox(
            options,
            from_=MIN_JPG_QUALITY,
            to=MAX_JPG_QUALITY,
            textvariable=self.quality_var,
            width=8,
        ).grid(row=2, column=1, sticky="w", pady=(8, 0))

        options.columnconfigure(1, weight=1)

        bottom = ttk.Frame(self.frame)
        bottom.pack(fill="x", pady=(10, 0))

        self.progress = ttk.Progressbar(bottom, mode="determinate", maximum=100)
        self.progress.pack(fill="x")

        ttk.Button(bottom, text="Convert to JPG", command=self._start_conversion).pack(anchor="e", pady=(8, 0))
        ttk.Label(bottom, textvariable=self.status_var).pack(anchor="w")

        self._toggle_output_folder_state()

    def _on_drop(self, event):
        for path in parse_drop_paths(event.data):
            self._try_add_file(path)

    def _add_files(self):
        paths = filedialog.askopenfilenames(
            title="Select images",
            filetypes=[("Images", "*.png *.webp"), ("All files", "*.*")],
        )
        for path in paths:
            self._try_add_file(path)

    def _try_add_file(self, path):
        path = path.strip()
        if not os.path.isfile(path):
            return
        if not is_supported_extension(path, SUPPORTED_IMAGE_TO_JPG_INPUTS):
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

    def _toggle_output_folder_state(self):
        state = "disabled" if self.same_folder_var.get() else "normal"
        self.output_entry.configure(state=state)
        self.output_button.configure(state=state)

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
        if not self.files:
            messagebox.showwarning("No files", "Please add at least one image file.")
            return

        save_in_source = self.same_folder_var.get()
        output_folder = self.output_var.get().strip()

        if not save_in_source and not output_folder:
            messagebox.showwarning("Output folder", "Please choose an output folder.")
            return

        quality = self.quality_var.get()
        if quality < MIN_JPG_QUALITY or quality > MAX_JPG_QUALITY:
            messagebox.showwarning("Quality", "Quality must be between 1 and 100.")
            return

        self.progress["value"] = 0
        self.status_var.set("Starting conversion...")

        def worker():
            return convert_images_to_jpg(
                input_files=list(self.files),
                output_folder=output_folder,
                quality=quality,
                save_in_source=save_in_source,
                progress_callback=self._update_progress,
            )

        def on_success(result):
            converted_files, errors = result
            self.progress["value"] = 100
            self.status_var.set("Done. %s converted, %s failed." % (len(converted_files), len(errors)))
            if errors:
                messagebox.showwarning("Some files failed", "\n".join(errors[:10]))
            else:
                messagebox.showinfo("Success", "All files converted successfully.")

        def on_error(exc):
            self.status_var.set("Conversion failed.")
            messagebox.showerror("Error", str(exc))

        self.start_job_callback(worker, on_success, on_error)
