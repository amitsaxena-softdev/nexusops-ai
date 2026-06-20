import json, re
from shared.llm import ask, ask_with_file

DR_THEISS_CATALOG = {
    "Allgäuer Latschenkiefer Mobil Gel": {
        "line": "Muscles & Joints",
        "price": "€7.99",
        "target": "Active adults 30–55, office workers, athletes",
        "peak_season": "Winter, post-summer sport season",
        "hero_ingredient": "Allgäu mountain-pine oil + menthol",
        "usp": "Natural cooling-warming action from a 50-year Allgäu tradition",
        "angles": "post-workout recovery ritual · office desk stretch routine · winter sports warm-down",
    },
    "Eisspray akut": {
        "line": "Muscles & Joints",
        "price": "€8.49",
        "target": "Athletes, coaches, physios, 20–45",
        "peak_season": "Year-round; peak summer/autumn sport season",
        "hero_ingredient": "Instant cold spray (−20 °C)",
        "usp": "Instant cold in seconds — the spray physios use pitch-side",
        "angles": "sports injury instant relief · pitch-side recovery drama · gym-bag essentials reel",
    },
    "5in1 Beinlotion": {
        "line": "Legs & Veins",
        "price": "€9.99",
        "target": "Women 30–55, nurses, retail workers, frequent flyers",
        "peak_season": "Summer (heavy legs), spring",
        "hero_ingredient": "Horse chestnut, red vine leaf, menthol",
        "usp": "5 benefits in 1 — cooling, toning, refreshing, moisturising, light legs",
        "angles": "end-of-day heavy-leg relief ASMR · summer legs routine · shift-worker relatable hook",
    },
    "Allgäuer Latschenkiefer Fußbad": {
        "line": "Foot Care",
        "price": "€4.99",
        "target": "Adults 35+, standing-job workers",
        "peak_season": "Winter (cosy ritual), autumn",
        "hero_ingredient": "Allgäu mountain-pine oil, sea salt",
        "usp": "Soothes tired feet in 10 minutes — natural mountain-pine tradition since 1973",
        "angles": "evening self-care ritual ASMR · nurse/retail treat-yourself hook · cosy winter night-in",
    },
    "Hornhaut Entferner Maske": {
        "line": "Foot Care",
        "price": "€5.49",
        "target": "Women 25–45, beauty-conscious",
        "peak_season": "Spring (sandal-season prep), summer",
        "hero_ingredient": "Urea, salicylic acid",
        "usp": "Removes hard skin in 5 minutes — no pumice needed",
        "angles": "sandal-season transformation before/after · 5-min foot mask routine · beauty hack reveal",
    },
    "Custom product / campaign": {
        "line": "", "price": "", "target": "", "peak_season": "",
        "hero_ingredient": "", "usp": "", "angles": "",
    },
}

SYSTEM = """You are a professional social media filmmaker for Dr. Theiss Naturwaren GmbH (Homburg).
Write a concise, structured video production brief that a creator can paste directly into
an AI video tool (Sora, Runway, Kling, Pika) to generate the reel.

SAFE ZONE RULES to reference in every text overlay:
- TikTok: top 14% and bottom 20% are UI danger zones — no text or logo.
- Instagram Reels: top 14% and bottom 25% are UI danger zones — no text or logo.
- Left/right: 8% margin each side. All text within the inner 84% width.

Output this exact structure — plain text, no markdown headers, no code fences:

CONCEPT: [short creative title]
PLATFORM: [platform] | DURATION: [Xs]
MUSIC: [one sentence: mood, tempo, genre]

SCENE 1 — [Label] (0–Xs)
Visual: [precise camera direction and shot description]
Voiceover: [exact words spoken, or: no voiceover — music only]
Text overlay: [on-screen text — or: none] | Placement: [safe zone position]

SCENE 2 — [Label] (Xs–Ys)
...repeat for each scene...

CAPTION:
[ready-to-post caption with emojis and hashtags, max 150 chars]

SAFE ZONE REMINDER:
[one-line reminder relevant to the chosen platform]

Rules: 4–6 scenes, 15–45 seconds total. Labels: Hook · Build · Key Message · CTA.
Authentic storytelling — product integrates naturally, never salesy.
Be specific with camera direction so a video AI can act on it directly."""


def create_content(product_key: str, platform: str, style: str = "",
                   custom_desc: str = "", image_bytes: bytes = None, image_mime: str = None) -> str:
    info = DR_THEISS_CATALOG.get(product_key, {})
    if product_key == "Custom product / campaign":
        product_block = f"Product / campaign:\n{custom_desc}"
    else:
        product_block = (
            f"Product: {product_key}\n"
            f"Line: {info['line']} | Price: {info['price']}\n"
            f"Target audience: {info['target']}\n"
            f"Peak season: {info['peak_season']}\n"
            f"Hero ingredient: {info['hero_ingredient']}\n"
            f"USP: {info['usp']}\n"
            f"Suggested content angles: {info['angles']}"
        )

    prompt = (
        f"Write a video production brief for a {platform} reel.\n\n"
        f"{product_block}\n\n"
        f"Style: {style or 'authentic, modern, engaging'}"
    )

    if image_bytes and image_mime:
        return ask_with_file(prompt, image_bytes, image_mime, system_instruction=SYSTEM)
    return ask(prompt, system_instruction=SYSTEM)
