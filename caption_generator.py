"""
caption_generator.py
Generates the Facebook post caption to accompany the quote video.
6 themes: ofw, health, money, mindset, success, biblical
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

BANNED (automatic reject if you use any of these):
"one win you're proud of", "what's one win", "you're building something great",
"it's tough sometimes", "every effort", "you've got this", "keep pushing",
"what's your morning", "share your thoughts", "what resonates with you"

WHAT WORKS INSTEAD:
- React to the quote with a sharp observation, not cheerleading
- Ask a question that relates to their SPECIFIC professional life
  e.g. "Are you actually investing what you earn, or just earning more?" (money)
  e.g. "When did you last take a full day off without guilt?" (health)
  e.g. "What's one thing you've been putting off that would change everything?" (success)
- Or share a brief honest thought that connects the quote to real life

RULES:
- 2–3 short sentences max. Each under 15 words.
- Sound like a real person — not a motivational coach
- Contractions always. Simple words.
- Start with an emoji. End with a CTA.
- Don't repeat the quote word for word.

Write ONLY the caption. No preamble."""

FALLBACK_CAPTIONS = {
    "ofw": [
        "🌏 Good morning.\nYou're earning in one of the world's strongest currencies. Are you building with it or just spending it?\nDrop a 💬 below — what are you building right now?",
        "💫 This one's for anyone working abroad and wondering if it's all worth it.\nIt is — but only if you make it worth it intentionally.\nWhat's your plan for when you go home? 👇",
        "☀️ You didn't cross an ocean just to send money home and repeat.\nAt some point the sacrifice has to build something permanent.\nWhat does that look like for you? Comment below 💬",
    ],
    "health": [
        "🌿 Honest question — when did you last have a full health check?\nNot when you were sick. An actual check-up.\nDrop your answer below, no judgment 👇",
        "💚 You push through 12-hour shifts. You cover for colleagues. You keep going.\nBut who's making sure you're okay?\nTake 5 minutes for yourself today. That's it. 🌱",
        "🌸 The professionals who last longest in demanding careers aren't the toughest.\nThey're the ones who figured out how to recover properly.\nHow do you recharge? Share below 👇",
    ],
    "money": [
        "💰 Here's an uncomfortable question — do you actually know your savings rate?\nNot roughly. Exactly.\nIf not, that's the first thing to fix this week 👇",
        "📈 Most people earning good salaries still feel financially behind after 5 years.\nIt's not a salary problem. It's a system problem.\nAre you building a system? Comment below 💬",
        "🌟 Your next pay day is coming.\nThe question isn't how much — it's what percentage you're keeping.\nDrop your savings rate target below. Let's talk 👇",
    ],
    "mindset": [
        "🔥 Good morning.\nThe version of you from 3 years ago would be impressed by where you are.\nDon't forget that — and don't stop now 💪",
        "💫 Most people are waiting to feel motivated before they start.\nBut motivation follows action — not the other way around.\nWhat's one thing you'll do today without waiting to feel ready? 👇",
        "🌅 Discipline is just doing what needs doing, whether you feel like it or not.\nThat's not complicated. It's just hard.\nWhat are you choosing to show up for today? 💬",
    ],
    "success": [
        "🏆 Good morning.\nThe people who achieve what you want are not luckier or more talented.\nThey just stopped waiting and started. When are you starting? 👇",
        "🔥 Success leaves clues — and the biggest one is this:\nMost people who made it did it while still afraid.\nWhat's the fear that's been keeping you from your next move? 💬",
        "⚡ You know what you need to do.\nYou probably even know how.\nThe only question left is when. Drop your answer below 👇",
    ],
    "biblical": [
        "🙏 Good morning.\nHis mercies are new every single morning — including today, whatever yesterday looked like.\nDrop a ❤️ if you needed that reminder 👇",
        "✨ You are not carrying today alone.\nThat changes the weight of everything you're facing right now.\nShare this with someone who needs to hear it 🙏",
        "🌅 Whatever you're stepping into today — He's already been there.\nThat's not a small thing. Walk into your day knowing that.\nDrop a 🙏 if this is your anchor today 👇",
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
    # Rotate by date + week number for more variety
    now  = datetime.now()
    seed = f"{now.strftime('%Y-%m-%d')}{theme}cap{now.isocalendar()[1]}"
    idx  = int(hashlib.md5(seed.encode()).hexdigest(), 16) % len(captions)
    return captions[idx]
