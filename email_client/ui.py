import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkhtmlview import HTMLLabel
from threading import Thread
from plyer import notification
import pystray
from PIL import Image, ImageDraw

from imap_handler import EmailAccount
from smtp_handler import send_email
from encryption import encrypt, decrypt

import json
import os
import time


# ---------------------------------------------------
#   SETTINGS (ACCOUNTS)
# ---------------------------------------------------

SETTINGS_FILE = "accounts.json"

def load_accounts():
    if not os.path.exists(SETTINGS_FILE):
        return []

    with open(SETTINGS_FILE, "r") as f:
        data = json.load(f)

    accounts = []
    for acc in data:
        email = acc["email"]
        password = decrypt(acc["password"])
        accounts.append((email, password))

    return accounts


def save_accounts(accounts):
    data = []
    for acc in accounts:
        data.append({
            "email": acc.email,
            "password": encrypt(acc.password)
        })

    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ---------------------------------------------------
#   TRAY ICON
# ---------------------------------------------------

def create_tray_icon(on_quit):
    img = Image.new("RGB", (64, 64), "black")
    d = ImageDraw.Draw(img)
    d.ellipse((8, 8, 56, 56), fill="white")

    icon = pystray.Icon("MailClient", img, "Mail Client", menu=pystray.Menu(
        pystray.MenuItem("Beenden", lambda: on_quit())
    ))
    Thread(target=icon.run, daemon=True).start()


# ---------------------------------------------------
#   PUSH NOTIFICATION
# ---------------------------------------------------

def notify(subject, sender):
    notification.notify(
        title=f"Neue E-Mail von {sender}",
        message=subject,
        timeout=5
    )


# ---------------------------------------------------
#   ULTRA MODERN UI
# ---------------------------------------------------

