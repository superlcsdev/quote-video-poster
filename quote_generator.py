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
import json
import hashlib
import requests
from datetime import datetime, timedelta
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

Write or select ONE universally powerful quote. It must be impactful by itself
without needing to know the reader's profession.

STRICT RULES:

BANNED PHRASES - automatic reject:
don't give up, keep going, believe in yourself, you can do it,
hard work pays off, stay strong, never stop, you've got this,
it'll pay off, keep pushing, your efforts will pay off,
you are capable, trust the process, you are enough,
nurses, IT professionals, engineers, OFWs, abroad,
optimise, leverage, empower, holistic, synergy

OVERUSED QUOTES - do NOT use any of these ever:
- We are what we repeatedly do. Excellence is not an act, but a habit. (Aristotle)
- Someone is sitting in the shade today because someone planted a tree. (Buffett)
- Whether you think you can or you think you can't, you're right. (Ford)
- The secret of getting ahead is getting started. (Twain)
- In the middle of every difficulty lies opportunity. (Einstein)
- It always seems impossible until it's done. (Mandela)
- You miss 100% of the shots you don't take. (Gretzky)
- Success is not final, failure is not fatal. (Churchill)
- Take care of your body. It's the only place you have to live. (Jim Rohn)
- The first wealth is health. (Emerson)
- Do not save what is left after spending. (Buffett)
- The stock market transfers money from the impatient to the patient. (Buffett)
- The only limit to our realisation of tomorrow will be our doubts. (Roosevelt)

Instead, find a LESS FAMOUS quote from a credible person, or write an original
insight. Something the reader is unlikely to have seen recently.

WHAT MAKES A GREAT QUOTE:
- A less-quoted line from a well-known person (not their signature quote)
- Or a quote from a lesser-known but credible author, thinker, entrepreneur
- Timeless and universally true
- About: delayed gratification, discipline, compound growth, health as wealth,
  courage, building long-term wealth, success mindset

