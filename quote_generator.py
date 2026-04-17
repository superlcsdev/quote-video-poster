"""
quote_generator.py
Generates morning quotes for Filipino professionals in SG + PH.
6 themes: ofw, health, money, mindset, success, biblical

NON-BIBLICAL: Universally powerful quotes from famous people (Buffett, Churchill,
  Rohn, Kiyosaki, etc.) OR original quotes on delayed gratification, discipline,
  wealth, health, success. NOT profession-specific.
BIBLICAL: Exact NKJV scripture ONLY — no paraphrase, no commentary.
  Gemini is NOT used for biblical. Fallback library is the source.
"""

import os
import hashlib
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# ── Theme rotation across the week ────────────────────────────────────────────
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


# ── Gemini prompt — for NON-BIBLICAL themes only ──────────────────────────────
QUOTE_PROMPT = """You are curating morning quotes for a Facebook page focused on
motivation, financial wisdom, health, and success mindset.

Theme: {theme}
Today's angle: {angle}

Write or select ONE universally powerful quote. It must be impactful by itself —
without needing to know the reader's profession.

STRICT RULES:

BANNED — automatic reject if used:
"don't give up", "keep going", "believe in yourself", "you can do it",
"hard work pays off", "stay strong", "never stop", "you've got this",
"it'll pay off", "keep pushing", "your efforts will pay off",
"you are capable", "trust the process", "you are enough",
"nurses", "IT professionals", "engineers", "OFWs", "abroad",
"optimise", "leverage", "empower", "holistic", "synergy"

WHAT MAKES A GREAT QUOTE:
- Timeless and universally true — anyone reading this can feel it
- Can be from a famous person: Warren Buffett, Jim Rohn, Robert Kiyosaki,
  Winston Churchill, Einstein, Steve Jobs, Aristotle, Roosevelt, Maya Angelou, etc.
- Or an original quote with razor-sharp insight on the theme
- About: delayed gratification, discipline, compound growth, health as wealth,
  courage, building long-term wealth, success mindset

FORMAT:
- If from a famous person: "[Quote]" — [Full Name]
- If original: just the quote, no attribution
- Max 2 sentences. No profession-specific references.

Write ONLY the quote. Nothing else."""

# Angles rotate daily — broad and universal, not profession-specific
THEME_ANGLES = {
    "ofw": [
        "delayed gratification — sacrificing now to build something lasting",
        "the power of playing a long game when others want quick results",
        "doing hard things now so future you has real choices",
        "what long-term commitment to a goal produces that shortcuts never can",
        "patience as a competitive advantage most people refuse to develop",
        "why the people who win are often the ones who outlasted everyone else",
        "planting seeds today for shade you may never personally sit under",
    ],
    "health": [
        "your body as your most important long-term investment",
        "the compound effect of small daily health habits over years",
        "energy and vitality as the foundation of everything you want to achieve",
        "why protecting your health is protecting your future",
        "rest and recovery as part of peak performance, not the opposite",
        "the true cost of neglecting your physical wellbeing",
        "how physical discipline creates mental and financial strength",
    ],
    "money": [
        "compound interest and why patience beats intelligence in building wealth",
        "the difference between earning money and keeping money",
        "why most people stay poor even on good incomes — the mindset gap",
        "the discipline of investing consistently regardless of circumstances",
        "long-term financial thinking vs short-term spending decisions",
        "delayed gratification as the foundation of every fortune ever built",
        "why starting early matters more than investing more",
    ],
    "mindset": [
        "discipline being more reliable than motivation every single day",
        "the compound effect of doing small things consistently over years",
        "why your daily habits determine your future more than your intentions",
        "what separates people who achieve from people who always plan to",
        "the power of showing up on hard days vs easy days",
        "why excellence is a daily standard, not an occasional achievement",
        "the identity shift required to make real change permanent",
    ],
    "success": [
        "starting before you feel ready — why waiting is the biggest risk",
        "why most people don't achieve what they're capable of",
        "courage and action being more powerful than perfect conditions",
        "why ordinary consistent effort beats sporadic brilliance over time",
        "what successful people do differently when no one is watching",
        "the relationship between fear, action, and lasting achievement",
        "why the most important move is always the very next one",
    ],
}


