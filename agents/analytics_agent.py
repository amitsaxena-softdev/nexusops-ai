import json, re
from shared.llm import ask

SYSTEM = """You are a customer analytics specialist for Dr. Theiss Naturwaren GmbH (Homburg).
You receive computed statistics from real transaction data and generate concrete advertising targeting signals.

Return ONLY a valid JSON object — no markdown, no code fences:

{
  "segments": [
    {
      "name": "Segment name",
      "profile": "One sentence describing who these customers are",
      "peak_season": "e.g. Mar–Jun",
      "top_channel": "e.g. pharmacy",
      "best_send_window": "e.g. Thu–Fri, 17:00–19:00",
      "recommended_skus": ["SKU name 1", "SKU name 2"],
      "ad_hook": "One-line creative angle for this segment"
    }
  ],
  "overall_insight": "2–3 sentences summarising the most important pattern in the data",
  "top_opportunity": "Single highest-revenue opportunity — specific segment × SKU × timing",
  "measurement_kpis": ["KPI 1", "KPI 2", "KPI 3", "KPI 4"]
}

Be concrete and data-driven. Reference actual numbers from the statistics provided.
For best_send_window, infer from segment profile: athletes → weekday evenings 18–20:00; self-care → weekend mornings 10–12:00; winter/wellness → Sunday evenings 19–21:00; budget → lunchtime 12–13:00."""


def generate_targeting_signals(stats_summary: str) -> dict:
    raw = ask(f"Customer transaction statistics:\n\n{stats_summary}", system_instruction=SYSTEM)
    m = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', raw)
    if m:
        raw = m.group(1)
    return json.loads(raw.strip())


def build_stats_summary(df) -> str:
    total_customers = df["customer_id"].nunique()
    total_revenue   = df["revenue"].sum()
    date_range      = f"{df['date'].min()} to {df['date'].max()}"

    monthly     = df.groupby("month")["revenue"].sum().round(0)
    top_months  = monthly.nlargest(3).index.tolist()

    seg_stats = df.groupby("segment").agg(
        customers=("customer_id", "nunique"),
        orders=("customer_id", "count"),
        revenue=("revenue", "sum"),
        avg_order=("revenue", "mean"),
    ).round(2)

    sku_stats = df.groupby("sku_name").agg(
        orders=("qty", "sum"),
        revenue=("revenue", "sum"),
    ).sort_values("revenue", ascending=False).round(2)

    channel_stats = df.groupby("channel")["revenue"].sum().sort_values(ascending=False).round(0)

    seg_sku = df.groupby(["segment", "sku_name"])["revenue"].sum().round(0).reset_index()
    top_per_seg = (
        seg_sku.sort_values(["segment", "revenue"], ascending=[True, False])
        .groupby("segment").head(2)
        .to_string(index=False)
    )

    monthly_sku = df.groupby(["sku_name", "month"])["revenue"].sum().round(0).unstack(fill_value=0)

    return f"""
DATE RANGE: {date_range}
TOTAL CUSTOMERS: {total_customers}
TOTAL REVENUE: €{total_revenue:,.2f}
TOP REVENUE MONTHS: {top_months}

MONTHLY REVENUE (month → €revenue):
{monthly.to_string()}

SEGMENT BREAKDOWN:
{seg_stats.to_string()}

TOP SKUs OVERALL:
{sku_stats.to_string()}

TOP 2 SKUs PER SEGMENT:
{top_per_seg}

CHANNEL REVENUE:
{channel_stats.to_string()}

MONTHLY REVENUE BY SKU:
{monthly_sku.to_string()}
""".strip()
