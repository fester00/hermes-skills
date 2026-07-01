import subprocess, json, os

def read_yandex_disk_token() -> str:
    """Read YANDEX_DISK_TOKEN from ~/.hermes/.env safely."""
    env_path = os.path.expanduser("~/.hermes/.env")
    with open(env_path) as f:
        for line in f:
            if line.startswith("YANDEX_DISK_TOKEN="):
                return line.strip().split("=", 1)[1]
    raise RuntimeError("YANDEX_DISK_TOKEN not found in ~/.hermes/.env")

def upload_file_to_yandex_disk(local_path: str, remote_name: str, publish: bool = True) -> str:
    """
    Upload a local file to Yandex Disk and return the public URL.

    Args:
        local_path: Absolute path to the local file
        remote_name: Name for the file on Yandex Disk (e.g., "pentajunior-v2.db")
        publish: Whether to publish the file (make publicly accessible)

    Returns:
        Public URL if publish=True, or "uploaded" if publish=False
    """
    token = read_yandex_disk_token()

    # 1. Get upload URL
    r1 = subprocess.run(
        ["curl", "-s",
         "-H", f"Authorization: OAuth {token}",
         f"https://cloud-api.yandex.net/v1/disk/resources/upload?path=app:/{remote_name}&overwrite=true"],
        capture_output=True, text=True, check=True
    )
    upload_url = json.loads(r1.stdout)["href"]

    # 2. Upload file
    subprocess.run(
        ["curl", "-s", "-T", local_path, upload_url],
        capture_output=True, check=True
    )

    if not publish:
        return "uploaded"

    # 3. Publish
    subprocess.run(
        ["curl", "-s",
         "-H", f"Authorization: OAuth {token}",
         "-X", "PUT",
         f"https://cloud-api.yandex.net/v1/disk/resources/publish?path=app:/{remote_name}"],
        capture_output=True, check=True
    )

    # 4. Get public URL
    r4 = subprocess.run(
        ["curl", "-s",
         "-H", f"Authorization: OAuth {token}",
         f"https://cloud-api.yandex.net/v1/disk/resources?path=app:/{remote_name}"],
        capture_output=True, text=True, check=True
    )
    return json.loads(r4.stdout).get("public_url", "NOT_FOUND")

if __name__ == "__main__":
    # Example usage
    local_path = os.path.expanduser("~/pentajunior-v2/pentajunior.db")
    remote_name = "pentajunior-v2.db"
    pub_url = upload_file_to_yandex_disk(local_path, remote_name)
    print(f"Public URL: {pub_url}")
