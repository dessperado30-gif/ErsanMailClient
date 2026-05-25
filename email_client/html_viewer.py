import tkinter as tk
from tkhtmlview import HTMLLabel

def show_html(parent, html_content):
    for widget in parent.winfo_children():
        widget.destroy()

    label = HTMLLabel(parent, html=html_content)
    label.pack(fill="both", expand=True)
