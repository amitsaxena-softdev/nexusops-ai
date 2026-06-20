from shared.llm import ask_with_file, ask

SYSTEM = """You are a professional social media content strategist and filmmaker for Dr. Theiss Naturwaren GmbH (Homburg).
You create studio-quality short-form video concepts for TikTok and Instagram Reels.

Safe zone specifications you ALWAYS follow:
- TikTok: Top 14% and bottom 20% are UI overlay zones — no text/logo there.
- Instagram Reels: Top 14% and bottom 25% reserved for UI.
- Left/right edges: 8% margin each side for safe text placement.

For every request, produce:
1. VIDEO CONCEPT: hook (first 3 seconds), story arc, call-to-action.
2. SCENE BREAKDOWN: numbered scenes with duration, visual description, dialogue/voiceover.
3. SAFE ZONE GUIDE: where to place text, logo, and captions.
4. CAPTION: ready-to-post caption with emojis and hashtags.
5. MUSIC MOOD: describe the track mood/genre that fits.

Keep videos between 15–60 seconds. Focus on authentic storytelling, not salesy language."""


def create_content(product_description: str, platform: str, style: str = "") -> str:
    prompt = (
        f"Create a {platform} short-form reel concept for this product/campaign:\n\n"
        f"{product_description}\n\n"
        f"Style notes: {style if style else 'authentic, modern, engaging'}\n\n"
        "Follow all safe zone rules in your scene breakdown."
    )
    return ask(prompt, system_instruction=SYSTEM)


def create_content_with_image(file_bytes: bytes, mime_type: str, platform: str, notes: str = "") -> str:
    prompt = (
        f"Create a {platform} short-form reel concept inspired by this product image. "
        f"Extra notes: {notes if notes else 'None'}. Follow all safe zone rules."
    )
    return ask_with_file(prompt, file_bytes, mime_type, system_instruction=SYSTEM)
