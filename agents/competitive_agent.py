import json, re
from shared.llm import ask, ask_with_file, ask_with_search

# ── Default sample (Dr. Theiss) — used as pre-fill only ───────────────────────
DR_THEISS_PRODUCTS = [
    {"name": "Hornhaut Entferner Maske",              "category": "Foot Care — Callus",  "price": 5.49},
    {"name": "Allgäuer Latschenkiefer Fußbad",        "category": "Foot Care — Bath",    "price": 4.99},
    {"name": "5in1 Beinlotion",                       "category": "Legs & Veins",        "price": 9.99},
    {"name": "Allgäuer Latschenkiefer Mobil Gel",     "category": "Muscles & Joints",    "price": 7.99},
    {"name": "Eisspray akut",                         "category": "Sports Recovery",     "price": 8.49},
    {"name": "Allgäuer Latschenkiefer Hustenbonbons", "category": "Cough & Cold",        "price": 3.49},
]

# ── Extract product list from uploaded PDF / document ─────────────────────────
EXTRACT_SYSTEM = (
    "You are a product catalogue parser. Extract every product from the document. "
    "Return ONLY a valid JSON array — no markdown, no code fences:\n"
    '[{"name": "Product name", "category": "Category", "price": 0.00}]\n'
    "If price is not listed, use 0.00. Category should be a short phrase (e.g. Foot Care, Muscles & Joints)."
)


def extract_products_from_file(file_bytes: bytes, mime_type: str) -> list[dict]:
    raw = ask_with_file(
        "Extract all products from this document into a JSON array.",
        file_bytes, mime_type,
        system_instruction=EXTRACT_SYSTEM,
    )
    m = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', raw)
    if m:
        raw = m.group(1)
    return json.loads(raw.strip())

# ── Competitors from Dr. Theiss data pack ─────────────────────────────────────
COMPETITORS = ["Gehwol", "Scholl", "Allpresan", "Kneipp", "tetesept",
               "Hansaplast", "Doppelherz", "Voltaren", "Pernaton", "Retterspitz"]

# ── White-space hypotheses seeded from data pack ──────────────────────────────
WHITE_SPACE_SEEDS = [
    "Men-targeted muscle recovery — no natural brand owns this segment",
    "Cooling sports sprays for gym/amateur athletes — Eisspray has no direct natural competitor",
    "Subscription refill packs — no player in pharmacy natural segment offers this",
    "Sustainability/eco positioning — none of the major competitors lead on this",
    "Diabetic-foot sub-brand — underserved clinical niche in foot care",
    "QR/app guidance on packaging — zero natural brands do this",
]

# ── Live competitor research ───────────────────────────────────────────────────
SEARCH_SYSTEM = (
    "You are a competitive intelligence researcher. Return ONLY a valid JSON object — "
    "no markdown, no code fences:\n"
    '{"findings": "3-4 sentences summarising competitor products, pricing, and gaps in this category",'
    '"top_competitors": ["Competitor A", "Competitor B"],'
    '"price_range": "e.g. €3–€15",'
    '"dominant_format": "e.g. cream, gel, spray",'
    '"underserved_segments": "one sentence on who nobody is targeting well"}'
)


def fetch_category_intel(category: str, competitors: list[str] = None) -> dict:
    comp_list = competitors or COMPETITORS
    prompt = (
        f"Search Google for competitor products in the '{category}' segment "
        f"of the European consumer health and pharmacy market (focus: Germany, Austria, Switzerland).\n"
        f"Known competitors to check: {', '.join(comp_list[:8])}.\n"
        f"Find: current product offerings, price points, target demographics, and gaps."
    )
    raw = ask_with_search(prompt, system_instruction=SEARCH_SYSTEM)
    m = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', raw)
    if m:
        raw = m.group(1)
    try:
        return json.loads(raw.strip())
    except Exception:
        return {"findings": raw.strip(), "top_competitors": [],
                "price_range": "N/A", "dominant_format": "N/A",
                "underserved_segments": "N/A"}


# ── Gap matrix analysis ────────────────────────────────────────────────────────
GAP_SYSTEM = """You are a competitive product-gap analyst for Dr. Theiss Naturwaren GmbH (Homburg).
Given live competitor intelligence and the Dr. Theiss product portfolio, produce a structured gap analysis.

Return ONLY a valid JSON object — no markdown, no code fences:

{
  "market_summary": "2-3 sentences on the overall competitive landscape",
  "gap_matrix": [
    {
      "need": "Specific consumer need (e.g. Callus removal for men)",
      "dr_theiss_coverage": "Strong / Partial / Absent",
      "competitor_coverage": "Strong / Partial / Absent",
      "gap_size": "Large / Medium / Small",
      "white_space": "One sentence describing the gap and who it affects"
    }
  ],
  "opportunities": [
    {
      "title": "Short opportunity name",
      "need": "Consumer need it addresses",
      "target": "Target demographic",
      "format": "Product format (e.g. cooling spray, subscription kit)",
      "rationale": "Why Dr. Theiss is well-placed to win here",
      "priority": "High / Medium / Low",
      "market_size": "Large / Medium / Small"
    }
  ]
}

Produce 6–8 gap_matrix rows and 3–4 opportunities ranked by priority. Be specific."""


def analyse_portfolio(live_intel: dict, products: list[dict]) -> dict:
    products_text = "\n".join(
        f"- {p['name']} ({p['category']}, €{float(p.get('price', 0)):.2f})"
        for p in products
    )
    intel_text = "\n\n".join(
        f"Category: {cat}\n"
        f"Findings: {d.get('findings', '')}\n"
        f"Top competitors here: {', '.join(d.get('top_competitors', []))}\n"
        f"Market price range: {d.get('price_range', 'N/A')}\n"
        f"Underserved segments: {d.get('underserved_segments', 'N/A')}"
        for cat, d in live_intel.items()
    )
    seeds = "\n".join(f"- {s}" for s in WHITE_SPACE_SEEDS)

    prompt = (
        f"Dr. Theiss portfolio:\n{products_text}\n\n"
        f"Live competitor intelligence per category:\n{intel_text}\n\n"
        f"Known white-space hypotheses from internal data:\n{seeds}\n\n"
        "Produce the competitive gap matrix and ranked product opportunities."
    )
    raw = ask(prompt, system_instruction=GAP_SYSTEM)
    m = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', raw)
    if m:
        raw = m.group(1)
    return json.loads(raw.strip())


# ── Stateless follow-up ────────────────────────────────────────────────────────
CHAT_SYSTEM = """You are a sharp competitive intelligence analyst for Dr. Theiss Naturwaren GmbH.
Answer questions about competitor products, market gaps, and opportunities.
Be concise: 2-4 sentences. Reference specific competitors or product names where possible."""


def send_followup(conversation: list, message: str) -> str:
    prior = "\n\n".join(
        f"{'User' if m['role'] == 'user' else 'Analyst'}: {m['content']}"
        for m in conversation
    ) if conversation else "(none)"
    return ask(
        f"Prior conversation:\n{prior}\n\nUser question: {message}",
        system_instruction=CHAT_SYSTEM,
    )
