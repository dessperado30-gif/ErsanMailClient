import tkinter as tk

def enable_dragdrop(widget, callback):
    def drop(event):
        files = widget.tk.splitlist(event.data)
        callback(files)

    widget.drop_target_register("DND_Files")
    widget.dnd_bind("<<Drop>>", drop)
