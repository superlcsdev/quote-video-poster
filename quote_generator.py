"""
quote_generator.py
Generates morning inspiration quotes for Filipino professionals in SG + PH.
6 themes: ofw, health, money, mindset, success, biblical
10 quotes per theme = 60 total fallback quotes
Uses Gemini → fallback library.
"""

import os
import hashlib
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# ── 6 themes rotating across the week ─────────────────────────────────────────
DAY_THEMES = {
    0: "success",    # Monday
    1: "health",     # Tuesday
    2: "money",      # Wednesday
    3: "biblical",   # Thursday
    4: "ofw",        # Friday
    5: "success",    # Saturday
    6: "mindset",    # Sunday
}

THEMES = ["ofw", "health", "money", "mindset", "success", "biblical"]


QUOTE_PROMPT = """You are writing a morning inspiration quote for Filipino professionals
— nurses, IT workers, engineers, architects — in Singapore and the Philippines.

Write ONE original quote. Theme: {theme}

LANGUAGE RULES:
- Simple plain English. Max 2 sentences. Each sentence max 15 words.
- Sound like a real person talking, not a motivational poster
- Contractions always: "you're", "it's", "don't", "can't", "won't"
- NEVER use: leverage, optimise, empower, unlock, holistic, transformative, synergy
- English only — no Tagalog in the quote
- No brand names

THEME CONTEXT:
- ofw: career abroad, building wealth while working away from family, making it worth it
- health: energy and performance at work, protecting your body and mind, longevity
- money: building wealth not just earning, financial habits that compound over time
- mindset: discipline, resilience, showing up when it's hard, doing the work
- success: achieving goals, winning attitude, going from where you are to where you want to be
- biblical: motivational quote using NKJV scripture or biblical wisdom — encouraging,
  hopeful, and uplifting. For example: "Trust in the LORD with all your heart" (Prov 3:5)
  or a paraphrase of biblical truth about strength, perseverance, or purpose.
  Keep it universal — not preachy. One sentence quote, one sentence reflection.

Write ONLY the quote text. No quotation marks. No author name. Nothing else."""


