import tkinter as tk
from tkinter import ttk

from app.styles.theme import colors


class DropZone(ttk.Frame):
    def __init__(self, parent, text, on_click=None):
        ttk.Frame.__init__(self, parent, style="Surface.TFrame")
        self._on_click = on_click

        c = colors()
        self._box = tk.Frame(self, bd=1, relief="solid", bg=c["surface_alt"], highlightthickness=0)
        self._box.pack(fill="x")

        self.label = tk.Label(
            self._box,
            text=text,
            bg=c["surface_alt"],
            fg=c["muted"],
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
        c = colors()
        self.label.configure(bg="#e2ebff" if c["bg"] != "#1b1f24" else "#2f4d74", fg=c["primary"])

    def _on_leave(self, _event):
        c = colors()
        self.label.configure(bg=c["surface_alt"], fg=c["muted"])

    def _on_click_event(self, _event):
        if self._on_click:
            self._on_click()


class FileListPanel(ttk.Frame):
    def __init__(self, parent, title):
        ttk.Frame.__init__(self, parent, style="Surface.TFrame")
        c = colors()

        frame = ttk.LabelFrame(self, text=title, style="Card.TLabelframe", padding=10)
        frame.pack(fill="both", expand=True)

        self.listbox = tk.Listbox(
            frame,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=c["border"],
            selectbackground="#dbe8ff" if c["bg"] != "#1b1f24" else "#3b4a5a",
            selectforeground=c["text"],
            activestyle="none",
            height=10,
            bg=c["surface"],
            fg=c["text"],
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
        c = colors()
        color = c["muted"]
        if level == "success":
            color = c["success"]
        elif level == "error":
            color = c["error"]
        elif level == "warning":
            color = c["warning"]
        self.label.configure(foreground=color)
        self.var.set(message)
