import tkinter as tk
from tkinter import ttk, messagebox
from imapclient import IMAPClient
import pyzmail
import smtplib
from email.mime.text import MIMEText


# -----------------------------
# AUTOMATISCHE SERVER-ERKENNUNG
# -----------------------------

def detect_server(email):
    domain = email.split("@")[-1].lower()

    servers = {
        "web.de": "imap.web.de",
        "gmail.com": "imap.gmail.com",
        "unitybox.de": "imap.unitybox.de",
        "vodafonemail.de": "imap.vodafonemail.de"
    }

    return servers.get(domain, None)


def detect_smtp(email):
    domain = email.split("@")[-1].lower()

    servers = {
        "web.de": ("smtp.web.de", 587),
        "gmail.com": ("smtp.gmail.com", 587),
        "unitybox.de": ("smtp.unitybox.de", 587),
        "vodafonemail.de": ("smtp.vodafonemail.de", 587)
    }

    return servers.get(domain, None)


# -----------------------------
# E-MAIL KONTO
# -----------------------------

class EmailAccount:
    def __init__(self, email, server, password):
        self.email = email
        self.server = server
        self.password = password
        self.connection = None

    def connect(self):
        try:
            self.connection = IMAPClient(self.server, ssl=True)
            self.connection.login(self.email, self.password)
            self.connection.select_folder("INBOX")
            return True
        except Exception as e:
            return str(e)

    def fetch_emails(self, limit=20):
        try:
            messages = self.connection.search(["ALL"])
            messages = messages[-limit:]
            response = self.connection.fetch(messages, ["ENVELOPE"])
            email_list = []

            for msgid, data in response.items():
                env = data[b"ENVELOPE"]
                subject = env.subject.decode() if env.subject else "(Kein Betreff)"
                sender = env.from_[0].mailbox.decode() + "@" + env.from_[0].host.decode()
                date = env.date
                email_list.append((msgid, subject, sender, date))

            return email_list
        except Exception:
            return []

    def read_email(self, msgid):
        try:
            raw = self.connection.fetch([msgid], ["RFC822"])
            msg = pyzmail.PyzMessage.factory(raw[msgid][b"RFC822"])
            if msg.text_part:
                return msg.text_part.get_payload().decode(msg.text_part.charset)
            elif msg.html_part:
                return msg.html_part.get_payload().decode(msg.html_part.charset)
            else:
                return "(Keine lesbare Nachricht)"
        except:
            return "(Fehler beim Lesen)"


# -----------------------------
# HAUPT-APP
# -----------------------------

class EmailApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Multi‑E‑Mail‑Client (8 Konten)")
        self.window.geometry("900x600")

        self.accounts = []
        self.selected_account = None

        self.setup_ui()

    def setup_ui(self):
        frame = tk.Frame(self.window)
        frame.pack(pady=10)

        tk.Label(frame, text="E‑Mail:").grid(row=0, column=0)
        tk.Label(frame, text="Passwort:").grid(row=1, column=0)

        self.email_entry = tk.Entry(frame, width=40)
        self.pass_entry = tk.Entry(frame, width=40, show="*")

        self.email_entry.grid(row=0, column=1)
        self.pass_entry.grid(row=1, column=1)

        tk.Button(frame, text="Konto hinzufügen", command=self.add_account).grid(row=2, column=1, pady=5)

        self.account_list = tk.Listbox(self.window, height=5)
        self.account_list.pack(fill="x", padx=10)
        self.account_list.bind("<<ListboxSelect>>", self.load_account)

        self.email_tree = ttk.Treeview(self.window, columns=("Betreff", "Von", "Datum"), show="headings")
        self.email_tree.heading("Betreff", text="Betreff")
        self.email_tree.heading("Von", text="Von")
        self.email_tree.heading("Datum", text="Datum")
        self.email_tree.pack(fill="both", expand=True)
        self.email_tree.bind("<Double-1>", self.open_email)

        self.text_area = tk.Text(self.window)
        self.text_area.pack(fill="both", expand=True)

        # SENDEN BUTTON
        tk.Button(self.window, text="E-Mail senden", command=self.open_send_window).pack(pady=5)

    # -----------------------------
    # KONTO HINZUFÜGEN
    # -----------------------------

    def add_account(self):
        email = self.email_entry.get()
        server = detect_server(email)

        if server is None:
            messagebox.showerror("Fehler", "Unbekannte Domain | Server nicht gefunden.")
            return

        password = self.pass_entry.get()
        acc = EmailAccount(email, server, password)
        result = acc.connect()

        if result is True:
            self.accounts.append(acc)
            self.account_list.insert(tk.END, email)
            messagebox.showinfo("OK", f"Konto {email} hinzugefügt.")
        else:
            messagebox.showerror("Fehler", f"Login fehlgeschlagen:\n{result}")

    # -----------------------------
    # POSTEINGANG LADEN
    # -----------------------------

    def load_account(self, event):
        selection = self.account_list.curselection()
        if not selection:
            return

        index = selection[0]
        self.selected_account = self.accounts[index]

        emails = self.selected_account.fetch_emails()

        for row in self.email_tree.get_children():
            self.email_tree.delete(row)

        for msgid, subject, sender, date in emails:
            self.email_tree.insert("", tk.END, iid=msgid, values=(subject, sender, date))

    # -----------------------------
    # E-MAIL ÖFFNEN
    # -----------------------------

    def open_email(self, event):
        item = self.email_tree.focus()
        if not item:
            return

        msgid = int(item)
        content = self.selected_account.read_email(msgid)

        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, content)

    # -----------------------------
    # SENDEN-FENSTER
    # -----------------------------

    def open_send_window(self):
        if not self.selected_account:
            messagebox.showerror("Fehler", "Bitte zuerst ein Konto auswählen.")
            return

        send_win = tk.Toplevel(self.window)
        send_win.title("E-Mail senden")
        send_win.geometry("500x400")

        tk.Label(send_win, text="An:").pack()
        to_entry = tk.Entry(send_win, width=50)
        to_entry.pack()

        tk.Label(send_win, text="Betreff:").pack()
        subject_entry = tk.Entry(send_win, width=50)
        subject_entry.pack()
    
    toolbar = ctk.CTkFrame(win)
    toolbar.pack(pady=5)

    def make_bold():
        body_text.insert("insert", "<b></b>")
    def make_italic():
        body_text.insert("insert", "<i></i>")
    def make_red():
        body_text.insert("insert", '<span style="color:red"></span>')

    ctk.CTkButton(toolbar, text="B", width=40, command=make_bold).pack(side="left", padx=2)
    ctk.CTkButton(toolbar, text="I", width=40, command=make_italic).pack(side="left", padx=2)
    ctk.CTkButton(toolbar, text="Rot", width=40, command=make_red).pack(side="left", padx=2)

    tk.Label(send_win, text="Nachricht:").pack()
    body_text = tk.Text(send_win, height=10)
    body_text.pack()

    tk.Button(
            send_win,
            text="Senden",
            command=lambda: self.send_email(
                to_entry.get(),
                subject_entry.get(),
                body_text.get("1.0", tk.END)
            )
        ).pack(pady=10)

    # -----------------------------
    # E-MAIL SENDEN
    # -----------------------------

    def send_email(self, to_addr, subject, body):
        acc = self.selected_account
        smtp_info = detect_smtp(acc.email)

        if smtp_info is None:
            messagebox.showerror("Fehler", "SMTP-Server nicht gefunden.")
            return

        smtp_server, smtp_port = smtp_info

        try:
            msg = MIMEText(body)
            msg["From"] = acc.email
            msg["To"] = to_addr
            msg["Subject"] = subject

            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(acc.email, acc.password)
            server.sendmail(acc.email, to_addr, msg.as_string())
            server.quit()

            messagebox.showinfo("OK", "E-Mail erfolgreich gesendet!")

        except Exception as e:
            messagebox.showerror("Fehler", f"E-Mail konnte nicht gesendet werden:\n{e}")

    # -----------------------------
    # START
    # -----------------------------

    def run(self):
        self.window.mainloop()


app = EmailApp()
app.run()
