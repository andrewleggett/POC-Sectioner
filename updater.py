import requests
import os
import sys

def get_latest_release_info(repo_owner, repo_name):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch latest release info: {response.status_code}")

def download_file(url, destination):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(destination, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
    else:
        raise Exception(f"Failed to download file: {response.status_code}")

def get_current_version(version_file):
    if os.path.exists(version_file):
        with open(version_file, 'r') as file:
            return file.read().strip()
    else:
        raise Exception(f"Version file not found: {version_file}")

def update_version_file(version_file, new_version):
    with open(version_file, 'w') as file:
        file.write(new_version)

def main():
    repo_owner = "andrewleggett"
    repo_name = "POC-Sectioner-Py"
    version_file = os.path.join(os.path.dirname(sys.argv[0]), "version.txt")

    try:
        current_version = get_current_version(version_file)
        release_info = get_latest_release_info(repo_owner, repo_name)
        latest_version = release_info.get("tag_name", "")

        if latest_version <= current_version:
            print(f"No update needed. Current version: {current_version}, Latest version: {latest_version}")
            return

        assets = release_info.get("assets", [])

        # Find the asset with the name 'POC-Sectioner.exe'
        poc_sectioner_asset = next((asset for asset in assets if asset["name"] == "POC Sectioner.exe"), None)

        if poc_sectioner_asset:
            download_url = poc_sectioner_asset["browser_download_url"]
            destination_path = os.path.join(os.path.dirname(sys.argv[0]), "POC Sectioner.exe")

            print(f"Downloading {download_url} to {destination_path}...")
            download_file(download_url, destination_path)
            print("Download complete.")

            # Update the version file with the new version
            update_version_file(version_file, latest_version)
            print(f"Updated to version {latest_version}.")
        else:
            print("POC Sectioner.exe not found in the latest release.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