FORMAT:
- If from a person: [Quote text] - [Full Name]
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
        ('"What you do today can improve all your tomorrows." — Ralph Marston', "Make today count 🌅"),
        ('"The only way to achieve the impossible is to believe it is possible." — Charles Kingsleigh', "Believe it 💡"),
        ('"Patience, persistence, and perspiration make an unbeatable combination for success." — Napoleon Hill', "Stay the course 💪"),
        ('"The price of anything is the amount of life you exchange for it." — Henry David Thoreau', "Make it worth it 🎯"),
        ('"Life is not measured by the number of breaths we take, but by the moments that take our breath away." — Maya Angelou', "Live fully 🌟"),
        ('"Do not wait; the time will never be just right. Start where you stand." — Napoleon Hill', "Start where you are 🔥"),
        ('"The man who moves a mountain begins by carrying away small stones." — Confucius', "One stone at a time 🏔️"),
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
        ('"The body achieves what the mind believes." — Napoleon Hill', "Believe it first 💡"),
        ('"To ensure good health: eat lightly, breathe deeply, live moderately, cultivate cheerfulness." — William Londen', "Simple steps 🌿"),
        ('"You can\'t enjoy wealth if you\'re not in good health." — Anonymous', "Health before wealth 💚"),
        ('"Happiness is nothing more than good health and a bad memory." — Albert Schweitzer', "Protect both 😄"),
        ('"It is health that is real wealth and not pieces of gold and silver." — Mahatma Gandhi', "True wealth 🌟"),
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
        ('"Never spend your money before you have earned it." — Thomas Jefferson', "Earn first 💡"),
        ('"Formal education will make you a living; self-education will make you a fortune." — Jim Rohn', "Keep learning 📚"),
        ('"Rich people have small TVs and big libraries, and poor people have small libraries and big TVs." — Zig Ziglar', "Feed your mind 💎"),
        ('"The habit of saving is itself an education; it fosters every virtue, teaches self-denial, cultivates the sense of order." — T.T. Munger', "Build the habit 🌱"),
        ('"Invest in yourself. Your career is the engine of your wealth." — Paul Clitheroe', "Engine of wealth 🚀"),
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
        ('"Motivation is what gets you started. Habit is what keeps you going." — Jim Rohn', "Build the habit ⚡"),
        ('"The secret of your success is determined by your daily agenda." — John C. Maxwell', "Check your agenda 📅"),
        ('"You will never always be motivated, so you must learn to be disciplined." — Anonymous', "Choose discipline 💪"),
        ('"A year from now you may wish you had started today." — Karen Lamb', "Start today 🔥"),
        ('"Do something today that your future self will thank you for." — Sean Patrick Flanery', "For future you 🌟"),
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
        ('"The secret to success is to know something nobody else knows." — Aristotle Onassis', "Know more 📚"),
        ('"Success is not the key to happiness. Happiness is the key to success." — Albert Schweitzer', "Find your why 😊"),
        ('"The road to success is always under construction." — Lily Tomlin', "Keep building 🚧"),
        ('"Action is the foundational key to all success." — Pablo Picasso', "Take action now 🔥"),
        ('"There are no secrets to success. It is the result of preparation, hard work, and learning from failure." — Colin Powell', "No shortcuts 💪"),
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
        ('"But those who wait on the LORD shall renew their strength; they shall mount up with wings like eagles." — Isaiah 40:31 (NKJV)', "Renew your strength 🦅"),
        ('"The LORD bless you and keep you; the LORD make His face shine upon you, and be gracious to you." — Numbers 6:24-25 (NKJV)', "You are blessed 🙏"),
        ('"Come to Me, all you who labor and are heavy laden, and I will give you rest." — Matthew 11:28 (NKJV)', "Find rest in Him 💚"),
        ('"Have I not commanded you? Be strong and of good courage; do not be afraid." — Joshua 1:9a (NKJV)', "He commands it 💪"),
        ('"But seek first the kingdom of God and His righteousness, and all these things shall be added to you." — Matthew 6:33 (NKJV)', "Seek first 🌅"),
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



# ── Quote history — prevents repeats ──────────────────────────────────────────
QUOTE_HISTORY_FILE = "quote_history.json"
QUOTE_HISTORY_DAYS = 60   # don't repeat any quote within this window

# These are the canonical "default" quotes every AI defaults to.
# We ban them from Gemini AND pre-seed history so fallback skips them first.
OVERUSED_QUOTES = [
    "we are what we repeatedly do",          # Aristotle habit
    "someone is sitting in the shade",        # Buffett tree
    "whether you think you can",              # Ford
    "secret of getting ahead is getting started",  # Twain
    "in the middle of every difficulty",      # Einstein
    "it always seems impossible until",       # Mandela
    "you miss 100% of the shots",             # Gretzky
    "success is not final, failure is not fatal",  # Churchill
    "take care of your body. it's the only place",  # Jim Rohn
    "the first wealth is health",             # Emerson
    "do not save what is left after spending",  # Buffett
    "stock market is a device for transferring",  # Buffett
]


def _is_overused(quote_text: str) -> bool:
    """Return True if this quote is in the overused canonical list."""
    lower = quote_text.strip().lower()
    return any(marker in lower for marker in OVERUSED_QUOTES)


def _load_quote_history() -> dict:
    """
    Load {quote_key: last_shown_date} from file.
    If file is empty or missing, pre-seed overused quotes so they go to
    the back of the queue immediately — preventing Gemini defaults from
    dominating when history is fresh.
    """
    history = {}
    if os.path.exists(QUOTE_HISTORY_FILE):
        try:
            with open(QUOTE_HISTORY_FILE) as f:
                history = json.load(f)
        except Exception:
            history = {}

    # Pre-seed: mark any fallback quote that is "overused" as shown 30 days ago
    # This pushes them to the back without fully blocking them
    preseed_date = (datetime.now() - timedelta(days=30)).isoformat()
    changed = False
    for theme, quotes in FALLBACK_QUOTES.items():
        for i, (q, _) in enumerate(quotes):
            key = f"{theme}:{i}"
            if key not in history and _is_overused(q):
                history[key] = preseed_date
                changed = True
    if changed:
        _save_quote_history(history)

    return history




