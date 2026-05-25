THEMES = {
    "dark": {
        "bg": "#121212",
        "fg": "#ffffff",
        "accent": "#bb86fc"
    },
    "light": {
        "bg": "#ffffff",
        "fg": "#000000",
        "accent": "#6200ee"
    }
}

def apply_theme(widget, theme):
    colors = THEMES[theme]
    widget.configure(bg=colors["bg"], fg=colors["fg"])
    for child in widget.winfo_children():
        try:
            child.configure(bg=colors["bg"], fg=colors["fg"])
        except:
            pass
        apply_theme(child, theme)