# ── Fallback quote library ─────────────────────────────────────────────────────
# NON-BIBLICAL: Real quotes from famous people — universally impactful.
# BIBLICAL: Exact NKJV text only. No paraphrase. No commentary added.
FALLBACK_QUOTES = {
    "ofw": [
        ('"Someone is sitting in the shade today because someone planted a tree long ago." — Warren Buffett', "Plant your tree 🌳"),
        ('"The secret of getting ahead is getting started." — Mark Twain', "Start now 🔥"),
        ('"You don\'t have to be great to start, but you have to start to be great." — Zig Ziglar', "Start today 🚀"),
        ('"A goal without a plan is just a wish." — Antoine de Saint-Exupéry', "Make the plan 🎯"),
        ('"The future belongs to those who believe in the beauty of their dreams." — Eleanor Roosevelt', "Believe and build 💫"),
        ('"It does not matter how slowly you go as long as you do not stop." — Confucius', "Keep going 🏃"),
        ('"Success usually comes to those who are too busy to be looking for it." — Henry David Thoreau', "Stay busy building 💎"),
        ('"In the long run, we shape our lives, and we shape ourselves." — Eleanor Roosevelt', "Shape your life 🌟"),
        ('"The only way to achieve the impossible is to believe it is possible." — Charles Kingsleigh', "Believe it 💡"),
        ('"What you do today can improve all your tomorrows." — Ralph Marston', "Make today count 🌅"),
    ],
    "health": [
        ('"Take care of your body. It\'s the only place you have to live." — Jim Rohn', "Invest in yourself 💚"),
        ('"The first wealth is health." — Ralph Waldo Emerson', "Health is wealth 💪"),
        ('"He who has health has hope, and he who has hope has everything." — Arabian Proverb', "Protect your health 🌿"),
        ('"Those who think they have no time for healthy eating will sooner or later have to find time for illness." — Edward Stanley', "Make time for health ⏰"),
        ('"The greatest medicine of all is teaching people how not to need it." — Hippocrates', "Prevention wins 🏆"),
        ('"Your body is a temple, but only if you treat it as one." — Astrid Alauda', "Treat it well 🌸"),
        ('"Physical fitness is not only one of the most important keys to a healthy body — it is the basis of dynamic and creative intellectual activity." — John F. Kennedy', "Move to think better ⚡"),
        ('"To keep the body in good health is a duty, otherwise we shall not be able to keep our mind strong and clear." — Buddha', "Mind and body 🧠"),
        ('"Rest when you\'re weary. Refresh and renew yourself, your body, your mind, your spirit." — Ralph Marston', "Rest is productive 😴"),
        ('"A healthy outside starts from the inside." — Robert Urich', "Start within 🌱"),
    ],
    "money": [
        ('"The stock market is a device for transferring money from the impatient to the patient." — Warren Buffett', "Be patient 📈"),
        ('"Do not save what is left after spending, but spend what is left after saving." — Warren Buffett', "Save first 💰"),
        ('"Compound interest is the eighth wonder of the world. He who understands it, earns it; he who doesn\'t, pays it." — Albert Einstein', "Let it compound 📊"),
        ('"It\'s not how much money you make, but how much money you keep, how hard it works for you, and how many generations you keep it for." — Robert Kiyosaki', "Keep and grow 💎"),
        ('"An investment in knowledge pays the best interest." — Benjamin Franklin', "Invest in yourself 📚"),
        ('"Money is a terrible master but an excellent servant." — P.T. Barnum', "Master your money 🔑"),
        ('"Financial freedom is available to those who learn about it and work for it." — Robert Kiyosaki', "Learn then earn 🎯"),
        ('"Wealth is not about having a lot of money; it\'s about having a lot of options." — Chris Rock', "Build your options 🌟"),
        ('"The goal isn\'t more money. The goal is living life on your own terms." — Chris Brogan', "Life on your terms 🚀"),
        ('"The rich invest in time; the poor invest in money." — Warren Buffett', "Invest your time 🕐"),
    ],
    "mindset": [
        ('"We are what we repeatedly do. Excellence, then, is not an act, but a habit." — Aristotle', "Build the habit ⭐"),
        ('"Whether you think you can or you think you can\'t, you\'re right." — Henry Ford', "Think you can 💪"),
        ('"The mind is everything. What you think you become." — Buddha', "Think carefully 🧠"),
        ('"Discipline is the bridge between goals and accomplishment." — Jim Rohn', "Build the bridge 🎯"),
        ('"The only person you are destined to become is the person you decide to be." — Ralph Waldo Emerson', "Decide now 🔥"),
        ('"Success is the sum of small efforts, repeated day in and day out." — Robert Collier', "Small steps daily 🎯"),
        ('"In the middle of every difficulty lies opportunity." — Albert Einstein', "See the opportunity 💡"),
        ('"It always seems impossible until it\'s done." — Nelson Mandela', "Do it anyway 🏆"),
        ('"The secret of change is to focus all of your energy not on fighting the old, but on building the new." — Socrates', "Build the new 🌱"),
        ('"Your time is limited, so don\'t waste it living someone else\'s life." — Steve Jobs', "Live your life 💫"),
    ],
    "success": [
        ('"Success is not final, failure is not fatal: it is the courage to continue that counts." — Winston Churchill', "Have courage 🔥"),
        ('"Opportunities don\'t happen. You create them." — Chris Grosser', "Create yours 🚀"),
        ('"I find that the harder I work, the more luck I seem to have." — Thomas Jefferson', "Work harder 💪"),
        ('"If you are not willing to risk the usual, you will have to settle for the ordinary." — Jim Rohn', "Risk the usual 💎"),
        ('"The only limit to our realisation of tomorrow will be our doubts of today." — Franklin D. Roosevelt', "Drop the doubts 💡"),
        ('"Don\'t be afraid to give up the good to go for the great." — John D. Rockefeller', "Go for great 🌟"),
        ('"Success is walking from failure to failure with no loss of enthusiasm." — Winston Churchill', "Stay enthusiastic 🏆"),
        ('"The difference between who you are and who you want to be is what you do." — Unknown', "Do the work ⚡"),
        ('"Success is liking yourself, liking what you do, and liking how you do it." — Maya Angelou', "Like all three 💫"),
        ('"You miss 100% of the shots you don\'t take." — Wayne Gretzky', "Take the shot 🎯"),
    ],
    "biblical": [
        ('"Trust in the LORD with all your heart, and lean not on your own understanding; in all your ways acknowledge Him, and He shall direct your paths." — Proverbs 3:5-6 (NKJV)', "He will direct you 🙏"),
        ('"I can do all things through Christ who strengthens me." — Philippians 4:13 (NKJV)', "Strength in Him 💪"),
        ('"For God has not given us a spirit of fear, but of power and of love and of a sound mind." — 2 Timothy 1:7 (NKJV)', "Walk in power ✨"),
        ('"And whatever you do, do it heartily, as to the Lord and not to men." — Colossians 3:23 (NKJV)', "Work with purpose 🙏"),
        ('"Be strong and of good courage; do not be afraid, nor be dismayed, for the LORD your God is with you wherever you go." — Joshua 1:9 (NKJV)', "He goes with you 💫"),
        ('"Delight yourself also in the LORD, and He shall give you the desires of your heart." — Psalm 37:4 (NKJV)', "Seek Him first 🌅"),
        ('"Now to Him who is able to do exceedingly abundantly above all that we ask or think, according to the power that works in us." — Ephesians 3:20 (NKJV)', "He does more 🌟"),
        ('"The LORD is my shepherd; I shall not want." — Psalm 23:1 (NKJV)', "You are provided for 🙏"),
        ('"And we know that all things work together for good to those who love God, to those who are the called according to His purpose." — Romans 8:28 (NKJV)', "His purpose holds ✨"),
        ('"For I know the thoughts that I think toward you, says the LORD, thoughts of peace and not of evil, to give you a future and a hope." — Jeremiah 29:11 (NKJV)', "His plans are good 💎"),
    ],
}

