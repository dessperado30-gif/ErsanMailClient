import requests
import json
import os
import subprocess

# 🔹 Hier kommt deine GitHub-RAW-URL rein:
VERSION_URL = "https://raw.githubusercontent.com/dessperado30-gif/ErsanMailClient/main/version.json"

LOCAL_VERSION = "1.0.0"

def check_for_updates():
    try:
        response = requests.get(VERSION_URL)
        data = response.json()

        online_version = data["version"]
        download_url = data["download_url"]

        if online_version != LOCAL_VERSION:
            print(f"Neue Version verfügbar: {online_version}")
            download_update(download_url)
        else:
            print("Du hast die neueste Version.")
    except Exception as e:
        print("Update-Check fehlgeschlagen:", e)

def download_update(url):
    print("Lade Update herunter...")
    exe_path = "update_installer.exe"

    r = requests.get(url)
    with open(exe_path, "wb") as f:
        f.write(r.content)

    print("Starte Installer...")
    subprocess.Popen([exe_path])
    os._exit(0)
