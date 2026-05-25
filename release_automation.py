import os
import json
import zipfile
import subprocess
from git import Repo

PROJECT_NAME = "ErsanMailClient"
BASE_VERSION = "1.0"
GITHUB_RAW = "https://raw.githubusercontent.com/dessperado30-gif/ErsanMailClient/main"
REPO_PATH = os.getcwd()

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
    os.makedirs("delta", exist_ok=True)

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

def git_commit_and_push(version):
    repo = Repo(REPO_PATH)
    repo.git.add(all=True)
    repo.index.commit(f"Release {version}")
    origin = repo.remote(name="origin")
    origin.push()
    print(f"✅ Release {version} erfolgreich auf GitHub gepusht.")

def main():
    print("🚀 Starte Release‑Automation...")
    old_version = input("Aktuelle Version eingeben (z.B. 1.0.103): ").strip()
    build = get_build_number()
    new_version = create_version(build)
    installer_name = create_installer_name(new_version)

    print(f"➡️ Neue Version: {new_version}")
    delta_name = create_delta(old_version, new_version)
    write_version_json(new_version, installer_name, delta_name, old_version)

    subprocess.run(["python", "auto_build.py"], check=False)
    git_commit_and_push(new_version)
    print("🎉 Release‑Automation abgeschlossen!")

if __name__ == "__main__":
    main()
