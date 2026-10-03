"""
uploader.py
───────────
Uploads the generated image to a public GitHub repository
and returns a raw.githubusercontent.com URL that Instagram
can access during the Content Publishing API call.
"""

import os
import base64
import logging
from pathlib import Path
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

load_dotenv()

log = logging.getLogger(__name__)

GITHUB_TOKEN      = os.getenv("GITHUB_TOKEN", "")
GITHUB_IMAGE_REPO = os.getenv("GITHUB_IMAGE_REPO", "")   # e.g. "username/current-affairs-images"
GITHUB_BRANCH     = os.getenv("GITHUB_IMAGE_BRANCH", "main")
GITHUB_API        = "https://api.github.com"


def _get_existing_sha(filename: str) -> str | None:
    """
    GitHub requires the blob SHA when updating an existing file.
    Returns None if the file doesn't exist yet.
    """
    url = f"{GITHUB_API}/repos/{GITHUB_IMAGE_REPO}/contents/{filename}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }
    resp = requests.get(url, headers=headers, params={"ref": GITHUB_BRANCH}, timeout=15)
    if resp.status_code == 200:
        return resp.json().get("sha")
    return None


def upload_image_to_github(image_path: Path) -> str:
    """
    Commit an image file to the public GitHub repo.

    Args:
        image_path: Local path to the .jpg image.

    Returns:
        Public raw.githubusercontent.com URL for the uploaded image.

    Raises:
        ValueError: if required env vars are missing.
        RuntimeError: if the GitHub API call fails.
    """
    if not GITHUB_TOKEN:
        raise ValueError("GITHUB_TOKEN is not set. Check your .env file.")
    if not GITHUB_IMAGE_REPO:
        raise ValueError("GITHUB_IMAGE_REPO is not set. Check your .env file.")

    # Ensure it's a string path
    image_path_str = str(image_path)
    filename = os.path.basename(image_path_str)   # e.g. current_affairs_2026_09_19.jpg

    # Read and base64-encode the image
    with open(image_path_str, "rb") as f:
        content_b64 = base64.b64encode(f.read()).decode("utf-8")

    # Check if file already exists (need SHA to update)
    existing_sha = _get_existing_sha(filename)

    date_str = datetime.now(timezone.utc).strftime("%d %B %Y")
    payload: dict = {
        "message": f"chore: add current affairs image {date_str}",
        "content": content_b64,
        "branch":  GITHUB_BRANCH,
    }
    if existing_sha:
        payload["sha"] = existing_sha   # required for updates

    url = f"{GITHUB_API}/repos/{GITHUB_IMAGE_REPO}/contents/{filename}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
    }

    log.info(f"Uploading {filename} to GitHub repo {GITHUB_IMAGE_REPO} …")
    resp = requests.put(url, json=payload, headers=headers, timeout=30)

    if resp.status_code not in (200, 201):
        raise RuntimeError(
            f"GitHub upload failed [{resp.status_code}]: {resp.text}"
        )

    # Build the public raw URL
    raw_url = (
        f"https://raw.githubusercontent.com/{GITHUB_IMAGE_REPO}"
        f"/{GITHUB_BRANCH}/{filename}"
    )
    log.info(f"Image publicly available at: {raw_url}")
    return raw_url


# ── Quick test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    # Pass a local image path as argument for testing
    if len(sys.argv) < 2:
        print("Usage: python uploader.py <path_to_image.jpg>")
        sys.exit(1)

    test_path = Path(sys.argv[1])
    if not test_path.exists():
        print(f"File not found: {test_path}")
        sys.exit(1)

    public_url = upload_image_to_github(test_path)
    print(f"\n✅ Public URL:\n{public_url}")
