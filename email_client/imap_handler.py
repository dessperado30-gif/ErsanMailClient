from imapclient import IMAPClient
import pyzmail

IMAP_SERVERS = {
    "web.de": "imap.web.de",
    "gmail.com": "imap.gmail.com",
    "unitybox.de": "imap.unitybox.de",
    "vodafonemail.de": "imap.vodafonemail.de"
}

def detect_imap(email):
    domain = email.split("@")[-1].lower()
    return IMAP_SERVERS.get(domain, None)

class EmailAccount:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.server = detect_imap(email)
        self.connection = None

    def connect(self):
        try:
            self.connection = IMAPClient(self.server, ssl=True)
            self.connection.login(self.email, self.password)
            self.connection.select_folder("INBOX")
            return True
        except Exception as e:
            return str(e)

    def fetch_emails(self, limit=50):
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
                email_list.append((msgid, subject, sender, date, self))

            return email_list
        except:
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
