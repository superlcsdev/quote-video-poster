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
for Filipino professionals — nurses, IT professionals, engineers, architects, pharmacists, 
statisticians, and other degree-holding career-driven individuals in Singapore and the Philippines.

Write ONE original inspirational quote for today. 

Guidelines:
- Theme: {theme}
- Short and punchy — 1 to 2 sentences maximum
- Speaks to professional ambition, career growth, and building wealth — not hardship
- Peer-to-peer tone — like a successful colleague sharing wisdom
- Write in English only — no Tagalog or Taglish words
- Do NOT mention any brand, company, or product
- Format: Just the quote text itself, no quotation marks, no author name

Theme options context:
- ofw: building a career abroad, investing skills and income wisely, creating lasting value
- health: performance, energy, longevity — health as a professional asset
- money: building wealth strategically, financial intelligence, multiple income streams
- mindset: growth mindset, ambition, continuous improvement, professional excellence

Write ONLY the quote. Nothing else."""

# ── Hand-written fallback quotes — professional tone ──────────────────────────
FALLBACK_QUOTES = {
    "ofw": [
        ("Your skills travel with you. Your wealth is built by how wisely you deploy them.", "Build intentionally 🌏"),
        ("Distance from home is the price of ambition. Make sure the return is worth it.", "Invest your years wisely 💫"),
        ("The professional who builds abroad and invests at home wins twice.", "Think long-term 🎯"),
        ("You didn't study hard and move across the world to just collect a salary. Build something.", "Start today 🔥"),
        ("Your expertise has value beyond your job description. Are you monetising it?", "Think bigger 💡"),
        ("The best return on your time abroad is not just the salary — it's what you build with it.", "Build wisely 📈"),
        ("Every year in your career is capital. Invest it, don't just spend it.", "Time is your asset 💎"),
        ("A professional abroad who doesn't invest is just trading time for money at a premium.", "Make it count 🌟"),
        ("You have the skills, the discipline, and the drive. The only question is what you build next.", "Think ahead 🚀"),
        ("The best reason to work hard today is to have real choices tomorrow.", "Keep building 💪"),
    ],
    "health": [
        ("Your career is only as long as your health allows. Protect both.", "Invest in your health 💚"),
        ("Sleep is not a luxury for high performers — it is the foundation of their performance.", "Prioritise rest 🌿"),
        ("The most productive professionals treat their body like their most important business asset.", "Protect your edge 💪"),
        ("Your skills took years to build. So did the body and mind behind them — protect that investment.", "Stay strong 🌱"),
        ("Burnout is not a badge of honour. It is a strategy failure.", "Work smarter 🧠"),
        ("Energy management is a career skill. The highest performers master it first.", "Perform at your best ⚡"),
        ("A healthy routine is not a luxury — it is the infrastructure of a long, successful career.", "Build the foundation 🏗️"),
        ("The professionals who last the longest are not the ones who worked the hardest — they worked the smartest.", "Play the long game 🎯"),
        ("Your cognitive performance, your focus, your output — all start with how well you take care of yourself.", "Start today 💙"),
        ("Prevention is not an expense. It is the most cost-effective investment a professional can make.", "Invest in yourself 🌸"),
    ],
    "money": [
        ("A high salary and financial freedom are not the same thing. The gap is strategy.", "Build the strategy 📈"),
        ("Your income is the seed. Your investments are the tree. Most people never plant.", "Start investing now 🌱"),
        ("The financially free didn't earn more than everyone else. They built systems everyone else ignored.", "Build systems 💡"),
        ("One income stream is a job. Two is a plan. Three is freedom.", "Build your portfolio 🔑"),
        ("The cost of not investing is always higher than the cost of investing.", "Do the math 📊"),
        ("Your degree increased your earning potential. Now increase what you keep.", "Build net worth 💰"),
        ("High earners who never invest are just highly paid employees with an expensive lifestyle.", "Think differently 🎯"),
        ("Wealth is not built in the salary — it is built in the decisions made after the salary arrives.", "Decide wisely 💎"),
        ("The professionals who retire comfortably are not always the highest paid — they are the most intentional.", "Be intentional 🌟"),
        ("Your financial IQ is worth more than your income. Build both.", "Keep learning 📚"),
    ],
    "mindset": [
        ("The professional you are today was built by the decisions you made when no one was watching.", "Keep showing up 🔥"),
        ("Consistency in the small things is what separates good professionals from exceptional ones.", "Stay consistent 💪"),
        ("Your career is a long game. Play it with patience, not just ambition.", "Think long-term 🌅"),
        ("The most successful professionals are not the smartest — they are the most disciplined.", "Build discipline 🎯"),
        ("Growth is not a destination. It is the daily decision to be slightly better than yesterday.", "Grow daily 🌱"),
        ("Comfort is the enemy of progress. The best version of you is just outside your current routine.", "Step forward 🚀"),
        ("Your potential is not defined by your current position — it is defined by your next decision.", "Decide boldly 💫"),
        ("The professionals who change their circumstances are the ones who first change their thinking.", "Think differently 🧠"),
        ("Excellence is not an event. It is a standard you set for yourself every single day.", "Set the standard ⭐"),
        ("The gap between where you are and where you want to be is bridged by one thing: consistent action.", "Take action today 💡"),
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