def _save_quote_history(history: dict):
    """Persist history, pruning entries older than QUOTE_HISTORY_DAYS."""
    cutoff = (datetime.now() - timedelta(days=QUOTE_HISTORY_DAYS)).isoformat()
    recent = {k: v for k, v in history.items() if v >= cutoff}
    try:
        with open(QUOTE_HISTORY_FILE, "w") as f:
            json.dump(recent, f, indent=2)
    except Exception as e:
        print(f"  ⚠️  Could not save quote history: {e}")


def _load_quote_history_raw_end(): pass  # marker




def save_shown_quote(theme: str, idx: int = None, content_hash: str = None):
    """
    Record that a quote was shown today.
    idx: fallback library index (for fallback picks)
    content_hash: MD5 of quote text (for Gemini-generated quotes)
    """
    history = _load_quote_history()
    now     = datetime.now().isoformat()
    if idx is not None:
        history[f"{theme}:{idx}"] = now
    if content_hash is not None:
        history[f"{theme}:gemini:{content_hash}"] = now
    key = f"{theme}:{idx}" if idx is not None else f"{theme}:gemini:{content_hash[:8] if content_hash else '?'}"
    _save_quote_history(history)
    print(f"  📝 Quote history saved: {key}")


def _quote_hash(text: str) -> str:
    return hashlib.md5(text.strip().lower().encode()).hexdigest()[:12]


def _gemini_quote_seen_recently(theme: str, quote_text: str) -> bool:
    history = _load_quote_history()
    cutoff  = (datetime.now() - timedelta(days=QUOTE_HISTORY_DAYS)).isoformat()
    key     = f"{theme}:gemini:{_quote_hash(quote_text)}"
    return history.get(key, "1970-01-01") >= cutoff


def _gemini_quote_matches_fallback(theme: str, quote_text: str):
    """
    Check if Gemini generated a quote that exists in our fallback library.
    Strips outer quotes, attribution, trailing punctuation before comparing.
    Returns index or None.
    """
    pool = FALLBACK_QUOTES.get(theme, [])

    def normalise(t):
        t = t.strip()
        # Strip outer curly and straight quote marks
        t = t.strip('\u201c\u201d\u2018\u2019"\'')
        t = t.lower()
        # Remove attribution (everything after dash separators)
        for sep in [' \u2014 ', ' - ', '\u2014', '\u2013']:
            if sep in t:
                t = t.split(sep)[0]
        # Strip trailing quotes, periods, spaces
        t = t.strip().strip('"\'.\u201d\u2019')
        return t

    q_norm = normalise(quote_text)
    for i, (fq, _) in enumerate(pool):
        fq_norm = normalise(fq)
        # Match: shorter text found inside longer (handles partial Gemini quotes)
        if q_norm and fq_norm:
            shorter = q_norm  if len(q_norm)  < len(fq_norm) else fq_norm
            longer  = fq_norm if len(q_norm)  < len(fq_norm) else q_norm
            if shorter and len(shorter) >= 15 and shorter in longer:
                return i
            # Also match on first 30 chars
            if len(q_norm) >= 15 and q_norm[:30] == fq_norm[:30]:
                return i
    return None


