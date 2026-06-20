from shared.llm import ask

SYSTEM = """You are a customer analytics and targeting specialist for Dr. Theiss Naturwaren GmbH (Homburg).
You analyse customer data to detect behavioural patterns and generate actionable advertising signals.

When given customer data (CSV summary or raw data):
1. SEGMENTATION: identify 3–5 distinct customer segments with names, size estimate, key traits.
2. BEHAVIOURAL PATTERNS: purchase frequency, seasonal spikes, category affinities.
3. TARGETING SIGNALS: for each segment, the optimal ad channel, day of week, and time of day.
4. PRODUCT RECOMMENDATIONS: which products to push to which segment.
5. MEASUREMENT PLAN: what KPIs to track post-campaign to confirm sales lift.

Be specific and data-driven. If data is limited, state assumptions clearly."""


def analyse_data(data_summary: str) -> str:
    prompt = f"Analyse this customer data and generate targeting signals:\n\n{data_summary}"
    return ask(prompt, system_instruction=SYSTEM)


def analyse_csv_text(csv_content: str) -> str:
    prompt = (
        "Here is customer transaction data in CSV format. Analyse it for behavioural patterns "
        "and generate advertising targeting signals:\n\n" + csv_content[:8000]
    )
    return ask(prompt, system_instruction=SYSTEM)
