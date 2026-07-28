import argparse
import os
import pickle
import time
from pathlib import Path

import requests


def read_token() -> str | None:
    """Read YANDEX_DISK_TOKEN from ~/.hermes/.env safely."""
    env_path = os.path.expanduser("~/.hermes/.env")
    if not os.path.exists(env_path):
        return None
    with open(env_path) as f:
        for line in f:
            if line.startswith("YANDEX_DISK_TOKEN="):
                return line.strip().split("=", 1)[1]
    return None


def list_dir(public_key: str, path: str = "/", retries: int = 5) -> dict:
    params = {"public_key": public_key, "path": path, "limit": 1000, "offset": 0}
    for i in range(retries):
        try:
            r = requests.get(
                "https://cloud-api.yandex.net/v1/disk/public/resources",
                params=params,
                timeout=60,
            )
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if i == retries - 1:
                raise
            print(f"  list_dir retry {path}: {e}")
            time.sleep(2 ** i)
    raise RuntimeError("unreachable")


def build_catalog(public_key: str) -> list[dict]:
    all_items: list[dict] = []

    def walk(path: str = "/") -> None:
        j = list_dir(public_key, path)
        items = j.get("_embedded", {}).get("items", [])
        for it in items:
            all_items.append(it)
            if it["type"] == "dir":
                walk(it["path"])

    walk("/")
    return all_items


def download_item(
    public_key: str,
    disk_path: str,
    local_path: Path,
    download_api: str = "https://cloud-api.yandex.net/v1/disk/public/resources/download",
    attempts: int = 4,
) -> tuple[str, str, str | None]:
    rel = disk_path.lstrip("/")
    local_path.parent.mkdir(parents=True, exist_ok=True)
    if local_path.exists():
        return rel, "ok", None

    for attempt in range(attempts):
        try:
            r = requests.get(
                download_api,
                params={"public_key": public_key, "path": disk_path},
                timeout=60,
            )
            r.raise_for_status()
            href = r.json().get("href")
            if not href:
                raise RuntimeError(f"no download href for {disk_path}")

            with requests.get(href, stream=True, timeout=240) as fresp:
                fresp.raise_for_status()
                with open(local_path, "wb") as f:
                    for chunk in fresp.iter_content(chunk_size=65536):
                        if chunk:
                            f.write(chunk)
            return rel, "ok", None
        except Exception as e:
            if attempt == attempts - 1:
                return rel, "err", str(e)[:300]
            time.sleep(2)
    return rel, "err", "exhausted"


def save_state(state_path: Path, remaining: list[dict]) -> None:
    with open(state_path, "wb") as f:
        pickle.dump({"missing": remaining}, f)


def load_state(state_path: Path) -> list[dict] | None:
    if not state_path.exists():
        return None
    with open(state_path, "rb") as f:
        data = pickle.load(f)
    return data.get("missing")


def download_public_folder(
    public_key_or_url: str,
    destination: Path,
    state_path: Path | None = None,
    workers: int = 4,
    batch_size: int = 700,
    resume: bool = True,
) -> None:
    """
    Recursively download a public Yandex.Disk folder to a local directory.

    Args:
        public_key_or_url: Yandex public key (URL like https://disk.yandex.ru/d/XXXX).
        destination: Local directory where files will be saved.
        state_path: Optional pickle file to resume interrupted downloads.
        workers: Concurrent download threads.
        batch_size: Number of files to attempt per invocation before stopping.
        resume: Reuse existing state if state_path exists.
    """
    destination.mkdir(parents=True, exist_ok=True)

    if state_path and resume:
        missing = load_state(state_path)
        if missing is not None:
            print(f"resuming from state: {len(missing)} items remaining")
        else:
            print("building catalog from Yandex Disk...")
            all_items = build_catalog(public_key_or_url)
            missing = [it for it in all_items if it["type"] == "file"]
    else:
        print("building catalog from Yandex Disk...")
        all_items = build_catalog(public_key_or_url)
        missing = [it for it in all_items if it["type"] == "file"]

    print(f"total files to download: {len(missing)}")

    batch = missing[:batch_size]
    errors: list[tuple[str, str]] = []

    import concurrent.futures

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        futures = [
            ex.submit(
                download_item,
                public_key_or_url,
                it["path"],
                destination / it["path"].lstrip("/"),
            )
            for it in batch
        ]
        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            rel, status, err = future.result()
            if status != "ok":
                errors.append((rel, err or "unknown"))
            if i % 100 == 0:
                print(f"  {i}/{len(batch)} done, errors so far: {len(errors)}")

    print(f"batch finished. errors: {len(errors)}")
    for rel, err in errors[:10]:
        print(f"  ERROR {rel}: {err}")

    # Save remaining missing items for the next run.
    still_missing = [
        it for it in missing if not (destination / it["path"].lstrip("/")).exists()
    ]
    if state_path:
        save_state(state_path, still_missing)
        print(f"state saved: {len(still_missing)} items remaining")
    else:
        print(f"remaining without state file: {len(still_missing)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Recursively download a public Yandex.Disk folder."
    )
    parser.add_argument("public_key", help="Public key or public URL of the folder")
    parser.add_argument("destination", help="Local destination directory")
    parser.add_argument(
        "--state",
        default=".yandex-download-state.pkl",
        help="Pickle state file for resume (default: .yandex-download-state.pkl)",
    )
    parser.add_argument(
        "--workers", type=int, default=4, help="Concurrent download threads"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=700,
        help="Max files to download in one invocation",
    )
    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="Ignore existing state file and rebuild catalog",
    )
    args = parser.parse_args()

    download_public_folder(
        public_key_or_url=args.public_key,
        destination=Path(args.destination),
        state_path=Path(args.state),
        workers=args.workers,
        batch_size=args.batch_size,
        resume=not args.no_resume,
    )
