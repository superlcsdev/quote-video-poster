"""
quote_generator.py
Generates OFW/finance/health inspirational quotes for Filipino audience.
Uses Gemini → 60+ hand-written fallback quotes.
"""

import os
import random
import hashlib
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

QUOTE_PROMPT = """You are a content creator writing daily morning inspiration quotes 
for Filipinos in Singapore and the Philippines — OFWs, employees, and people building 
side income and better health habits.

Write ONE original inspirational quote for today. 

Guidelines:
- Theme: {theme}
- Short and punchy — 1 to 2 sentences maximum
- Deeply relatable to hardworking Filipinos
- Warm, encouraging, never preachy
- Occasionally use 1 Tagalog word for warmth (optional, only if natural)
- Do NOT mention any brand, company, or product
- Format: Just the quote text itself, no quotation marks, no author name

Theme options context:
- ofw: working hard abroad, missing family, sacrifice, resilience, hope for the future
- health: taking care of yourself, small daily habits, energy, wellness, self-love
- money: saving, building wealth slowly, financial freedom, multiple income streams
- mindset: growth, perseverance, believing in yourself, not giving up

Write ONLY the quote. Nothing else."""

# ── 60+ hand-written fallback quotes ──────────────────────────────────────────
FALLBACK_QUOTES = {
    "ofw": [
        ("Every peso you save today is a dream you're building for tomorrow.", "For every OFW grinding far from home 💪"),
        ("You left home to build a better one. That sacrifice is never wasted.", "Your hard work matters 🏠❤️"),
        ("Being far from family doesn't mean being far from your purpose.", "Stay strong, kababayan 🌏"),
        ("The distance between you and your dreams is measured in discipline, not miles.", "Keep going 💫"),
        ("You are not just working for a salary. You are building a legacy.", "For every hardworking OFW 🙏"),
        ("Homesickness is the price of love. And you pay it every day with grace.", "You are braver than you know ❤️"),
        ("Your family may not see every long day you put in — but every sacrifice counts.", "Hindi nasasayang ang pagod mo 💪"),
        ("One day, you won't have to say goodbye at the airport anymore.", "Hold on to that vision 🌅"),
        ("The strongest people are those who smile through hard times and fight for their dreams.", "That's you 🔥"),
        ("You didn't come this far to only come this far.", "Keep pushing forward 💫"),
    ],
    "health": [
        ("Your body is the only home you'll live in forever. Take care of it.", "Start with one small step today 🌿"),
        ("Rest is not laziness. It is how you come back stronger.", "Give yourself permission to recharge 💚"),
        ("Drinking water, sleeping early, and moving your body — simple habits that change everything.", "Start today 💧"),
        ("You cannot pour from an empty cup. Fill yourself up first.", "Self-care is not selfish 🌸"),
        ("Small consistent actions beat dramatic changes every time.", "One healthy choice at a time 💪"),
        ("Your health is an investment, not an expense.", "Protect it 🏃"),
        ("The best project you'll ever work on is yourself.", "One habit at a time 🌱"),
        ("Sleep, water, movement, and peace of mind. These are free — and priceless.", "Choose yourself today 💙"),
        ("You don't have to be perfect. You just have to be consistent.", "Progress over perfection 🌿"),
        ("A healthy outside starts from the inside.", "Nourish yourself 🌸"),
    ],
    "money": [
        ("Financial freedom begins with one decision: to start.", "The best time is now 💰"),
        ("Rich is not how much you earn. It's how much you keep and grow.", "Build wisely 📈"),
        ("One income is a risk. Two incomes is a plan. Three is a strategy.", "Start building today 💡"),
        ("The money you don't spend today is the freedom you buy for tomorrow.", "Save with intention 💸"),
        ("Stop working for money. Start making money work for you.", "Learn, invest, grow 🌱"),
        ("Every large fortune started with a single small decision to save.", "Start small, dream big 🏦"),
        ("Your salary is not your net worth. Your habits are.", "Build the right ones 💪"),
        ("It's not about having a lot of money. It's about having enough choices.", "Financial freedom 🗝️"),
        ("The financially free didn't find a shortcut. They found consistency.", "Stay the course 📊"),
        ("Invest in yourself first. Everything else follows.", "You are your best asset 💡"),
    ],
    "mindset": [
        ("You don't need a new year to start over. You just need a new decision.", "Today is enough 🌅"),
        ("Growth is uncomfortable. That discomfort means you're moving forward.", "Keep going 🔥"),
        ("Stop waiting for the perfect moment. Start with the imperfect one you have now.", "Begin today 💫"),
        ("The version of you 5 years from now is built by what you do today.", "Make it count 🌟"),
        ("Consistency is quiet. But its results are loud.", "Show up every day 💪"),
        ("You are not behind. You are exactly where you need to be to move forward.", "Trust the process 🌸"),
        ("What you do on the hard days defines who you become.", "Keep moving forward 🔥"),
        ("Small progress is still progress. Don't stop.", "One step at a time 🌱"),
        ("The only person you need to be better than is the one you were yesterday.", "Grow daily 💫"),
        ("Believe in the slow work. Not everything blooms overnight.", "Magtiyaga — good things take time 🌼"),
    ],
}

# Theme rotation by day of week
DAY_THEMES = {
    0: "ofw",      # Monday
    1: "health",   # Tuesday
    2: "money",    # Wednesday
    3: "mindset",  # Thursday
    4: "ofw",      # Friday
    5: "health",   # Saturday
    6: "money",    # Sunday
}


def get_theme_for_today() -> str:
    return DAY_THEMES[datetime.now().weekday()]


def _generate_via_gemini(theme: str) -> tuple | None:
    if not GEMINI_API_KEY:
        return None
    try:
        prompt = QUOTE_PROMPT.format(theme=theme)
        resp = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}",
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=30,
        )
        quote = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        quote = quote.strip('"').strip("'")
        subtitle = "Morning inspiration for you ☀️"
        print(f"  ✅ Gemini generated quote for theme: {theme}")
        return (quote, subtitle)
    except Exception as e:
        print(f"  ⚠️  Gemini quote error: {e}")
        print(f"  ⚠️  Response: {resp.text[:200] if 'resp' in locals() else 'no response'}")
        return None


def _get_fallback_quote(theme: str) -> tuple:
    quotes = FALLBACK_QUOTES.get(theme, FALLBACK_QUOTES["mindset"])
    seed   = datetime.now().strftime("%Y-%m-%d") + theme
    idx    = int(hashlib.md5(seed.encode()).hexdigest(), 16) % len(quotes)
    return quotes[idx]


def generate_quote(theme: str = None) -> dict:
    if not theme:
        theme = get_theme_for_today()

    print(f"\n💬 Generating quote for theme: {theme.upper()}")

    result = _generate_via_gemini(theme)
    if not result:
        print("  ⚠️  Using fallback quote library.")
        result = _get_fallback_quote(theme)

    quote, subtitle = result
    return {
        "theme":    theme,
        "quote":    quote,
        "subtitle": subtitle,
        "author":   "mentorlawrencesia",
    }


if __name__ == "__main__":
    from quote_generator import FALLBACK_QUOTES
    for theme in ["ofw", "health", "money", "mindset"]:
        q = generate_quote(theme)
        print(f"\n{'='*60}")
        print(f"Theme : {q['theme'].upper()}")
        print(f"Quote : {q['quote']}")
        print(f"Sub   : {q['subtitle']}")
