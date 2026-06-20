import io
from datetime import timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

from agents.analytics_agent import build_stats_summary, generate_targeting_signals
from shared.theme import apply_theme

st.set_page_config(page_title="Customer Analytics — Dr. Theiss", page_icon="📊")
apply_theme()
st.title("📊 Customer Analytics Agent")
st.caption("Client: Dr. Theiss Naturwaren GmbH (Homburg) — Behavioural patterns, targeting signals, and campaign lift measurement")

SAMPLE_CSV = Path("samples/transactions.csv")
MONTH_NAMES = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
               7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}

# ── Data loader ────────────────────────────────────────────────────────────────
uploaded = st.file_uploader("Upload customer transactions CSV", type=["csv"])
if uploaded:
    df = pd.read_csv(io.BytesIO(uploaded.read()))
elif SAMPLE_CSV.exists():
    df = pd.read_csv(SAMPLE_CSV)
    st.info(f"Using sample dataset — {SAMPLE_CSV.name}  ({len(df):,} transactions, {df['customer_id'].nunique()} customers)")
else:
    st.warning("No CSV found. Upload a file or add samples/transactions.csv.")
    st.stop()

# Ensure date column is parsed
df["date"] = pd.to_datetime(df["date"])

# ── KPI row ───────────────────────────────────────────────────────────────────
st.divider()
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Customers",   f"{df['customer_id'].nunique():,}")
k2.metric("Transactions", f"{len(df):,}")
k3.metric("Total Revenue", f"€{df['revenue'].sum():,.0f}")
k4.metric("Avg Order Value", f"€{df['revenue'].mean():.2f}")
k5.metric("Top Channel", df.groupby("channel")["revenue"].sum().idxmax())

# ── Charts ────────────────────────────────────────────────────────────────────
st.divider()
col_a, col_b = st.columns(2)

with col_a:
    st.markdown("**Monthly Revenue (€)**")
    monthly = (
        df.groupby("month")["revenue"].sum()
        .rename(index=MONTH_NAMES)
        .rename("Revenue (€)")
    )
    st.bar_chart(monthly)

with col_b:
    st.markdown("**Revenue by Segment**")
    seg_rev = (
        df.groupby("segment")["revenue"].sum()
        .sort_values(ascending=False)
        .rename("Revenue (€)")
    )
    st.bar_chart(seg_rev)

col_c, col_d = st.columns(2)

with col_c:
    st.markdown("**Top Products by Revenue**")
    sku_rev = (
        df.groupby("sku_name")["revenue"].sum()
        .sort_values()
        .rename("Revenue (€)")
    )
    st.bar_chart(sku_rev)

with col_d:
    st.markdown("**Sales by Channel**")
    ch_rev = (
        df.groupby("channel")["revenue"].sum()
        .sort_values(ascending=False)
        .rename("Revenue (€)")
    )
    st.bar_chart(ch_rev)

# ── AI targeting signals ───────────────────────────────────────────────────────
st.divider()
st.markdown("### 🎯 AI Targeting Signals")

if "analytics_signals" not in st.session_state:
    st.session_state.analytics_signals = None

if st.button("Generate Targeting Signals", type="primary"):
    with st.spinner("Computing behavioural patterns and generating targeting signals…"):
        try:
            summary = build_stats_summary(df)
            signals = generate_targeting_signals(summary)
            st.session_state.analytics_signals = signals
        except Exception as e:
            st.error(f"Error: {e}")

