from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
import json
import os

KEY_FILE = "settings.json"
KEY = None


def load_key():
    global KEY
    if not os.path.exists(KEY_FILE):
        key = get_random_bytes(32)
        with open(KEY_FILE, "w") as f:
            json.dump({"key": base64.b64encode(key).decode()}, f)
        KEY = key
        return key

    with open(KEY_FILE, "r") as f:
        data = json.load(f)
        KEY = base64.b64decode(data["key"])
        return KEY


load_key()


def encrypt(text):
    cipher = AES.new(KEY, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(text.encode())
    return base64.b64encode(cipher.nonce + tag + ciphertext).decode()


def decrypt(enc):
    raw = base64.b64decode(enc)
    nonce = raw[:16]
    tag = raw[16:32]
    ciphertext = raw[32:]
    cipher = AES.new(KEY, AES.MODE_EAX, nonce)
    return cipher.decrypt_and_verify(ciphertext, tag).decode()