# ── Quality filter ─────────────────────────────────────────────────────────────
BANNED_PHRASES = [
    "don't give up", "keep going", "believe in yourself", "you can do it",
    "hard work pays off", "stay strong", "never stop", "you've got this",
    "it'll pay off", "keep pushing", "your efforts will pay off",
    "you are capable", "trust the process", "you are enough",
    "it will pay off", "efforts will surely", "surely pay off",
    "don't stop", "just keep", "hang in there", "it gets better",
    "nurses", "it professionals", "engineers", "ofws",
]


def _is_quality_quote(text: str) -> bool:
    lower = text.lower()
    for phrase in BANNED_PHRASES:
        if phrase in lower:
            print(f"  ⚠️  Quote rejected — banned phrase: '{phrase}'")
            return False
    if len(text.strip()) < 30:
        print(f"  ⚠️  Quote rejected — too short")
        return False
    return True


def _get_angle(theme: str) -> str:
    angles  = THEME_ANGLES.get(theme, ["a universal truth about growth and discipline"])
    now     = datetime.now()
    seed    = f"{now.strftime('%Y-%m-%d')}{theme}"
    idx     = int(hashlib.md5(seed.encode()).hexdigest(), 16) % len(angles)
    return angles[idx]


def get_theme_for_today() -> str:
    return DAY_THEMES[datetime.now().weekday()]


def _get_fallback_quote(theme: str) -> tuple:
    quotes = FALLBACK_QUOTES.get(theme, FALLBACK_QUOTES["mindset"])
    now    = datetime.now()
    seed   = f"{now.strftime('%Y-%m-%d')}{theme}{now.timetuple().tm_yday}"
    idx    = int(hashlib.md5(seed.encode()).hexdigest(), 16) % len(quotes)
    return quotes[idx]


def _generate_via_gemini(theme: str) -> tuple | None:
    # Biblical quotes NEVER go through Gemini — exact NKJV only from fallback library
    if theme == "biblical":
        return None
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
            return None

        subtitles = {
            "ofw":     "For every professional building far from home 🌏",
            "health":  "Good morning ☀️",
            "money":   "Build what lasts 📈",
            "mindset": "Good morning ☀️",
            "success": "Go get it 🏆",
        }
        subtitle = subtitles.get(theme, "Good morning ☀️")
        print(f"  ✅ Gemini quote for theme: {theme} | angle: {angle[:50]}")
        return (quote, subtitle)
    except Exception as e:
        print(f"  ⚠️  Gemini quote error: {e}")
        return None


def generate_quote(theme: str = None) -> dict:
    if not theme:
        theme = get_theme_for_today()

    print(f"\n💬 Generating quote — theme: {theme.upper()}")

    # Biblical always uses fallback library (exact NKJV, no Gemini)
    if theme == "biblical":
        print("  📖 Biblical theme — using NKJV library directly.")
        quote, subtitle = _get_fallback_quote(theme)
    else:
        result = _generate_via_gemini(theme)
        if result:
            quote, subtitle = result
        else:
            print("  ⚠️  Using fallback quote library.")
            quote, subtitle = _get_fallback_quote(theme)

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
