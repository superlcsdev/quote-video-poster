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


QUOTE_PROMPT = """You are writing a morning quote for Filipino professionals in Singapore and Philippines.
Theme: {theme}
Today's angle: {angle}

YOUR JOB: Write ONE quote that stops someone mid-scroll. It must feel like it was written
specifically for a Filipino nurse, engineer, or IT professional — not a generic human.

STRICT RULES — read these carefully before writing:

BANNED PHRASES (automatic reject if you use any of these):
"don't give up", "keep going", "believe in yourself", "you can do it",
"hard work pays off", "stay strong", "never stop", "you've got this",
"it'll pay off", "keep pushing", "your efforts will pay off",
"you are capable", "trust the process", "you are enough"

These are banned because they're what every generic motivational account posts.
If your quote sounds like it could be on a poster in a dentist's waiting room — rewrite it.

WHAT MAKES A GREAT QUOTE (use one of these approaches):
1. A SHARP OBSERVATION — something true that most people haven't thought about
   Example: "A nurse who doesn't protect her sleep is giving away the one thing her patients need most."
2. A REFRAME — takes a familiar idea and flips the angle
   Example: "The salary you're chasing is someone else's idea of success. Build your own number."
3. A SPECIFIC TRUTH — concrete, tied to their actual professional life
   Example: "You optimise code and patient care all day. Your finances deserve the same attention."
4. A CHALLENGE — calls them to act, not just feel better
   Example: "The plan you haven't started yet costs more every month you wait."
5. BIBLICAL (for biblical theme only) — pair a NKJV verse with a one-line professional application
   Example: "He gives strength to the weary (Isaiah 40:29). That 12-hour shift didn't finish you — it proved you."

LANGUAGE:
- Max 2 sentences. Each sentence max 15 words.
- Sound like a smart friend who happens to know the truth — not a life coach
- Contractions: "you're", "it's", "don't", "can't"
- NO: leverage, optimise, empower, unlock, holistic, transformative, synergy
- English only. No brand names.

Write ONLY the quote. No quotation marks. No preamble. No author name."""

# Angles rotate daily so Gemini gets a fresh creative constraint each day
THEME_ANGLES = {
    "ofw": [
        "the financial gap between earning abroad and actually building wealth",
        "what returning home with nothing means after years of sacrifice",
        "the difference between the highest earner and the most intentional professional abroad",
        "why your years abroad are capital — not just income",
        "building for yourself, not just for the family back home",
        "the opportunity cost of not investing while working in Singapore",
        "what 10 years abroad should actually produce financially",
    ],
    "health": [
        "why sleep is a professional skill, not a personal luxury",
        "the hidden career cost of ignoring your physical health",
        "burnout as a strategy failure, not a badge of honour",
        "why nurses and engineers who skip self-care are taking a career risk",
        "the connection between your body's condition and your professional output",
        "how small daily health habits compound just like financial investments",
        "what exhaustion is actually telling a high-performing professional",
    ],
    "money": [
        "the difference between a high salary and actual net worth",
        "why most professionals with good incomes still feel financially behind",
        "the math of starting to invest 5 years earlier vs later",
        "lifestyle inflation as the silent wealth killer for professionals",
        "why one income stream is a financial risk, not a stable foundation",
        "the real cost of waiting until you feel ready to invest",
        "how compounding works against you every month you delay",
    ],
    "mindset": [
        "why discipline on bad days matters more than motivation on good ones",
        "what separates professionals who advance from those who plateau",
        "the power of doing the work when no one is watching",
        "why being consistent beats being talented in the long run",
        "what happens to your career when you stop choosing comfort",
        "the identity shift that happens when you commit to growth",
        "why the hardest step is always the one you take today",
    ],
    "success": [
        "why successful people start before they feel ready",
        "the real difference between people who achieve and people who plan to",
        "what most successful professionals did differently in their first 5 years",
        "why waiting for the right moment is the most expensive habit",
        "the mindset of someone who wins — and why most people don't have it",
        "what separates high achievers: it's not talent, it's consistency of action",
        "the one decision that changes your trajectory more than any skill",
    ],
    "biblical": [
        "God's provision for professionals carrying heavy loads (Isaiah 40:29 or Phil 4:19)",
        "strength for the weary — for nurses and workers on long shifts (Isaiah 40:31)",
        "moving forward with purpose when the path is unclear (Prov 3:5-6 or Jer 29:11)",
        "doing excellent work as an act of faith (Col 3:23)",
        "not being anxious about the future as a professional (Phil 4:6-7)",
        "God's plans being bigger than our current circumstances (Jer 29:11 or Eph 3:20)",
        "the peace that comes from trusting God over our own plans (Prov 16:3)",
    ],
}


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



