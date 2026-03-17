"""
video_fetcher.py
Downloads a background video from Pixabay API based on the quote theme.
Categories: ocean/beach, sunrise/nature, rain/forest, city/timelapse.
"""

import os
import random
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "")
PIXABAY_API_URL = "https://pixabay.com/api/videos/"

# Search queries per theme — multiple options for variety
THEME_QUERIES = {
    "ofw":     ["ocean waves", "beach sunset", "sea horizon", "waves shore"],
    "health":  ["forest rain", "green nature", "sunrise trees", "morning light"],
    "money":   ["city timelapse", "city lights night", "urban sunset", "golden city"],
    "mindset": ["sunrise golden", "mountain sunrise", "golden nature", "dawn sky"],
}

# Video duration filter — prefer 15-30s clips
MIN_DURATION = 10
MAX_DURATION = 60


def _fetch_pixabay_video(query: str, per_page: int = 20) -> str | None:
    """Fetch video URL from Pixabay API for a given search query."""
    if not PIXABAY_API_KEY:
        print("  ⚠️  PIXABAY_API_KEY not set.")
        return None
    try:
        resp = requests.get(
            PIXABAY_API_URL,
            params={
                "key":       PIXABAY_API_KEY,
                "q":         query,
                "per_page":  per_page,
                "video_type": "film",
                "safesearch": "true",
            },
            timeout=15,
        )
        data = resp.json()
        hits = data.get("hits", [])
        if not hits:
            print(f"  ⚠️  No Pixabay results for: {query}")
            return None

        # Filter by duration and prefer medium quality (720p — good balance)
        suitable = [
            h for h in hits
            if MIN_DURATION <= h.get("duration", 0) <= MAX_DURATION
            and h.get("videos", {}).get("medium", {}).get("url")
        ]
        if not suitable:
            suitable = hits  # fallback to all if none match duration

        # Pick randomly from top results for variety
        seed   = datetime.now().strftime("%Y-%m-%d") + query
        random.seed(int(sum(ord(c) for c in seed)))
        chosen = random.choice(suitable[:10])

        # Prefer large (1080p) → medium (720p) → small
        videos = chosen.get("videos", {})
        url = (
            videos.get("large",  {}).get("url") or
            videos.get("medium", {}).get("url") or
            videos.get("small",  {}).get("url")
        )
        duration = chosen.get("duration", 0)
        print(f"  ✅ Pixabay video found: {query} ({duration}s)")
        return url

    except Exception as e:
        print(f"  ❌ Pixabay API error: {e}")
        return None


def download_video(url: str, output_path: str) -> bool:
    """Download video from URL to local file."""
    try:
        print(f"  📥 Downloading video...")
        resp = requests.get(url, stream=True, timeout=60)
        if resp.status_code == 200:
            with open(output_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=1024 * 1024):
                    f.write(chunk)
            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            print(f"  ✅ Downloaded: {output_path} ({size_mb:.1f} MB)")
            return True
        else:
            print(f"  ❌ Download failed: HTTP {resp.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Download error: {e}")
        return False


def fetch_background_video(theme: str, output_path: str) -> bool:
    """
    Fetch and download a background video for the given theme.
    Tries multiple search queries until one succeeds.
    Returns True if successful.
    """
    queries = THEME_QUERIES.get(theme, THEME_QUERIES["mindset"])

    # Rotate which query we use based on date for variety
    seed_idx = (datetime.now().timetuple().tm_yday) % len(queries)
    ordered  = queries[seed_idx:] + queries[:seed_idx]

    for query in ordered:
        print(f"  🔍 Searching Pixabay: '{query}'...")
        url = _fetch_pixabay_video(query)
        if url:
            return download_video(url, output_path)

    print(f"  ❌ All Pixabay queries failed for theme: {theme}")
    return False


if __name__ == "__main__":
    import sys
    theme = sys.argv[1] if len(sys.argv) > 1 else "ofw"
    print(f"Testing video fetch for theme: {theme}")
    success = fetch_background_video(theme, f"test_bg_{theme}.mp4")
    print(f"Result: {'✅ Success' if success else '❌ Failed'}")
