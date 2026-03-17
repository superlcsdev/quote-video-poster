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

CAPTION_PROMPT = """Write a short Facebook post caption to accompany this morning quote video.
The audience is Filipinos in Singapore and Philippines.

Quote: "{quote}"
Theme: {theme}

Rules:
- 2-3 sentences maximum
- Start with an emoji that matches the mood
- Warm and conversational, like a friend sharing this
- End with a question or CTA that invites comments
- Do NOT repeat the quote verbatim
- Do NOT mention any brand or product

Write ONLY the caption."""

FALLBACK_CAPTIONS = {
    "ofw": [
        "🌅 Starting your Monday with this reminder — your sacrifices are never in vain.\nEvery hard day is one step closer to the life you're building.\nWhich part of this speaks to you today? 💬",
        "🌊 For every OFW reading this in the early morning before work — this one's for you.\nYou are doing something extraordinary. Don't forget that.\nDrop a ❤️ if this resonated with you! 👇",
        "☀️ Good morning! Let this be your fuel for the week ahead.\nThe distance from your family makes your love stronger, not weaker.\nShare this with an OFW who needs to hear it today! 🙏",
    ],
    "health": [
        "🌿 Good morning! Your body is talking to you every day.\nThe question is — are you listening? Small habits compound into big results.\nWhat's one healthy habit you're committing to this week? 💬",
        "💚 This is your reminder to take care of yourself today.\nNot tomorrow. Not after the deadline. Today.\nDrop your healthy habit goal below! 👇",
        "🌸 Morning reminder: you cannot show up fully for others if you're running on empty.\nChoose yourself first today.\nWhat does self-care look like for you? Share below! 💬",
    ],
    "money": [
        "💰 Good morning! Let's start the day with the right money mindset.\nFinancial freedom isn't a dream — it's a decision made one day at a time.\nWhat's your #1 financial goal right now? Drop it below! 👇",
        "📈 This hit differently this morning. 💡\nWe work so hard for money — but are we making money work for us?\nShare this with someone who needs a financial wake-up call! 🙏",
        "🌟 Your morning reminder that building wealth is a marathon, not a sprint.\nConsistency beats intensity every single time.\nWhat's one money habit you're building? Comment below! 💬",
    ],
    "mindset": [
        "🔥 Good morning! Let this be the first thing that fuels your day.\nYour mindset is your most powerful asset — protect it.\nWhat's your morning mantra? Share it below! 👇",
        "💫 Saving this for every morning I need a reminder to keep going.\nThe journey is hard but you are harder.\nTag someone who needs to see this today! ❤️",
        "🌅 Rise and shine! Today is another chance to move forward.\nNot perfectly — just forward.\nDrop a 💪 if you're ready to make today count! 👇",
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
