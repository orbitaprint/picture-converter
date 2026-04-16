from tkinter import ttk


class Theme(object):
    S4 = 4
    S8 = 8
    S12 = 12
    S16 = 16
    S24 = 24

    FONT_FAMILY = "Segoe UI"


THEMES = {
    "light": {
        "bg": "#f3f5f7",
        "surface": "#ffffff",
        "surface_alt": "#eef2f6",
        "text": "#1f2a37",
        "muted": "#617182",
        "primary": "#2b6de5",
        "primary_hover": "#215bc7",
        "border": "#d7dde5",
        "success": "#127a4a",
        "warning": "#a16207",
        "error": "#b42318",
    },
    "dark": {
        "bg": "#1b1f24",
        "surface": "#232931",
        "surface_alt": "#2f3842",
        "text": "#e6edf3",
        "muted": "#9aa7b3",
        "primary": "#3b82f6",
        "primary_hover": "#2f6fcb",
        "border": "#3a4652",
        "success": "#22a06b",
        "warning": "#d4a72c",
        "error": "#f47067",
    },
}


_CURRENT = THEMES["light"]


def colors():
    return _CURRENT


def apply_theme(root, mode="light"):
    global _CURRENT
    _CURRENT = THEMES.get(mode, THEMES["light"])
    c = _CURRENT

    style = ttk.Style()
    try:
        style.theme_use("clam")
    except Exception:
        pass

    root.configure(background=c["bg"])
    root.option_add("*Font", (Theme.FONT_FAMILY, 10))

    style.configure("App.TFrame", background=c["bg"])
    style.configure("Surface.TFrame", background=c["surface"], relief="flat")

    style.configure("TLabel", background=c["bg"], foreground=c["text"])
    style.configure("Muted.TLabel", background=c["bg"], foreground=c["muted"])
    style.configure("PanelTitle.TLabel", background=c["surface"], foreground=c["text"], font=(Theme.FONT_FAMILY, 11, "bold"))
    style.configure("PageTitle.TLabel", background=c["bg"], foreground=c["text"], font=(Theme.FONT_FAMILY, 15, "bold"))

    style.configure("TNotebook", background=c["bg"], borderwidth=0)
    style.configure("TNotebook.Tab", padding=(14, 10), font=(Theme.FONT_FAMILY, 10))
    style.map("TNotebook.Tab", background=[("selected", c["surface"]), ("!selected", c["surface_alt"])])

    style.configure("Primary.TButton", padding=(12, 8), relief="flat", foreground="#ffffff", background=c["primary"], borderwidth=0)
    style.map("Primary.TButton", background=[("active", c["primary_hover"]), ("pressed", c["primary_hover"])])

    style.configure("Secondary.TButton", padding=(10, 7), relief="flat", background=c["surface_alt"], bordercolor=c["border"])

    style.configure("TEntry", fieldbackground=c["surface"], bordercolor=c["border"], padding=6)
    style.configure("TCombobox", fieldbackground=c["surface"], padding=4)
    style.configure("TSpinbox", fieldbackground=c["surface"], padding=4)

    style.configure("Card.TLabelframe", background=c["surface"], bordercolor=c["border"], relief="solid", borderwidth=1)
    style.configure("Card.TLabelframe.Label", background=c["surface"], foreground=c["text"], font=(Theme.FONT_FAMILY, 10, "bold"))

    style.configure("Status.TLabel", background=c["bg"], foreground=c["muted"])
