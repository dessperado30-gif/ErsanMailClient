import json
import os

BASE_VERSION = "1.0"

def get_build_number():
    with open("build_number.txt", "r") as f:
        num = int(f.read().strip())
    num += 1
    with open("build_number.txt", "w") as f:
        f.write(str(num))
    return num

def create_version_json(build_number):
    version = f"{BASE_VERSION}.{build_number}"
    filename = f"ErsanMailClient_Setup_{version}.exe"

    data = {
        "version": version,
        "download_url": f"https://raw.githubusercontent.com/dessperado30-gif/ErsanMailClient/main/{filename}"
    }

    with open("version.json", "w") as f:
        json.dump(data, f, indent=4)

    print("Neue version.json erzeugt:", data)
    return filename

if __name__ == "__main__":
    build = get_build_number()
    installer_name = create_version_json(build)
    print("Neuer Installer-Name:", installer_name)
