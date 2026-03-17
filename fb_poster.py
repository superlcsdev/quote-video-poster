"""
fb_poster.py
Posts a video (Reel) to Facebook Page via Graph API.
Uses the resumable upload endpoint for reliable video uploads.
"""

import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

FB_PAGE_ID      = os.getenv("FB_PAGE_ID", "")
FB_ACCESS_TOKEN = os.getenv("FB_ACCESS_TOKEN", "")
GRAPH_API_URL   = "https://graph.facebook.com/v19.0"


def post_reel_to_facebook(video_path: str, caption: str) -> bool:
    """
    Upload and publish a video as a Facebook Reel.
    Returns True on success, False on failure.
    """
    if not FB_PAGE_ID or not FB_ACCESS_TOKEN:
        print("  ❌ FB_PAGE_ID or FB_ACCESS_TOKEN not set.")
        return False

    try:
        file_size = os.path.getsize(video_path)
        print(f"  📤 Uploading video ({file_size / 1024 / 1024:.1f} MB)...")

        # ── Step 1: Initialise resumable upload session ───────────
        init_resp = requests.post(
            f"{GRAPH_API_URL}/{FB_PAGE_ID}/video_reels",
            data={
                "access_token": FB_ACCESS_TOKEN,
                "upload_phase":  "start",
                "file_size":     file_size,
            },
            timeout=30,
        )
        init_data = init_resp.json()

        if "video_id" not in init_data or "upload_url" not in init_data:
            print(f"  ❌ Upload init failed: {init_data}")
            return False

        video_id  = init_data["video_id"]
        upload_url = init_data["upload_url"]
        print(f"  ✅ Upload session started. Video ID: {video_id}")

        # ── Step 2: Upload video bytes ────────────────────────────
        with open(video_path, "rb") as f:
            upload_resp = requests.post(
                upload_url,
                headers={
                    "Authorization":  f"OAuth {FB_ACCESS_TOKEN}",
                    "offset":         "0",
                    "file_size":      str(file_size),
                },
                data=f,
                timeout=180,
            )

        if upload_resp.status_code not in [200, 201]:
            print(f"  ❌ Video upload failed: {upload_resp.text[:300]}")
            return False
        print(f"  ✅ Video bytes uploaded successfully.")

        # ── Step 3: Publish the Reel ──────────────────────────────
        print("  📢 Publishing Reel...")
        pub_resp = requests.post(
            f"{GRAPH_API_URL}/{FB_PAGE_ID}/video_reels",
            data={
                "access_token":    FB_ACCESS_TOKEN,
                "video_id":        video_id,
                "upload_phase":    "finish",
                "video_state":     "PUBLISHED",
                "description":     caption,
                "title":           caption[:100],
            },
            timeout=60,
        )
        pub_data = pub_resp.json()

        if pub_data.get("success"):
            print(f"  🎉 Reel published! Video ID: {video_id}")
            return True
        else:
            print(f"  ❌ Publish failed: {pub_data}")
            return False

    except Exception as e:
        print(f"  ❌ Exception during video post: {e}")
        return False


if __name__ == "__main__":
    print("FB_PAGE_ID set     :", bool(FB_PAGE_ID))
    print("FB_ACCESS_TOKEN set:", bool(FB_ACCESS_TOKEN))
