import tkinter as tk
from tkinter import ttk

from app.styles.theme import Theme


class DropZone(ttk.Frame):
    def __init__(self, parent, text, on_click=None):
        ttk.Frame.__init__(self, parent, style="Surface.TFrame")
        self._text = text
        self._on_click = on_click

        self._box = tk.Frame(self, bd=1, relief="solid", bg=Theme.COLORS["surface_alt"], highlightthickness=0)
        self._box.pack(fill="x")

        self.label = tk.Label(
            self._box,
            text=text,
            bg=Theme.COLORS["surface_alt"],
            fg=Theme.COLORS["muted"],
            padx=12,
            pady=16,
            cursor="hand2",
            anchor="center",
        )
        self.label.pack(fill="x")

        self.label.bind("<Enter>", self._on_enter)
        self.label.bind("<Leave>", self._on_leave)
        self.label.bind("<Button-1>", self._on_click_event)

    def _on_enter(self, _event):
        self.label.configure(bg="#e2ebff", fg=Theme.COLORS["primary"])

    def _on_leave(self, _event):
        self.label.configure(bg=Theme.COLORS["surface_alt"], fg=Theme.COLORS["muted"])

    def _on_click_event(self, _event):
        if self._on_click:
            self._on_click()


class FileListPanel(ttk.Frame):
    def __init__(self, parent, title):
        ttk.Frame.__init__(self, parent, style="Surface.TFrame")

        frame = ttk.LabelFrame(self, text=title, style="Card.TLabelframe", padding=10)
        frame.pack(fill="both", expand=True)

        self.listbox = tk.Listbox(
            frame,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=Theme.COLORS["border"],
            selectbackground="#dbe8ff",
            selectforeground=Theme.COLORS["text"],
            activestyle="none",
            height=10,
        )
        self.listbox.pack(fill="both", expand=True)

    def set_items(self, items):
        self.listbox.delete(0, "end")
        for item in items:
            self.listbox.insert("end", item)


class InlineNotice(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent, style="App.TFrame")
        self.var = tk.StringVar(value="Ready")
        self.label = ttk.Label(self, textvariable=self.var, style="Status.TLabel")
        self.label.pack(anchor="w")

    def show(self, message, level="info"):
        color = Theme.COLORS["muted"]
        if level == "success":
            color = Theme.COLORS["success"]
        elif level == "error":
            color = Theme.COLORS["error"]
        elif level == "warning":
            color = Theme.COLORS["warning"]
        self.label.configure(foreground=color)
        self.var.set(message)