class EmailApp:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.window = TkinterDnD.Tk()
        self.window.title("Ultra‑Modern Mail Client")
        self.window.geometry("1300x800")

        self.accounts = []
        self.selected_account = None
        self.attachments = []

        self.build_ui()
        self.load_saved_accounts()
        self.start_auto_sync()
        create_tray_icon(self.quit_app)

    # ---------------------------------------------------
    #   UI AUFBAU
    # ---------------------------------------------------

    def build_ui(self):
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self.window, width=250)
        self.sidebar.grid(row=0, column=0, sticky="ns")

        ctk.CTkLabel(self.sidebar, text="Konten", font=("Arial", 18)).pack(pady=10)

        self.account_list = ctk.CTkTextbox(self.sidebar, height=150)
        self.account_list.pack(fill="x", padx=10)
        self.account_list.bind("<Button-1>", self.select_account)
        ctk.CTkLabel(self.sidebar, text="Suche:").pack(pady=(20, 5))
        self.search_entry = ctk.CTkEntry(self.sidebar, placeholder_text="Suchbegriff...")
        self.search_entry.pack(pady=5)
        ctk.CTkButton(self.sidebar, text="Suchen", command=self.search_emails).pack(pady=5)

        ctk.CTkButton(self.sidebar, text="Konto hinzufügen", command=self.open_add_account).pack(pady=10)

        ctk.CTkButton(self.sidebar, text="E-Mail senden", command=self.open_send_window).pack(pady=10)
        ctk.CTkButton(self.sidebar, text="Aktualisieren", command=self.refresh_all).pack(pady=10)
        ctk.CTkButton(self.sidebar, text="Schlüssel erneuern", command=self.rotate_key_action).pack(pady=10)
        ctk.CTkLabel(self.sidebar, text="Theme:").pack(pady=(20, 5))
        theme_box = ctk.CTkComboBox(self.sidebar, values=["dark", "light", "system"],
                                    command=lambda mode: ctk.set_appearance_mode(mode))
        ctk.CTkLabel(self.sidebar, text="Suche:").pack(pady=(20, 5))
        self.search_entry = ctk.CTkEntry(self.sidebar, placeholder_text="Suchbegriff...")
        self.search_entry.pack(pady=5)
        ctk.CTkButton(self.sidebar, text="Suchen", command=self.search_emails).pack(pady=5)

        theme_box.set("dark")
        theme_box.pack(pady=5)

        # Hauptbereich
        self.main_frame = ctk.CTkFrame(self.window)
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        # E-Mail Liste
        self.email_list = ctk.CTkTextbox(self.main_frame, height=200)
        self.email_list.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.email_list.bind("<Button-1>", self.open_email)

        # HTML Viewer
        self.html_frame = ctk.CTkFrame(self.main_frame)
        self.html_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

    # ---------------------------------------------------
    #   KONTEN
    # ---------------------------------------------------

    def open_add_account(self):
        win = ctk.CTkToplevel(self.window)
        win.title("Konto hinzufügen")
        win.geometry("400x250")

        email_entry = ctk.CTkEntry(win, placeholder_text="E-Mail")
        email_entry.pack(pady=10)

        pass_entry = ctk.CTkEntry(win, placeholder_text="Passwort", show="*")
        pass_entry.pack(pady=10)

        def add():
            email = email_entry.get()
            password = pass_entry.get()

            acc = EmailAccount(email, password)
            result = acc.connect()

            if result is True:
                self.accounts.append(acc)
                save_accounts(self.accounts)
                self.update_account_list()
                win.destroy()
            else:
                messagebox.showerror("Fehler", result)

        ctk.CTkButton(win, text="Hinzufügen", command=add).pack(pady=10)

    def update_account_list(self):
        self.account_list.delete("1.0", "end")
        for acc in self.accounts:
            self.account_list.insert("end", acc.email + "\n")

    def select_account(self, event):
        index = int(float(self.account_list.index("@%s,%s" % (event.x, event.y))).__floor__())
        if index < len(self.accounts):
            self.selected_account = self.accounts[index]

    def load_saved_accounts(self):
        saved = load_accounts()
        for email, password in saved:
            acc = EmailAccount(email, password)
            if acc.connect() is True:
                self.accounts.append(acc)
        self.update_account_list()
        self.refresh_all()

    # ---------------------------------------------------
    #   POSTEINGANG
    # ---------------------------------------------------

    def refresh_all(self):
        self.email_list.delete("1.0", "end")

    def load_folder(self, folder_name):
        self.email_list.delete("1.0", "end")
        for acc in self.accounts:
            acc.connection.select_folder(folder_name)
        emails = acc.fetch_emails()
        for msgid, subject, sender, date, account in emails:
            self.email_list.insert("end", f"{account.email}|{msgid}|{subject}|{sender}\n")

        for acc in self.accounts:
            emails = acc.fetch_emails()
            for msgid, subject, sender, date, account in emails:
                self.email_list.insert("end", f"{account.email}|{msgid}|{subject}|{sender}\n")
    def search_emails(self):
        term = self.search_entry.get().lower()
        self.email_list.delete("1.0", "end")

        for acc in self.accounts:
            emails = acc.fetch_emails()
        for msgid, subject, sender, date, account in emails:
            if term in subject.lower() or term in sender.lower():
                self.email_list.insert("end", f"{account.email}|{msgid}|{subject}|{sender}\n")


    def open_email(self, event):
        line = self.email_list.get("insert linestart", "insert lineend")
        if "|" not in line:
            return

        email_addr, msgid, subject, sender = line.split("|")
        msgid = int(msgid)

        acc = next(a for a in self.accounts if a.email == email_addr)
        content = acc.read_email(msgid)

        for widget in self.html_frame.winfo_children():
            widget.destroy()

        HTMLLabel(self.html_frame, html=content).pack(fill="both", expand=True)

    # ---------------------------------------------------
    #   SENDEN
    # ---------------------------------------------------

    def open_send_window(self):
        win = ctk.CTkToplevel(self.window)
        win.title("E-Mail senden")
        win.geometry("600x600")
    from security import rotate_key

    def rotate_key_action(self):
        try:
            rotate_key()
            self.accounts = []
            self.load_saved_accounts()
            messagebox.showinfo("OK", "AES‑Schlüssel erfolgreich erneuert.")
        except Exception as e:
            messagebox.showerror("Fehler", f"Rotation fehlgeschlagen:\n{e}")

        from_box = ctk.CTkComboBox(win, values=[a.email for a in self.accounts])
        from_box.pack(pady=10)

        to_entry = ctk.CTkEntry(win, placeholder_text="An")
        to_entry.pack(pady=10)

        subject_entry = ctk.CTkEntry(win, placeholder_text="Betreff")
        subject_entry.pack(pady=10)

        body_text = ctk.CTkTextbox(win, height=200)
        body_text.pack(pady=10)

        attach_label = ctk.CTkLabel(win, text="Anhänge: keine")
        attach_label.pack()

        def add_attach():
            files = filedialog.askopenfilenames()
            if files:
                self.attachments.extend(files)
                attach_label.configure(text=f"{len(self.attachments)} Datei(en)")

        ctk.CTkButton(win, text="Anhang hinzufügen", command=add_attach).pack(pady=10)

        def send():
            acc = next(a for a in self.accounts if a.email == from_box.get())
            result = send_email(acc, to_entry.get(), subject_entry.get(),
                                body_text.get("1.0", "end"), html=True,
                                attachments=self.attachments)

            if result is True:
                messagebox.showinfo("OK", "E-Mail gesendet")
                self.attachments = []
                win.destroy()
            else:
                messagebox.showerror("Fehler", result)

        ctk.CTkButton(win, text="Senden", command=send).pack(pady=10)

    # ---------------------------------------------------
    #   AUTO SYNC
    # ---------------------------------------------------

    def start_auto_sync(self):
        def loop():
            while True:
                old = self.email_list.get("1.0", "end")
                self.refresh_all()
                new = self.email_list.get("1.0", "end")

                if new != old:
                    # Neue E-Mail erkannt
                    try:
                        last_line = new.strip().split("\n")[-1]
                        _, _, subject, sender = last_line.split("|")
                        notify(subject, sender)
                    except:
                        pass

                time.sleep(10)

        Thread(target=loop, daemon=True).start()

    # ---------------------------------------------------
    #   QUIT
    # ---------------------------------------------------

    def quit_app(self):
        self.window.destroy()


# ---------------------------------------------------
#   START
# ---------------------------------------------------

def run_app():
    app = EmailApp()
    app.window.mainloop()