if st.session_state.analytics_signals:
    signals = st.session_state.analytics_signals

    # Overall insight
    st.info(f"💡 **Key Insight:** {signals.get('overall_insight', '')}")
    st.success(f"🚀 **Top Opportunity:** {signals.get('top_opportunity', '')}")

    # Segment cards
    st.markdown("#### Segment Targeting Cards")
    segs = signals.get("segments", [])
    cols = st.columns(len(segs)) if segs else []
    for col, seg in zip(cols, segs):
        with col:
            st.markdown(f"""
<div style="background:#1e293b; border:1px solid #334155; border-radius:10px; padding:14px;">
  <div style="font-weight:800; font-size:14px; color:#f1f5f9; margin-bottom:8px;">{seg['name']}</div>
  <div style="font-size:11px; color:#94a3b8; margin-bottom:6px;">{seg['profile']}</div>
  <div style="font-size:11px; color:#cbd5e1;">📅 <b>Peak:</b> {seg['peak_season']}</div>
  <div style="font-size:11px; color:#cbd5e1;">🏪 <b>Channel:</b> {seg['top_channel']}</div>
  <div style="font-size:11px; color:#cbd5e1;">⏰ <b>Send:</b> {seg['best_send_window']}</div>
  <div style="font-size:11px; color:#86efac; margin-top:6px; font-style:italic;">"{seg['ad_hook']}"</div>
</div>""", unsafe_allow_html=True)

    # Targeting signals table
    st.markdown("#### Targeting Signals Table")
    table_rows = []
    for seg in segs:
        for sku in seg.get("recommended_skus", []):
            table_rows.append({
                "Segment":      seg["name"],
                "SKU":          sku,
                "Peak Season":  seg["peak_season"],
                "Channel":      seg["top_channel"],
                "Send Window":  seg["best_send_window"],
                "Ad Hook":      seg["ad_hook"],
            })
    if table_rows:
        st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

    # KPIs to measure
    kpis = signals.get("measurement_kpis", [])
    if kpis:
        st.markdown("**Measurement KPIs post-campaign:**  " + " · ".join(f"`{k}`" for k in kpis))

# ── Campaign Lift Measurement ──────────────────────────────────────────────────
st.divider()
st.markdown("### 📈 Campaign Lift Measurement")
st.caption("Simulate a campaign send and measure whether it lifted sales for the targeted product.")

segments  = sorted(df["segment"].unique())
skus      = sorted(df["sku_name"].unique())
all_dates = df["date"].dt.date

lc1, lc2, lc3 = st.columns(3)
with lc1:
    lift_seg   = st.selectbox("Target segment", segments, key="lift_seg")
with lc2:
    seg_skus   = sorted(df[df["segment"] == lift_seg]["sku_name"].unique())
    lift_sku   = st.selectbox("Target SKU", seg_skus, key="lift_sku")
with lc3:
    min_d, max_d = all_dates.min(), all_dates.max()
    mid_d = min_d + (max_d - min_d) // 2
    campaign_date = st.date_input("Campaign launch date", value=mid_d,
                                  min_value=min_d, max_value=max_d, key="lift_date")

window = 30  # days before/after

before_start = pd.Timestamp(campaign_date) - timedelta(days=window)
before_end   = pd.Timestamp(campaign_date)
after_start  = pd.Timestamp(campaign_date)
after_end    = pd.Timestamp(campaign_date) + timedelta(days=window)

mask_seg = df["segment"] == lift_seg
mask_sku = df["sku_name"] == lift_sku

before_rev = df[mask_seg & mask_sku & (df["date"] >= before_start) & (df["date"] < before_end)]["revenue"].sum()
after_rev  = df[mask_seg & mask_sku & (df["date"] >= after_start)  & (df["date"] < after_end) ]["revenue"].sum()

lift_pct = ((after_rev - before_rev) / before_rev * 100) if before_rev > 0 else 0.0

m1, m2, m3 = st.columns(3)
m1.metric("30 days BEFORE campaign", f"€{before_rev:,.2f}")
m2.metric("30 days AFTER campaign",  f"€{after_rev:,.2f}",
          delta=f"{lift_pct:+.1f}%",
          delta_color="normal" if lift_pct >= 0 else "inverse")
m3.metric("Sales Lift", f"{lift_pct:+.1f}%",
          delta="above baseline" if lift_pct > 0 else "below baseline")

# Timeline chart around campaign date
timeline = (
    df[mask_seg & mask_sku]
    .set_index("date")
    .resample("W")["revenue"]
    .sum()
    .rename("Weekly Revenue (€)")
)
if not timeline.empty:
    st.markdown(f"**Weekly revenue — {lift_seg} × {lift_sku}** (campaign launched {campaign_date})")
    st.line_chart(timeline)
    st.caption(f"↑ Campaign launch: {campaign_date}  |  Window: ±{window} days")
