# 🎬 Quote Video Auto-Poster

Daily 7:00 AM SGT morning quote videos for Facebook Reels.
Targets Filipinos in Singapore and Philippines with inspirational quotes
over cinematic background videos (ocean, sunrise, rain, city).

## Output format
- **Size**: 1080×1920 vertical (Facebook Reels optimised)
- **Duration**: 20 seconds
- **Background**: Pixabay royalty-free nature/city videos
- **Text**: Quote centered, gold decorative lines, page watermark

## Theme rotation (daily)

| Day | Theme | Background |
|-----|-------|-----------|
| Monday | 🌏 OFW life | Ocean waves |
| Tuesday | 🏥 Health | Forest / rain |
| Wednesday | 💰 Money | City timelapse |
| Thursday | 🧠 Mindset | Golden sunrise |
| Friday | 🌏 OFW life | Beach sunset |
| Saturday | 🏥 Health | Nature morning |
| Sunday | 💰 Money | City lights |

## Quick Start

```bash
pip install -r requirements.txt
# Also needs ffmpeg:
# Windows: https://ffmpeg.org/download.html
# Mac: brew install ffmpeg
# Linux: sudo apt install ffmpeg

cp .env.example .env
# Fill in your keys

# Test text overlay only (fastest — no video download needed)
python main.py --overlay-only

# Full dry run (downloads video, composes, skips FB post)
python main.py --dry-run

# Force a specific theme
python main.py --dry-run --theme ofw

# Full run
python main.py
```

## API Keys needed

| Key | Get it from | Required |
|-----|-------------|---------|
| `PIXABAY_API_KEY` | https://pixabay.com/api/docs/ (free signup) | ✅ Yes |
| `FB_PAGE_ID` | Same as other posters | ✅ Yes |
| `FB_ACCESS_TOKEN` | Same as other posters | ✅ Yes |
| `GEMINI_API_KEY` | Same as other posters (optional) | ⬜ Optional |

## Get your Pixabay API key (2 minutes)
1. Go to https://pixabay.com/accounts/register/
2. Sign up with email (no credit card)
3. Verify your email
4. Go to https://pixabay.com/api/docs/
5. Your key is shown at the top once logged in

## GitHub Secrets to add
- `PIXABAY_API_KEY` ← new one
- `FB_PAGE_ID` ← same as other repos
- `FB_ACCESS_TOKEN` ← same as other repos
- `GEMINI_API_KEY` ← same as other repos (optional)

## Full automated daily schedule

| Time SGT | Post | Repo |
|----------|------|------|
| 7:00 AM | 🎬 Quote Reel video | quote-video-poster (this repo) |
| 9:00 AM | 🏥 Health news | news-generator |
| 12:30 PM | 📊 Poll post (Mon/Wed/Fri) | poll-poster |
| 7:00 PM | 💰 Finance news | finance-poster |
