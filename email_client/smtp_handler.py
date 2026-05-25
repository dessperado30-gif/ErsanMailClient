import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

SMTP_SERVERS = {
    "web.de": ("smtp.web.de", 587),
    "gmail.com": ("smtp.gmail.com", 587),
    "unitybox.de": ("smtp.unitybox.de", 587),
    "vodafonemail.de": ("smtp.vodafonemail.de", 587)
}

def detect_smtp(email):
    domain = email.split("@")[-1].lower()
    return SMTP_SERVERS.get(domain, None)

def send_email(account, to_addr, subject, body, html=False, attachments=None):
    smtp_info = detect_smtp(account.email)
    if smtp_info is None:
        return "SMTP-Server nicht gefunden."

    smtp_server, smtp_port = smtp_info

    try:
        msg = MIMEMultipart()
        msg["From"] = account.email
        msg["To"] = to_addr
        msg["Subject"] = subject

        if html:
            msg.attach(MIMEText(body, "html"))
        else:
            msg.attach(MIMEText(body, "plain"))

        if attachments:
            for file_path in attachments:
                with open(file_path, "rb") as f:
                    part = MIMEApplication(f.read(), Name=file_path.split("/")[-1])
                part["Content-Disposition"] = f'attachment; filename="{file_path.split("/")[-1]}"'
                msg.attach(part)

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(account.email, account.password)
        server.sendmail(account.email, to_addr, msg.as_string())
        server.quit()

        return True

    except Exception as e:
        return str(e)
