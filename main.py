"""
main.py
Quote Video Auto-Poster pipeline.
Runs daily at 7:00 AM SGT via GitHub Actions.

Flow:
  1. Generate quote (Gemini or fallback library)
  2. Download background video from Pixabay
  3. Compose Reels video (1080x1920 MP4, 20s)
  4. Generate caption
  5. Post to Facebook as Reel

Run modes:
  python main.py                  → full pipeline
  python main.py --dry-run        → everything except FB post
  python main.py --theme ofw      → force specific theme
  python main.py --overlay-only   → test text overlay only (no video needed)
"""

import argparse
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from quote_generator   import generate_quote, get_theme_for_today
from video_fetcher     import fetch_background_video
from video_composer    import compose_video
from caption_generator import generate_caption
from fb_poster         import post_reel_to_facebook

OUTPUT_DIR = "output_videos"
TEMP_DIR   = "temp"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR,   exist_ok=True)


def run_pipeline(dry_run: bool = False, theme: str = None, overlay_only: bool = False):
    print("\n" + "=" * 60)
    print("  🎬  Quote Video Auto-Poster")
    print("  📅  " + datetime.now().strftime("%Y-%m-%d %H:%M") + " UTC")
    print("=" * 60)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # ── Step 1: Generate quote ────────────────────────────────────
    print("\n[1/5] Generating morning quote...")
    q_data = generate_quote(theme)
    quote    = q_data["quote"]
    subtitle = q_data["subtitle"]
    author   = q_data["author"]
    theme    = q_data["theme"]
    print(f"  📝 Quote : {quote[:70]}...")
    print(f"  🏷️  Theme : {theme}")

    # ── Overlay-only test mode ────────────────────────────────────
    if overlay_only:
        from video_composer import _make_text_overlay
        from PIL import Image
        import numpy as np
        print("\n[OVERLAY TEST] Generating text overlay image...")
        arr  = _make_text_overlay(quote, subtitle, author)
        path = os.path.join(OUTPUT_DIR, f"overlay_test_{timestamp}.png")
        Image.fromarray(arr).save(path)
        print(f"  ✅ Overlay saved: {path}")
        return

    # ── Step 2: Download background video ─────────────────────────
    print(f"\n[2/5] Fetching background video for theme: {theme}...")
    bg_path = os.path.join(TEMP_DIR, f"bg_{timestamp}.mp4")
    success = fetch_background_video(theme, bg_path)

    if not success:
        print("  ❌ Could not fetch background video. Exiting.")
        sys.exit(1)

    # ── Step 3: Compose video ─────────────────────────────────────
    print(f"\n[3/5] Composing Reels video (1080×1920, 20s)...")
    output_path = os.path.join(OUTPUT_DIR, f"quote_reel_{timestamp}.mp4")
    result = compose_video(
        bg_video_path = bg_path,
        quote         = quote,
        subtitle      = subtitle,
        author        = author,
        output_path   = output_path,
    )
    if not result:
        print("  ❌ Video composition failed. Exiting.")
        sys.exit(1)

    # ── Step 4: Generate caption ──────────────────────────────────
    print(f"\n[4/5] Generating post caption...")
    caption = generate_caption(quote, theme)
    print(f"  📝 Caption: {caption[:80]}...")

    # ── Step 5: Post to Facebook ──────────────────────────────────
    if dry_run:
        print("\n[5/5] DRY RUN — skipping Facebook post.")
        print(f"  🎬 Video : {output_path}")
        print(f"  📝 Caption: {caption}")
        print("\n✅ Dry run complete!")
        _cleanup(bg_path)
        return

    print(f"\n[5/5] Posting Reel to Facebook...")
    posted = post_reel_to_facebook(output_path, caption)

    if posted:
        print("\n🎉 Quote Reel posted successfully to Facebook!")
    else:
        print("\n❌ Facebook post failed — check credentials and permissions.")

    _cleanup(bg_path)


def _cleanup(bg_path: str):
    """Remove temporary background video file."""
    try:
        if os.path.exists(bg_path):
            os.remove(bg_path)
            print(f"  🧹 Cleaned up temp file: {bg_path}")
    except Exception:
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Quote Video Auto-Poster")
    parser.add_argument("--dry-run",      action="store_true")
    parser.add_argument("--overlay-only", action="store_true", help="Test text overlay only")
    parser.add_argument("--theme",        type=str, default=None,
                        help="Force theme: ofw, health, money, mindset")
    args = parser.parse_args()

    run_pipeline(
        dry_run      = args.dry_run,
        theme        = args.theme,
        overlay_only = args.overlay_only,
    )