# ── 60 hand-written fallback quotes (10 per theme) ───────────────────────────
FALLBACK_QUOTES = {
    "ofw": [
        ("Your skills travel with you. Build with them — not just earn with them.", "Make it count 🌏"),
        ("Distance from home is the price of ambition. Make sure the return is worth it.", "Invest wisely 💫"),
        ("You didn't study hard and move abroad just to collect a salary. Build something.", "Start today 🔥"),
        ("The best return on your years abroad isn't the salary — it's what you build with it.", "Think long-term 📈"),
        ("Every year working abroad is capital. Invest it, don't just spend it.", "Time is your asset 💎"),
        ("You left to give your family a better life. Don't forget to build one for yourself too.", "Build both 🎯"),
        ("A career abroad without a plan back home is just delayed regret. Plan now.", "Think ahead 💡"),
        ("The ones who win abroad are not the highest earners. They're the most intentional.", "Be intentional 🌟"),
        ("Your family is proud of what you sacrifice. Make them proud of what you build.", "Keep going 💪"),
        ("One day you'll stop saying goodbye at the airport. Build toward that day now.", "Stay focused 🌅"),
    ],

    "health": [
        ("Your career is only as long as your health allows. Protect both.", "Invest in your health 💚"),
        ("Sleep isn't lazy — it's how high performers stay high performing.", "Rest well 🌿"),
        ("The best version of you at work starts with taking care of you outside work.", "Start with yourself 💪"),
        ("You can't pour from an empty cup. Fill yours first.", "Take care of you 🌱"),
        ("Burnout isn't a badge of honour. It's a warning sign. Listen to it.", "Protect your edge ⚡"),
        ("Your body keeps the score. What is it telling you today?", "Listen to it 💙"),
        ("Small daily habits — sleep, water, movement — outlast any big health goal.", "Be consistent 🌸"),
        ("You invest in your career daily. Your health deserves the same commitment.", "Invest in you 💎"),
        ("A tired professional makes expensive mistakes. Rest is productivity.", "Rest is work 🧠"),
        ("The professionals who last the longest aren't the hardest workers — they're the smartest about rest.", "Work smart 🌿"),
    ],

    "money": [
        ("A high salary and financial freedom are not the same thing. The gap is strategy.", "Build the strategy 📈"),
        ("Your income is the seed. Your investments are the tree. Most people never plant.", "Start planting 🌱"),
        ("One income stream is a job. Two is a plan. Three is freedom.", "Build your plan 🔑"),
        ("The cost of not investing is always higher than the cost of starting.", "Start now 💡"),
        ("Wealth is built in the decisions made after the salary arrives.", "Decide wisely 💰"),
        ("High earners who never save are just highly paid people with expensive lifestyles.", "Think different 🎯"),
        ("The financially free didn't earn more — they kept more and grew it.", "Keep and grow 📊"),
        ("Every SGD you don't invest today is compounding for someone else.", "Your turn 💸"),
        ("It's not about how much you make. It's about how much stays.", "Make it stay 💎"),
        ("The raise is coming. The question is what you do the day it arrives.", "Have a plan 🌟"),
    ],

    "mindset": [
        ("The professional you are today was built by decisions you made when no one was watching.", "Keep showing up 🔥"),
        ("Consistency in the small things separates good professionals from great ones.", "Stay consistent 💪"),
        ("Your career is a long game. Play it with patience, not just ambition.", "Think long-term 🌅"),
        ("Growth is not a destination. It's the daily decision to be slightly better than yesterday.", "Grow daily 🌱"),
        ("Comfort is the enemy of progress. Step just outside your routine today.", "Step forward 🚀"),
        ("You don't need to be the smartest. You need to be the most disciplined.", "Build discipline 🎯"),
        ("The gap between where you are and where you want to be is crossed by consistent action.", "Take action 💡"),
        ("Hard days are not signs to stop. They're proof you're doing something that matters.", "Keep going 🔥"),
        ("Excellence isn't an event. It's a standard you set for yourself every single day.", "Set the standard ⭐"),
        ("The version of you 5 years from now is being built by what you do today.", "Build it now 💫"),
    ],

    "success": [
        ("Success is not about talent. It's about showing up when talent wants to take the day off.", "Show up 🏆"),
        ("The people who get what they want are usually the ones who didn't stop when it got hard.", "Don't stop 🔥"),
        ("Your goal doesn't care how you feel today. Work anyway.", "Work anyway 💪"),
        ("Every successful person has a story about the time they almost quit. They didn't.", "Keep going 🎯"),
        ("Winning isn't luck. It's what happens when preparation meets the moment you've been working for.", "Be ready 💡"),
        ("Stop waiting until you feel ready. You build confidence by doing, not by preparing forever.", "Start now 🚀"),
        ("The size of your success is determined by the size of your belief and the depth of your work.", "Believe and work 🌟"),
        ("Average people wait for the right moment. Successful people make the moment right.", "Make it right ⚡"),
        ("You are one decision away from a completely different life. Make the right one today.", "Decide well 💎"),
        ("The secret most successful people share is simple: they did the work when others didn't.", "Do the work 🏆"),
    ],

    "biblical": [
        ("Trust in the LORD with all your heart, not your own understanding — and He will direct your path. (Prov 3:5–6)", "Trust His plan 🙏"),
        ("I can do all things through Christ who strengthens me. Your limitations are not the final word. (Phil 4:13)", "Strength in Him 💪"),
        ("For God has not given us a spirit of fear, but of power, love, and a sound mind. (2 Tim 1:7)", "Walk in power ✨"),
        ("Commit your work to the LORD, and your plans will be established. Show up with excellence today. (Prov 16:3)", "Work with purpose 🙏"),
        ("Be strong and courageous. The LORD your God is with you wherever you go. (Josh 1:9)", "He goes with you 💫"),
        ("Delight yourself in the LORD, and He will give you the desires of your heart. (Psalm 37:4)", "Seek Him first 🌅"),
        ("Now to Him who is able to do exceedingly abundantly above all that we ask or think. (Eph 3:20)", "He does more 🌟"),
        ("The LORD is my shepherd; I shall not want. Even on your hardest day, you are provided for. (Psalm 23:1)", "You are provided for 🙏"),
        ("And we know that all things work together for good to those who love God. (Rom 8:28)", "Trust the process ✨"),
        ("For I know the plans I have for you — plans to prosper you and give you hope. (Jer 29:11)", "His plans are good 💎"),
    ],
}


def get_theme_for_today() -> str:
    return DAY_THEMES[datetime.now().weekday()]


def _generate_via_gemini(theme: str) -> tuple | None:
    if not GEMINI_API_KEY:
        return None
    try:
        prompt = QUOTE_PROMPT.format(theme=theme)
        resp   = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}",
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=30,
        )
        quote = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        quote = quote.strip('"').strip("'")

        # Subtitle by theme
        subtitles = {
            "ofw":      "For every professional building far from home 🌏",
            "health":   "Good morning ☀️",
            "money":    "Build what lasts 📈",
            "mindset":  "Good morning ☀️",
            "success":  "Go get it 🏆",
            "biblical": "Good morning — His mercies are new today 🙏",
        }
        subtitle = subtitles.get(theme, "Good morning ☀️")
        print(f"  ✅ Gemini generated quote for theme: {theme}")
        return (quote, subtitle)
    except Exception as e:
        print(f"  ⚠️  Gemini quote error: {e}")
        print(f"  ⚠️  Response: {resp.text[:200] if 'resp' in locals() else 'no response'}")
        return None


def _get_fallback_quote(theme: str) -> tuple:
    quotes = FALLBACK_QUOTES.get(theme, FALLBACK_QUOTES["mindset"])
    # Use week number + day to rotate — avoids same quote 2 weeks running
    now      = datetime.now()
    seed     = f"{now.strftime('%Y-%m-%d')}{theme}{now.isocalendar()[1]}"
    idx      = int(hashlib.md5(seed.encode()).hexdigest(), 16) % len(quotes)
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
    for theme in THEMES:
        q = generate_quote(theme)
        print(f"\n{'='*60}")
        print(f"Theme   : {q['theme'].upper()}")
        print(f"Quote   : {q['quote']}")
        print(f"Subtitle: {q['subtitle']}")
