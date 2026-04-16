from tkinter import ttk


class Theme(object):
    # Spacing scale (4px grid)
    S4 = 4
    S8 = 8
    S12 = 12
    S16 = 16
    S24 = 24

    FONT_FAMILY = "Segoe UI"

    COLORS = {
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
    }


def apply_theme(root):
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except Exception:
        pass

    colors = Theme.COLORS
    root.configure(background=colors["bg"])
    root.option_add("*Font", (Theme.FONT_FAMILY, 10))

    style.configure("App.TFrame", background=colors["bg"])
    style.configure("Surface.TFrame", background=colors["surface"], relief="flat")

    style.configure("TLabel", background=colors["bg"], foreground=colors["text"])
    style.configure("Muted.TLabel", background=colors["bg"], foreground=colors["muted"])
    style.configure("PanelTitle.TLabel", background=colors["surface"], foreground=colors["text"], font=(Theme.FONT_FAMILY, 11, "bold"))
    style.configure("PageTitle.TLabel", background=colors["bg"], foreground=colors["text"], font=(Theme.FONT_FAMILY, 15, "bold"))

    style.configure("TNotebook", background=colors["bg"], borderwidth=0)
    style.configure("TNotebook.Tab", padding=(14, 10), font=(Theme.FONT_FAMILY, 10))
    style.map("TNotebook.Tab", background=[("selected", colors["surface"]), ("!selected", colors["surface_alt"])])

    style.configure("Primary.TButton", padding=(12, 8), relief="flat", foreground="#ffffff", background=colors["primary"], borderwidth=0)
    style.map("Primary.TButton", background=[("active", colors["primary_hover"]), ("pressed", colors["primary_hover"])])

    style.configure("Secondary.TButton", padding=(10, 7), relief="flat", background=colors["surface_alt"], bordercolor=colors["border"])

    style.configure("TEntry", fieldbackground="#ffffff", bordercolor=colors["border"], padding=6)
    style.configure("TCombobox", fieldbackground="#ffffff", padding=4)
    style.configure("TSpinbox", fieldbackground="#ffffff", padding=4)

    style.configure("Card.TLabelframe", background=colors["surface"], bordercolor=colors["border"], relief="solid", borderwidth=1)
    style.configure("Card.TLabelframe.Label", background=colors["surface"], foreground=colors["text"], font=(Theme.FONT_FAMILY, 10, "bold"))

    style.configure("Status.TLabel", background=colors["bg"], foreground=colors["muted"]) 
