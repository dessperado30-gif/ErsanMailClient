import json
import base64
import os
from Crypto.Random import get_random_bytes
from encryption import decrypt, encrypt, KEY_FILE

ACCOUNTS_FILE = "accounts.json"
BACKUP_FILE = "settings_backup.json"


def rotate_key():
    # 1. Backup des alten Keys
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "r") as f:
            old_key_data = json.load(f)

        with open(BACKUP_FILE, "w") as f:
            json.dump(old_key_data, f, indent=4)

    # 2. Accounts laden
    if os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, "r") as f:
            accounts = json.load(f)
    else:
        accounts = []

    # 3. Passwörter entschlüsseln
    decrypted_accounts = []
    for acc in accounts:
        decrypted_accounts.append({
            "email": acc["email"],
            "password": decrypt(acc["password"])
        })

    # 4. Neuen AES‑Key generieren
    new_key = get_random_bytes(32)
    with open(KEY_FILE, "w") as f:
        json.dump({"key": base64.b64encode(new_key).decode()}, f)

    # 5. Passwörter neu verschlüsseln
    from encryption import load_key
    load_key()  # neuen Key laden

    new_accounts = []
    for acc in decrypted_accounts:
        new_accounts.append({
            "email": acc["email"],
            "password": encrypt(acc["password"])
        })

    # 6. Accounts speichern
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump(new_accounts, f, indent=4)

    return True
