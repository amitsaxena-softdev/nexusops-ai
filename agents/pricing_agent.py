import json, re, datetime
from shared.llm import ask, ask_with_search

# ── Product catalogue (from Dr. Theiss data pack §3) ──────────────────────────
DR_THEISS_PRODUCTS = [
    {"sku": "EIS001", "name": "Eisspray akut",                         "base_price": 8.49, "category": "Muscles & Joints", "sensitivity": "high"},
    {"sku": "MOB001", "name": "Allgäuer Latschenkiefer Mobil Gel",      "base_price": 7.99, "category": "Muscles & Joints", "sensitivity": "medium"},
    {"sku": "BEI001", "name": "5in1 Beinlotion",                       "base_price": 9.99, "category": "Legs & Veins",     "sensitivity": "high"},
    {"sku": "FUS001", "name": "Allgäuer Latschenkiefer Fußbad",        "base_price": 4.99, "category": "Foot Care",        "sensitivity": "medium"},
    {"sku": "HOR001", "name": "Hornhaut Entferner Maske",               "base_price": 5.49, "category": "Foot Care",        "sensitivity": "high"},
    {"sku": "HUS001", "name": "Allgäuer Latschenkiefer Hustenbonbons",  "base_price": 3.49, "category": "Cough & Cold",     "sensitivity": "high"},
]

# ── Guardrails (enforced in Python, not by LLM) ────────────────────────────────
MAX_INCREASE_PCT = 15.0   # never raise more than 15 %
MAX_DECREASE_PCT = 10.0   # never drop more than 10 %
PRICE_FLOOR_PCT  = 90.0   # minimum 90 % of base price


def _apply_guardrails(base: float, recommended: float) -> tuple[float, bool]:
    floor   = base * PRICE_FLOOR_PCT  / 100
    ceiling = base * (100 + MAX_INCREASE_PCT) / 100
    clamped = max(floor, min(ceiling, recommended))
    triggered = abs(clamped - recommended) > 0.005
    return round(clamped, 2), triggered


# ── Live signal fetch ──────────────────────────────────────────────────────────
SIGNALS_SYSTEM = (
    "You are a market-signal aggregator. Return ONLY a valid JSON object — no markdown, no prose.\n"
    '{\n'
    '  "weather": "one sentence: current German weather and health relevance",\n'
    '  "sports": "one sentence: upcoming Bundesliga or major sport fixtures this weekend",\n'
    '  "seasonal": "one sentence: current season, religious or public holidays this week",\n'
    '  "supply_chain": "one sentence: any pharmacy or health-product supply news",\n'
    '  "market": "one sentence: consumer or pharmacy market context"\n'
    '}'
)


def fetch_live_signals() -> dict:
    today = datetime.date.today().strftime("%A, %d %B %Y")
    prompt = (
        f"Today is {today}. Use Google Search to find:\n"
        "1. Current weather forecast for Germany (especially Bayern and Saarland)\n"
        "2. Bundesliga fixtures or major sport events this weekend\n"
        "3. German public holidays or religious events this week or coming days\n"
        "4. Any recent news about pharmacy or health-product supply-chain disruptions in Europe\n"
        "5. General pharmacy retail market context in Germany right now\n\n"
        "Summarise each in one sentence and return as JSON."
    )
    raw = ask_with_search(prompt, system_instruction=SIGNALS_SYSTEM)
    m = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', raw)
    if m:
        raw = m.group(1)
    return json.loads(raw.strip())


# ── Pricing engine ─────────────────────────────────────────────────────────────
PRICING_SYSTEM = """You are a dynamic pricing strategist for Dr. Theiss Naturwaren GmbH (Homburg).
Given real-time external signals, recommend a new price for each product in a catalogue.

Rules:
- Consider how each signal boosts or reduces demand for that specific product category.
- Raise prices when demand signals are strong and competitors have moved up.
- Lower prices (or hold) when demand is weak or season is off-peak.
- Factor in the product's seasonal sensitivity: high = react strongly to signals.

Return ONLY a valid JSON array — no markdown, no code fences:

[
  {
    "sku": "EIS001",
    "name": "Eisspray akut",
    "base_price": 8.49,
    "recommended_price": 8.99,
    "signals_applied": ["cold weather", "football fixtures"],
    "confidence": "High",
    "reasoning": "One clear sentence explaining the change"
  }
]

Include every product in the input. Be precise about recommended_price (2 decimal places).
Confidence: Low / Medium / High."""


def price_all_products(signals: dict) -> list[dict]:
    today    = datetime.date.today().strftime("%A, %d %B %Y")
    sig_text = "\n".join(f"- {k.title()}: {v}" for k, v in signals.items())
    products_text = "\n".join(
        f"- SKU {p['sku']}: {p['name']}, base price €{p['base_price']:.2f}, "
        f"category: {p['category']}, seasonal sensitivity: {p['sensitivity']}"
        for p in DR_THEISS_PRODUCTS
    )

    prompt = (
        f"Today: {today}\n\n"
        f"Live signals:\n{sig_text}\n\n"
        f"Product catalogue:\n{products_text}\n\n"
        "Recommend a new price for every product based on the signals."
    )

    raw = ask(prompt, system_instruction=PRICING_SYSTEM)
    m = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', raw)
    if m:
        raw = m.group(1)
    recommendations = json.loads(raw.strip())

    # Enforce guardrails in Python
    for rec in recommendations:
        base        = rec.get("base_price", rec.get("recommended_price", 0))
        rec_price   = rec.get("recommended_price", base)
        final, hit  = _apply_guardrails(base, rec_price)
        rec["final_price"]         = final
        rec["guardrail_triggered"] = hit
        rec["change_pct"]          = round((final - base) / base * 100, 1) if base else 0.0
        rec["max_increase_pct"]    = MAX_INCREASE_PCT
        rec["max_decrease_pct"]    = MAX_DECREASE_PCT

    return recommendations
