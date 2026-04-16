import tkinter as tk
from tkinter import ttk

from app.styles.theme import Theme, apply_theme
from app.utils.settings_store import save_settings


class SettingsTab(object):
    def __init__(self, parent, root, settings, notifications):
        self.frame = ttk.Frame(parent, style="Surface.TFrame", padding=Theme.S12)
        self.root = root
        self.settings = settings
        self.notifications = notifications

        self.theme_var = tk.StringVar(value=settings.get("theme", "light"))
        self.jpg_quality_var = tk.IntVar(value=settings.get("jpg_quality", 90))

        self._build_ui()

    def _build_ui(self):
        card = ttk.LabelFrame(self.frame, text="Appearance", style="Card.TLabelframe", padding=10)
        card.pack(fill="x")

        ttk.Label(card, text="Theme").grid(row=0, column=0, sticky="w")
        ttk.Combobox(card, textvariable=self.theme_var, values=["light", "dark"], state="readonly", width=10).grid(row=0, column=1, sticky="w", padx=Theme.S8)
        ttk.Button(card, text="Apply", style="Secondary.TButton", command=self._apply_theme).grid(row=0, column=2)

        conv = ttk.LabelFrame(self.frame, text="Defaults", style="Card.TLabelframe", padding=10)
        conv.pack(fill="x", pady=(Theme.S12, 0))
        ttk.Label(conv, text="Default JPG quality").grid(row=0, column=0, sticky="w")
        ttk.Spinbox(conv, from_=1, to=100, textvariable=self.jpg_quality_var, width=8).grid(row=0, column=1, sticky="w", padx=Theme.S8)

        ttk.Button(self.frame, text="Save settings", style="Primary.TButton", command=self._save).pack(anchor="e", pady=(Theme.S12, 0))

    def _apply_theme(self):
        self.settings["theme"] = self.theme_var.get()
        apply_theme(self.root, self.theme_var.get())
        self.notifications.notify("Theme applied. Restart app if any widget looks stale.", "info")

    def _save(self):
        self.settings["theme"] = self.theme_var.get()
        self.settings["jpg_quality"] = int(self.jpg_quality_var.get())
        save_settings(self.settings)
        self.notifications.notify("Settings saved.", "success")
