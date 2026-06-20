from shared.llm import ask
import datetime

SYSTEM = """You are a dynamic pricing strategist for Dr. Theiss Naturwaren GmbH (Homburg).
You adjust product prices based on external signals to maximise revenue while staying competitive.

Signals you consider:
- Weather (cold/flu season → health products surge)
- Religious / cultural events (Ramadan, Christmas, Easter → demand shifts)
- Sports fixtures (Bundesliga weekends → convenience products up)
- Supply chain status (shortages → adjust margin)
- Competitor pricing movements
- Day-of-week and time-of-day demand curves

Your output structure:
---
PRODUCT: <name>
CURRENT PRICE: <€X.XX>
SIGNALS DETECTED:
  - <signal 1>: <impact description>
  - <signal 2>: <impact description>
RECOMMENDED PRICE: <€X.XX>
CHANGE: <+/-X% or "No change">
CONFIDENCE: Low / Medium / High
REASONING: <paragraph>
GUARDRAILS: <any ethical/legal pricing limits to note>
REVIEW DATE: <when to re-evaluate>
---"""

MOCK_SIGNALS = {
    "weather": "Cold snap forecast across Germany this week (2–5°C). Flu season starting.",
    "holidays": "Advent season — Christmas markets open. High consumer spending period.",
    "sports": "Bundesliga matchday 15 this weekend. FC Saarbrücken home game Saturday.",
    "supply_chain": "Vitamin C raw material slightly constrained globally (+8% wholesale cost).",
    "competitor": "Two major competitors raised OTC health product prices by 4–6% this week.",
    "day_pattern": "Weekday evenings and Sunday mornings show peak pharmacy/online purchases.",
}


def get_pricing_recommendation(product: str, current_price: float, category: str) -> str:
    signals_text = "\n".join([f"- {k.title()}: {v}" for k, v in MOCK_SIGNALS.items()])
    today = datetime.date.today().strftime("%A, %d %B %Y")
    prompt = (
        f"Today is {today}.\n\n"
        f"Product: {product}\n"
        f"Current price: €{current_price:.2f}\n"
        f"Category: {category}\n\n"
        f"Current external signals:\n{signals_text}\n\n"
        "Provide a pricing recommendation with full reasoning."
    )
    return ask(prompt, system_instruction=SYSTEM)
