import json
import os
import shutil
import zipfile

BASE_VERSION = "1.0"
PROJECT_NAME = "ErsanMailClient"
GITHUB_RAW = "https://raw.githubusercontent.com/dessperado30-gif/ErsanMailClient/main"

def get_build_number():
    with open("build_number.txt", "r") as f:
        num = int(f.read().strip())
    num += 1
    with open("build_number.txt", "w") as f:
        f.write(str(num))
    return num

def create_version(build):
    return f"{BASE_VERSION}.{build}"

def create_installer_name(version):
    return f"{PROJECT_NAME}_Setup_{version}.exe"

def create_delta(old_version, new_version):
    delta_name = f"{old_version}_to_{new_version}.zip"
    delta_path = os.path.join("delta", delta_name)

    with zipfile.ZipFile(delta_path, "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk("dist"):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, "dist")
                z.write(full_path, rel_path)

    return delta_name

def write_version_json(version, installer_name, delta_name, old_version):
    data = {
        "version": version,
        "download_url": f"{GITHUB_RAW}/{installer_name}",
        "delta_url": f"{GITHUB_RAW}/delta/{delta_name}",
        "base_version": old_version
    }

    with open("version.json", "w") as f:
        json.dump(data, f, indent=4)

def main():
    print("🔧 Starte automatischen Build...")

    old_version = input("Gib deine aktuelle Version ein (z.B. 1.0.100): ").strip()

    build = get_build_number()
    new_version = create_version(build)
    installer_name = create_installer_name(new_version)

    print(f"➡️ Neue Version: {new_version}")
    print(f"➡️ Neuer Installer: {installer_name}")

    print("📦 Erstelle Delta‑Update...")
    delta_name = create_delta(old_version, new_version)

    print("📝 Aktualisiere version.json...")
    write_version_json(new_version, installer_name, delta_name, old_version)

    print("📁 Benenne Installer um...")
    shutil.copy("dist/ErsanMailClient.exe", installer_name)

    print("\n🎉 Alles fertig!")
    print("➡️ Lade hoch:")
    print(f"   - {installer_name}")
    print(f"   - version.json")
    print(f"   - delta/{delta_name}")

if __name__ == "__main__":
    main()