# These are the phrases that make a quote worthless — if Gemini produces them, reject it
BANNED_PHRASES = [
    "don't give up", "keep going", "believe in yourself", "you can do it",
    "hard work pays off", "stay strong", "never stop", "you've got this",
    "it'll pay off", "keep pushing", "your efforts will pay off",
    "you are capable", "trust the process", "you are enough",
    "it will pay off", "efforts will surely", "surely pay off",
    "don't stop", "just keep", "hang in there", "it gets better",
]


def _is_quality_quote(text: str) -> bool:
    """Reject generic, bland quotes. Return True only if quote passes quality bar."""
    lower = text.lower()
    # Reject if it contains any banned phrase
    for phrase in BANNED_PHRASES:
        if phrase in lower:
            print(f"  ⚠️  Quote rejected — contains banned phrase: '{phrase}'")
            return False
    # Reject if it's too short (likely incomplete)
    if len(text.strip()) < 40:
        print(f"  ⚠️  Quote rejected — too short ({len(text)} chars)")
        return False
    # Reject if it ends with generic motivational sign-offs
    generic_endings = ["you've got this!", "you can do it!", "keep going!", "don't give up!"]
    for ending in generic_endings:
        if lower.strip().endswith(ending):
            print(f"  ⚠️  Quote rejected — generic ending")
            return False
    return True


def _get_angle(theme: str) -> str:
    """Pick a fresh creative angle for Gemini based on date."""
    angles  = THEME_ANGLES.get(theme, ["a fresh perspective on this topic"])
    now     = datetime.now()
    seed    = f"{now.strftime('%Y-%m-%d')}{theme}"
    idx     = int(hashlib.md5(seed.encode()).hexdigest(), 16) % len(angles)
    return angles[idx]


def _generate_via_gemini(theme: str) -> tuple | None:
    if not GEMINI_API_KEY:
        return None
    try:
        angle  = _get_angle(theme)
        prompt = QUOTE_PROMPT.format(theme=theme, angle=angle)
        resp   = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}",
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=30,
        )
        quote = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        quote = quote.strip('"').strip("'")

        if not _is_quality_quote(quote):
            print(f"  ⚠️  Gemini output failed quality check — using fallback.")
            return None

        subtitles = {
            "ofw":      "For every professional building far from home 🌏",
            "health":   "Good morning ☀️",
            "money":    "Build what lasts 📈",
            "mindset":  "Good morning ☀️",
            "success":  "Go get it 🏆",
            "biblical": "His mercies are new today 🙏",
        }
        subtitle = subtitles.get(theme, "Good morning ☀️")
        print(f"  ✅ Gemini generated quality quote for theme: {theme}")
        print(f"     Angle: {angle[:60]}")
        return (quote, subtitle)
    except Exception as e:
        print(f"  ⚠️  Gemini quote error: {e}")
        print(f"  ⚠️  Response: {resp.text[:200] if 'resp' in locals() else 'no response'}")
        return None


def _get_fallback_quote(theme: str) -> tuple:
    quotes = FALLBACK_QUOTES.get(theme, FALLBACK_QUOTES["mindset"])
    # Seed with date + week number + day-of-year for maximum spread
    now     = datetime.now()
    seed    = f"{now.strftime('%Y-%m-%d')}{theme}{now.timetuple().tm_yday}"
    idx     = int(hashlib.md5(seed.encode()).hexdigest(), 16) % len(quotes)
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