def _pick_quote_index(theme: str, pool_size: int) -> int:
    """
    Pick the quote index least recently shown.
    Uses day-seeded random tiebreak among equally-old quotes
    so index 0 is NOT always chosen when history is empty.
    """
    history = _load_quote_history()
    cutoff  = (datetime.now() - timedelta(days=QUOTE_HISTORY_DAYS)).isoformat()

    available = [
        i for i in range(pool_size)
        if history.get(f"{theme}:{i}", "1970-01-01") < cutoff
    ]

    if not available:
        # All shown recently — prefer non-overused quotes
        pool = FALLBACK_QUOTES.get(theme, [])
        non_overused = [i for i in range(pool_size)
                        if i < len(pool) and not _is_overused(pool[i][0])]
        available = non_overused if non_overused else list(range(pool_size))
        print(f"  ⚠️  All {pool_size} quotes for '{theme}' shown recently "
              f"— cycling from {len(available)} non-overused.")

    def last_shown(i: int) -> str:
        return history.get(f"{theme}:{i}", "1970-01-01")

    # Group by oldest date, then pick randomly from that group
    oldest_date = min(last_shown(i) for i in available)
    oldest_pool = [i for i in available if last_shown(i) == oldest_date]

    # Day-seeded deterministic random — different every day, consistent within a day
    day_seed = int(hashlib.md5(
        f"{datetime.now().strftime('%Y-%m-%d')}{theme}tiebreak".encode()
    ).hexdigest(), 16)
    chosen = oldest_pool[day_seed % len(oldest_pool)]

    print(f"  🎲 Selected index {chosen} for '{theme}' "
          f"(last shown: {last_shown(chosen)[:10]}, "
          f"{len(oldest_pool)} in oldest group)")
    return chosen


def _get_fallback_quote(theme: str) -> tuple:
    quotes = FALLBACK_QUOTES.get(theme, FALLBACK_QUOTES["mindset"])
    idx    = _pick_quote_index(theme, len(quotes))
    return quotes[idx], idx


def _generate_via_gemini(theme: str):
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

        # Reject overused canonical quotes (Aristotle, Buffett, etc.)
        if _is_overused(quote):
            print(f"  ⚠️  Gemini returned an overused canonical quote — discarding.")
            return None

        # Reject if this exact quote was shown recently
        if _gemini_quote_seen_recently(theme, quote):
            print(f"  ⚠️  Gemini generated a recently-shown quote — discarding.")
            return None

        subtitles = {
            "ofw":     "For every professional building far from home 🌏",
            "health":  "Good morning ☀️",
            "money":   "Build what lasts 📈",
            "mindset": "Good morning ☀️",
            "success": "Go get it 🏆",
        }
        subtitle = subtitles.get(theme, "Good morning ☀️")
        print(f"  ✅ Gemini quote | theme: {theme} | angle: {angle[:50]}")
        return (quote, subtitle)
    except Exception as e:
        print(f"  ⚠️  Gemini quote error: {e}")
        return None


def generate_quote(theme: str = None) -> dict:
    if not theme:
        theme = get_theme_for_today()

    print(f"\n💬 Generating quote — theme: {theme.upper()}")

    quote    = None
    subtitle = None

    if theme == "biblical":
        print("  📖 Biblical theme — using NKJV library directly.")
        (quote, subtitle), idx = _get_fallback_quote(theme)
        save_shown_quote(theme, idx=idx)

    else:
        gemini_result = _generate_via_gemini(theme)
        if gemini_result:
            quote, subtitle = gemini_result
            # Check if Gemini quote is actually from our fallback library
            lib_idx = _gemini_quote_matches_fallback(theme, quote)
            if lib_idx is not None:
                # Known quote — track by both index AND content hash
                save_shown_quote(theme, idx=lib_idx, content_hash=_quote_hash(quote))
                print(f"  ℹ️  Gemini matched fallback index {lib_idx} — tracked in history")
            else:
                # Original Gemini quote — track by content hash
                save_shown_quote(theme, content_hash=_quote_hash(quote))
        else:
            print("  ⚠️  Using fallback quote library.")
            (quote, subtitle), idx = _get_fallback_quote(theme)
            save_shown_quote(theme, idx=idx)

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
