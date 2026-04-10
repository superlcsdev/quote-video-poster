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

BIBLICAL_CAPTION_PROMPT = """Write a Facebook post caption for a morning Bible verse video.
The audience is Filipino professionals — nurses, engineers, IT workers — in Singapore and Philippines.
Many are OFWs (overseas workers) far from home, facing career pressure, financial concerns, and homesickness.

Bible verse shown in the video: "{quote}"

YOUR JOB: Write a caption that helps your audience understand what this verse MEANS for their real life.
Model your caption on this example (for Jer 29:11):

"Trust the process, even when you are far from home.
For many OFWs, life can feel uncertain — new country, sacrifices, homesickness, and pressure to provide. But this verse reminds us that God's plans are not random. Even when things feel delayed or difficult, there is a bigger purpose being worked out.
Being away from family is not wasted time. It can be part of a journey toward growth, stability, and a better future — not just financially, but spiritually and emotionally too."

STRUCTURE — follow this exactly:
Line 1: A short, punchy headline sentence that captures the theme of the verse. (Max 12 words. No emoji.)
Line 2: Empty line.
Lines 3–5: 2–3 sentences connecting the verse to the real lives of Filipino professionals in SG/PH.
  Be specific — mention their challenges (long shifts, being far from family, financial pressure, uncertainty).
  Explain what the verse means in plain language — not just "God is good" but HOW this verse applies.
Line 6: Empty line.
Line 7: 1–2 sentences of encouragement. End with a reflection question or short CTA.

RULES:
- 120–180 words total
- Simple everyday English. No big words.
- Warm and genuine — not preachy or religious-sounding
- No hashtags in the caption body
- Do NOT repeat the verse word for word
- End with: "Drop a 🙏 if this spoke to you today. 👇" or similar

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
        """God's direction is always available — even when the path isn't clear.

Many of us were taught to figure things out on our own. Especially as professionals trained to solve problems, we default to logic, planning, and pushing harder. But Proverbs 3:5-6 calls us to something different — to trust God's direction above our own understanding.

This doesn't mean stop planning. It means hold your plans with open hands. Whatever decision you're facing today — a career move, a financial choice, a relationship challenge — bring it to Him first.

He has directed people in far more uncertain situations than yours. He'll direct you too.

Drop a 🙏 if you needed this reminder today. 👇""",

        """You are more capable than you feel right now — because it's not about your own strength.

If you've been feeling like your situation is too hard, your goals too big, or the distance from home too heavy — Philippians 4:13 is a direct answer to that. It's not motivational language. It's a statement of fact about where your strength actually comes from.

Being a Filipino professional abroad — navigating a demanding career, supporting family, building a future — takes more than most people realise. You don't have to carry it alone.

The strength you need for today has already been made available to you.

Drop a 💪 if this is your anchor today. 👇""",

        """Fear is not from God. So where is it coming from?

Many professionals carry quiet fears — fear of failing, fear of not being enough, fear of the future being uncertain. But 2 Timothy 1:7 is a reminder that those fears are not part of what God placed in you. What He placed in you is power, love, and a sound mind.

If you're facing something that feels bigger than you today — a difficult shift, a financial decision, an uncertain season — walk into it knowing that you were not designed to be afraid.

You were designed for more than that.

Share this with someone who needs to hear it today 🙏""",

        """Whatever you do today — do it for something bigger than a paycheck.

Colossians 3:23 was written to ordinary workers. People doing hard, repetitive work. And the instruction was clear: do it wholeheartedly, as if working for the Lord, not just for your boss or your salary.

That's a different kind of work ethic. It means showing up fully on the hard days. It means doing your job with integrity even when no one is watching. It means your daily work — nursing, engineering, coding — has spiritual weight.

Your work today matters more than you think.

Drop a 🙏 if this shifts how you see your work today. 👇""",

        """You are not going through this alone — wherever you are in the world.

Joshua 1:9 was spoken to someone who had just been given an overwhelming task in an unfamiliar territory. Sound familiar? For many Filipino professionals in Singapore — new country, new pressure, far from home — the feeling of facing the unknown is real.

But God's promise wasn't "the path will be easy." It was "I am with you wherever you go." That's not a feeling. That's a fact.

Be strong today — not because the situation is easy, but because you are not facing it alone.

Drop a ❤️ if this is your reminder for today. 👇""",

        """God is not limited by what you can imagine for yourself.

Ephesians 3:20 says He is able to do "exceedingly abundantly above all that we ask or think." That means your biggest goal — the career you want, the financial freedom you're building, the family life you're working toward — is not too much for Him.

Many OFWs and Filipino professionals shrink their dreams because of what they've seen or where they started. But God's plans are not limited by your starting point.

Don't cap what He can do by the size of what you're currently asking for.

Drop a 🌟 if this speaks to you. 👇""",
    ],
}


def generate_caption(quote: str, theme: str) -> str:
    if GEMINI_API_KEY:
        try:
            # Biblical theme gets its own dedicated prompt
            if theme == "biblical":
                prompt = BIBLICAL_CAPTION_PROMPT.format(quote=quote)
            else:
                prompt = CAPTION_PROMPT.format(quote=quote, theme=theme)

            resp = requests.post(
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
    now  = datetime.now()
    seed = f"{now.strftime('%Y-%m-%d')}{theme}cap{now.timetuple().tm_yday}"
    idx  = int(hashlib.md5(seed.encode()).hexdigest(), 16) % len(captions)
    return captions[idx]
