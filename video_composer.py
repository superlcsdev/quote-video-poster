"""
video_composer.py
Composes the final quote video:
  - Background video from Pixabay (looped to 20s if shorter)
  - Dark overlay for text readability
  - Quote text centered (large, bold)
  - Subtitle text below quote
  - Page handle watermark bottom right
  - Output: 1080x1920 vertical MP4 for Facebook Reels
"""

import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
try:
    # moviepy 2.x
    from moviepy import VideoFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips
except ImportError:
    # moviepy 1.x fallback
    from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips
from dotenv import load_dotenv

load_dotenv()

# ── Output config ──────────────────────────────────────────────────────────────
OUTPUT_WIDTH   = 1080
OUTPUT_HEIGHT  = 1920
TARGET_DURATION = 20   # seconds — ideal for Facebook Reels
FPS            = 30

# ── Font config ────────────────────────────────────────────────────────────────
FONT_PATHS_BOLD = [
    "arialbd.ttf",
    "Arial_Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]
FONT_PATHS_REGULAR = [
    "arial.ttf",
    "Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]


def _load_font(paths: list, size: int):
    win_fonts = os.path.join(os.environ.get("WINDIR", ""), "Fonts")
    for path in paths:
        for candidate in [path, os.path.join(win_fonts, path)]:
            if os.path.exists(candidate):
                try:
                    return ImageFont.truetype(candidate, size)
                except Exception:
                    pass
    return ImageFont.load_default()


def _make_text_overlay(quote: str, subtitle: str, author: str,
                        width: int = OUTPUT_WIDTH,
                        height: int = OUTPUT_HEIGHT) -> np.ndarray:
    """
    Create a transparent RGBA image with text overlay.
    Returns numpy array for MoviePy.
    """
    img  = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # ── Dark gradient overlay (full height, stronger center) ──────
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    # Solid dark center band where text sits
    band_top    = height // 4
    band_bottom = (height * 3) // 4
    for y in range(height):
        if band_top <= y <= band_bottom:
            alpha = 160
        elif y < band_top:
            # fade up
            alpha = int(160 * (y - band_top // 2) / (band_top // 2)) if y > band_top // 2 else 0
        else:
            # fade down
            dist  = y - band_bottom
            alpha = max(0, int(160 * (1 - dist / (height // 4))))
        ov_draw.rectangle([(0, y), (width, y + 1)], fill=(0, 0, 0, alpha))
    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)

    # ── Fonts ─────────────────────────────────────────────────────
    font_quote    = _load_font(FONT_PATHS_BOLD,    72)
    font_subtitle = _load_font(FONT_PATHS_REGULAR, 40)
    font_author   = _load_font(FONT_PATHS_BOLD,    36)
    font_handle   = _load_font(FONT_PATHS_REGULAR, 32)

    pad       = 100                        # safe margin each side
    max_text_w = width - (pad * 2)         # max pixel width for text

    # ── Pixel-aware word wrap ─────────────────────────────────────
    def wrap_by_pixels(text, font, max_px):
        """Wrap text based on actual rendered pixel width, not char count."""
        words   = text.split()
        lines   = []
        current = ""
        for word in words:
            test = f"{current} {word}".strip()
            bbox = draw.textbbox((0, 0), test, font=font)
            if bbox[2] > max_px and current:
                lines.append(current)
                current = word
            else:
                current = test
        if current:
            lines.append(current)
        return lines

    lines     = wrap_by_pixels(quote, font_quote, max_text_w)
    line_h    = 90
    total_quote_h = len(lines) * line_h
    quote_start_y = (height - total_quote_h) // 2 - 60

    # ── Draw quote lines (centered) ───────────────────────────────
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font_quote)
        lw   = bbox[2] - bbox[0]
        x    = (width - lw) // 2
        y    = quote_start_y + i * line_h
        # Shadow
        draw.text((x + 3, y + 3), line, font=font_quote, fill=(0, 0, 0, 180))
        draw.text((x,     y),     line, font=font_quote, fill=(255, 255, 255, 255))

    # ── Decorative line above/below quote ─────────────────────────
    line_y_top = quote_start_y - 30
    draw.rectangle([(pad * 2, line_y_top), (width - pad * 2, line_y_top + 3)],
                   fill=(255, 215, 0, 180))   # gold line

    line_y_bot = quote_start_y + total_quote_h + 20
    draw.rectangle([(pad * 2, line_y_bot), (width - pad * 2, line_y_bot + 3)],
                   fill=(255, 215, 0, 180))

    # ── Subtitle ──────────────────────────────────────────────────
    sub_y    = line_y_bot + 30
    sub_bbox = draw.textbbox((0, 0), subtitle, font=font_subtitle)
    sub_x    = (width - (sub_bbox[2] - sub_bbox[0])) // 2
    draw.text((sub_x + 2, sub_y + 2), subtitle, font=font_subtitle, fill=(0, 0, 0, 160))
    draw.text((sub_x,     sub_y),     subtitle, font=font_subtitle, fill=(220, 200, 120, 255))

    # ── Author / page handle (bottom center) ─────────────────────
    handle_text = f"— {author}"
    h_bbox = draw.textbbox((0, 0), handle_text, font=font_author)
    h_x    = (width - (h_bbox[2] - h_bbox[0])) // 2
    h_y    = height - 120
    draw.text((h_x + 2, h_y + 2), handle_text, font=font_author, fill=(0, 0, 0, 150))
    draw.text((h_x,     h_y),     handle_text, font=font_author, fill=(255, 255, 255, 220))

    # ── Small handle watermark bottom right ───────────────────────
    wm_text = "@mentorlawrencesia"
    wm_bbox = draw.textbbox((0, 0), wm_text, font=font_handle)
    wm_x    = width - (wm_bbox[2] - wm_bbox[0]) - 40
    wm_y    = height - 60
    draw.text((wm_x, wm_y), wm_text, font=font_handle, fill=(255, 255, 255, 140))

    return np.array(img)


def _resize_clip(clip, new_w, new_h):
    """Resize clip — handles moviepy 1.x and 2.x API difference."""
    try:
        return clip.resized((new_w, new_h))        # moviepy 2.x
    except AttributeError:
        return clip.resize((new_w, new_h))         # moviepy 1.x


def _subclip(clip, start, end):
    """Subclip — handles moviepy 1.x and 2.x."""
    try:
        return clip.subclipped(start, end)          # moviepy 2.x
    except AttributeError:
        return clip.subclip(start, end)             # moviepy 1.x


def _remove_audio(clip):
    """Remove audio — handles moviepy 1.x and 2.x."""
    try:
        return clip.without_audio()                 # both versions
    except Exception:
        try:
            return clip.set_audio(None)             # fallback
        except Exception:
            return clip


def _make_image_clip(array, duration):
    """Create ImageClip — handles moviepy 1.x and 2.x."""
    try:
        # moviepy 2.x: duration passed to constructor
        return ImageClip(array, duration=duration)
    except TypeError:
        # moviepy 1.x: chained method
        return ImageClip(array).set_duration(duration).set_fps(FPS)


def compose_video(bg_video_path: str, quote: str, subtitle: str,
                  author: str, output_path: str) -> str | None:
    """
    Compose final Reels video:
    1. Load background video, crop/resize to 1080x1920
    2. Loop to TARGET_DURATION seconds
    3. Composite text overlay on top
    4. Export MP4
    Returns output path or None on failure.
    """
    try:
        print(f"  🎬 Loading background video...")
        clip = VideoFileClip(bg_video_path)

        # ── Resize & crop to 1080x1920 vertical ──────────────────
        orig_w, orig_h = clip.size
        scale_w = OUTPUT_WIDTH  / orig_w
        scale_h = OUTPUT_HEIGHT / orig_h
        scale   = max(scale_w, scale_h)

        new_w = int(orig_w * scale)
        new_h = int(orig_h * scale)
        clip  = _resize_clip(clip, new_w, new_h)

        # Center crop
        x1 = (new_w - OUTPUT_WIDTH)  // 2
        y1 = (new_h - OUTPUT_HEIGHT) // 2
        clip = clip.crop(x1=x1, y1=y1,
                         x2=x1 + OUTPUT_WIDTH,
                         y2=y1 + OUTPUT_HEIGHT)

        # ── Loop to TARGET_DURATION ───────────────────────────────
        if clip.duration < TARGET_DURATION:
            loops_needed = int(np.ceil(TARGET_DURATION / clip.duration))
            clip = concatenate_videoclips([clip] * loops_needed)
        clip = _subclip(clip, 0, TARGET_DURATION)
        clip = _remove_audio(clip)

        print(f"  ✅ Background ready: {OUTPUT_WIDTH}x{OUTPUT_HEIGHT} @ {TARGET_DURATION}s")

        # ── Create text overlay as ImageClip ─────────────────────
        print(f"  ✍️  Rendering text overlay...")
        text_array = _make_text_overlay(quote, subtitle, author)
        text_clip  = _make_image_clip(text_array, TARGET_DURATION)

        # ── Composite ─────────────────────────────────────────────
        final = CompositeVideoClip([clip, text_clip],
                                   size=(OUTPUT_WIDTH, OUTPUT_HEIGHT))

        # ── Export ────────────────────────────────────────────────
        print(f"  💾 Exporting video → {output_path}")
        final.write_videofile(
            output_path,
            codec         = "libx264",
            audio         = False,
            fps           = FPS,
            preset        = "fast",
            ffmpeg_params = ["-crf", "23"],
            logger        = None,
        )

        # Cleanup
        clip.close()
        final.close()

        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"  ✅ Video exported: {size_mb:.1f} MB")
        return output_path

    except Exception as e:
        print(f"  ❌ Video composition error: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    # Test text overlay generation only (no video file needed)
    print("Testing text overlay generation...")
    arr = _make_text_overlay(
        quote    = "You didn't come this far to only come this far.",
        subtitle = "For every OFW grinding far from home 💪",
        author   = "mentorlawrencesia",
    )
    img = Image.fromarray(arr)
    img.save("test_overlay.png")
    print(f"✅ Overlay saved: test_overlay.png ({arr.shape})")
