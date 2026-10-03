"""
publisher.py
────────────
Publishes a post to Instagram using the Meta Content Publishing API.

Flow:
  Step 1 → POST /me/media          (create media container, get creation_id)
  Step 2 → POST /me/media_publish  (publish the container)

Requires:
  - A Professional Instagram account (Business or Creator)
  - INSTAGRAM_BUSINESS_ACCOUNT_ID
  - INSTAGRAM_ACCESS_TOKEN  (long-lived, ~60 days)
"""

import os
import time
import logging

import requests
from dotenv import load_dotenv

load_dotenv()

log = logging.getLogger(__name__)

IG_ACCOUNT_ID  = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID", "")
ACCESS_TOKEN   = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
GRAPH_API_BASE = "https://graph.instagram.com/v20.0"

# Max seconds to wait for the media container to be ready
CONTAINER_POLL_TIMEOUT = 120
CONTAINER_POLL_INTERVAL = 5


# ── Step 1: Create media container ────────────────────────────────────────────

def _create_media_container(image_url: str, caption: str) -> str:
    """
    Creates a media container on Instagram.

    Returns:
        creation_id (str) — used in step 2 to publish.
    """
    if not IG_ACCOUNT_ID or not ACCESS_TOKEN:
        raise ValueError(
            "INSTAGRAM_BUSINESS_ACCOUNT_ID or INSTAGRAM_ACCESS_TOKEN not set. "
            "Check your .env file."
        )

    url    = f"{GRAPH_API_BASE}/{IG_ACCOUNT_ID}/media"
    params = {
        "image_url":    image_url,
        "caption":      caption,
        "access_token": ACCESS_TOKEN,
    }

    log.info("Step 1: Creating Instagram media container …")
    resp = requests.post(url, params=params, timeout=30)

    if resp.status_code != 200:
        raise RuntimeError(
            f"Failed to create media container [{resp.status_code}]:\n{resp.text}"
        )

    creation_id = resp.json().get("id")
    if not creation_id:
        raise RuntimeError(f"No creation_id in response: {resp.json()}")

    log.info(f"Media container created → creation_id: {creation_id}")
    return creation_id


# ── Wait for container to be ready ────────────────────────────────────────────

def _wait_for_container(creation_id: str) -> None:
    """
    Polls the container status until it's FINISHED (ready to publish).
    Raises RuntimeError on timeout or error status.
    """
    url    = f"{GRAPH_API_BASE}/{creation_id}"
    params = {"fields": "status_code", "access_token": ACCESS_TOKEN}

    elapsed = 0
    while elapsed < CONTAINER_POLL_TIMEOUT:
        resp = requests.get(url, params=params, timeout=15)
        if resp.status_code == 200:
            status = resp.json().get("status_code", "")
            log.info(f"Container status: {status}")
            if status == "FINISHED":
                return
            if status == "ERROR":
                raise RuntimeError("Instagram media container entered ERROR state.")
        time.sleep(CONTAINER_POLL_INTERVAL)
        elapsed += CONTAINER_POLL_INTERVAL

    raise RuntimeError(
        f"Container {creation_id} not ready after {CONTAINER_POLL_TIMEOUT}s."
    )


# ── Step 2: Publish the container ─────────────────────────────────────────────

def _publish_container(creation_id: str) -> str:
    """
    Publishes the media container to Instagram.

    Returns:
        post_id (str) — the live Instagram post ID.
    """
    url    = f"{GRAPH_API_BASE}/{IG_ACCOUNT_ID}/media_publish"
    params = {
        "creation_id":  creation_id,
        "access_token": ACCESS_TOKEN,
    }

    log.info("Step 2: Publishing media container …")
    resp = requests.post(url, params=params, timeout=30)

    if resp.status_code != 200:
        raise RuntimeError(
            f"Failed to publish container [{resp.status_code}]:\n{resp.text}"
        )

    post_id = resp.json().get("id")
    log.info(f"✅ Post published successfully → Post ID: {post_id}")
    return post_id


# ── Public API ────────────────────────────────────────────────────────────────

def publish_to_instagram(image_url: str, caption: str) -> str:
    """
    Full two-step publish flow.

    Args:
        image_url: Publicly accessible HTTPS URL to the image.
        caption:   Instagram caption text (max 2200 chars).

    Returns:
        Instagram post ID.
    """
    # Truncate caption if it exceeds Instagram's limit
    if len(caption) > 2200:
        caption = caption[:2197] + "…"
        log.warning("Caption truncated to 2200 characters.")

    creation_id = _create_media_container(image_url, caption)
    _wait_for_container(creation_id)
    post_id     = _publish_container(creation_id)
    return post_id


# ── Quick test ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    if len(sys.argv) < 3:
        print("Usage: python publisher.py <public_image_url> <caption>")
        sys.exit(1)

    test_url     = sys.argv[1]
    test_caption = sys.argv[2]

    pid = publish_to_instagram(test_url, test_caption)
    print(f"\n✅ Published! Post ID: {pid}")
