from plyer import notification

def notify_new_email(subject, sender):
    notification.notify(
        title=f"Neue E-Mail von {sender}",
        message=subject,
        timeout=5
    )
