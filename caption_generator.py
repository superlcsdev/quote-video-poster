"""
caption_generator.py
Generates the Facebook post caption to accompany the quote video.
Short, warm, invites engagement.
"""

import os
import hashlib
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

CAPTION_PROMPT = """Write a short Facebook post caption for a morning quote video.
The audience is Filipino professionals — nurses, IT workers, engineers — in Singapore and Philippines.

Quote: "{quote}"
Theme: {theme}

LANGUAGE RULES:
- 2–3 short sentences max. Each sentence under 15 words.
- Sound like a real person, not a motivational poster
- Simple everyday words. Contractions always: "you're", "it's", "don't"
- NEVER use: leverage, optimise, empower, transformative, holistic, actionable
- Start with an emoji that fits the mood
- End with a question or short CTA that feels natural
- Don't repeat the quote. Don't mention any brand or product.

Write ONLY the caption. No preamble."""

FALLBACK_CAPTIONS = {
    "ofw": [
        "🌅 Good morning.\nYou left home to build something better — don't lose sight of that.\nWhat's keeping you going this week? Drop it below 👇",
        "💫 This one's for anyone building their career far from home.\nIt's not easy. But it's worth it.\nDrop a ❤️ if this hits close. 👇",
        "☀️ Start the week with this.\nYou're not just working — you're building.\nWhich part of this speaks to you? Comment below 💬",
    ],
    "health": [
        "🌿 Good morning.\nYour body keeps score — especially after long shifts and late nights.\nWhat's one thing you're doing for yourself today? 💬",
        "💚 This one's for the professionals who give everything at work but forget to take care of themselves.\nYou matter too.\nDrop your healthy habit below! 👇",
        "🌸 Morning check-in.\nAre you running on full or running on empty?\nOne small thing today. That's all it takes. 💬",
    ],
    "money": [
        "💰 Good morning.\nA good salary is just the start — what you build with it is what counts.\nWhat's your #1 money goal right now? Drop it below 👇",
        "📈 This hit differently this morning.\nEarning well and building wealth aren't the same thing.\nWhere are you in this journey? 💬",
        "🌟 Quick morning reminder.\nYour income is the seed. What you do with it is the garden.\nSave this — and share with someone who needs it 👇",
    ],
    "mindset": [
        "🔥 Good morning.\nSome days are harder than others. Show up anyway.\nDrop a 💪 if you're ready to make today count 👇",
        "💫 This is for anyone who needs a reset today.\nProgress doesn't have to be dramatic — it just has to be real.\nWhat's one thing you're working on? Comment below 💬",
        "🌅 Start the week with this thought.\nYou don't need a perfect plan. You need to take the next step.\nDrop a ❤️ if this resonates 👇",
    ],
}


def generate_caption(quote: str, theme: str) -> str:
    if GEMINI_API_KEY:
        try:
            prompt = CAPTION_PROMPT.format(quote=quote, theme=theme)
            resp   = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}",
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=30,
            )
            caption = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
            print("  ✅ Gemini generated caption.")
            return caption
        except Exception as e:
            print(f"  ⚠️  Gemini caption error: {e}")

    print("  ⚠️  Using fallback caption.")
    captions = FALLBACK_CAPTIONS.get(theme, FALLBACK_CAPTIONS["mindset"])
    seed     = datetime.now().strftime("%Y-%m-%d") + theme + "cap"
    idx      = int(hashlib.md5(seed.encode()).hexdigest(), 16) % len(captions)
    return captions[idx]
