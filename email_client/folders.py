FOLDERS = ["INBOX", "Sent", "Drafts", "Spam", "Trash"]

def list_folders(connection):
    return connection.list_folders()
