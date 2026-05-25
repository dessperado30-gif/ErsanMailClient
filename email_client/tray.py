import pystray
from PIL import Image, ImageDraw

def create_icon():
    img = Image.new("RGB", (64, 64), "black")
    d = ImageDraw.Draw(img)
    d.ellipse((8, 8, 56, 56), fill="white")
    return img

def run_tray(on_quit):
    icon = pystray.Icon("MailClient", create_icon(), "Mail Client", menu=pystray.Menu(
        pystray.MenuItem("Beenden", lambda: on_quit())
    ))
    icon.run()
