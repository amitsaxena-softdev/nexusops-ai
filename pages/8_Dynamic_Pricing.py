import pandas as pd
import streamlit as st

from agents.pricing_agent import (
    DR_THEISS_PRODUCTS, MAX_DECREASE_PCT, MAX_INCREASE_PCT, PRICE_FLOOR_PCT,
    fetch_live_signals, price_all_products,
)
from shared.theme import apply_theme

st.set_page_config(page_title="Dynamic Pricing — Dr. Theiss", page_icon="💰")
apply_theme()
st.title("💰 Dynamic Pricing Agent")
st.caption("Client: Dr. Theiss Naturwaren GmbH (Homburg) — Signal-driven pricing engine with guardrails")

# ── Session state ──────────────────────────────────────────────────────────────
if "pricing_signals"       not in st.session_state: st.session_state.pricing_signals       = None
if "pricing_results"       not in st.session_state: st.session_state.pricing_results       = None

# ── Live signals panel ─────────────────────────────────────────────────────────
st.markdown("### 📡 Live Market Signals")

col_sig, col_btn = st.columns([5, 1])
with col_btn:
    refresh = st.button("🔄 Refresh", type="secondary")

if refresh or st.session_state.pricing_signals is None:
    with st.spinner("Fetching live signals via Google Search…"):
        try:
            st.session_state.pricing_signals = fetch_live_signals()
            st.session_state.pricing_results = None   # reset results on signal refresh
        except Exception as e:
            st.error(f"Could not fetch signals: {e}")

signals = st.session_state.pricing_signals
if signals:
    icons = {"weather": "🌤️", "sports": "⚽", "seasonal": "📅",
             "supply_chain": "🚢", "market": "📈"}
    c1, c2, c3 = st.columns(3)
    cols = [c1, c2, c3, c1, c2]
    for col, (key, val) in zip(cols, signals.items()):
        col.markdown(f"{icons.get(key, '•')} **{key.replace('_', ' ').title()}**  \n{val}")

# ── Guardrails summary ─────────────────────────────────────────────────────────
st.divider()
st.markdown("### 🛡️ Guardrails")
g1, g2, g3 = st.columns(3)
g1.metric("Max price increase", f"+{MAX_INCREASE_PCT:.0f}%")
g2.metric("Max price decrease", f"−{MAX_DECREASE_PCT:.0f}%")
g3.metric("Price floor",        f"{PRICE_FLOOR_PCT:.0f}% of base")
st.caption("Guardrails are enforced in code — not by the LLM. Any out-of-range recommendation is clamped automatically.")

# ── Product catalogue ──────────────────────────────────────────────────────────
st.divider()
st.markdown("### 🛒 Product Catalogue")
catalog_df = pd.DataFrame([
    {"SKU": p["sku"], "Product": p["name"], "Category": p["category"],
     "Base Price (€)": f"€{p['base_price']:.2f}", "Sensitivity": p["sensitivity"].title()}
    for p in DR_THEISS_PRODUCTS
])
st.dataframe(catalog_df, use_container_width=True, hide_index=True)

# ── Price all products ─────────────────────────────────────────────────────────
st.divider()
if not signals:
    st.info("Signals not loaded yet — click 🔄 Refresh above.")
elif st.button("⚡ Price All Products", type="primary"):
    with st.spinner("Computing price recommendations against live signals…"):
        try:
            st.session_state.pricing_results = price_all_products(signals)
        except Exception as e:
            st.error(f"Pricing error: {e}")

# ── Results table ──────────────────────────────────────────────────────────────
if st.session_state.pricing_results:
    results = st.session_state.pricing_results
    st.markdown("### 📊 Pricing Recommendations")

    rows = []
    for r in results:
        chg     = r.get("change_pct", 0.0)
        arrow   = "↑" if chg > 0.1 else ("↓" if chg < -0.1 else "→")
        guardrail = "⚠️ clamped" if r.get("guardrail_triggered") else "✅ within limits"
        rows.append({
            "SKU":            r.get("sku", ""),
            "Product":        r.get("name", ""),
            "Base (€)":       f"€{r.get('base_price', 0):.2f}",
            "Recommended (€)": f"€{r.get('final_price', 0):.2f}",
            "Change":         f"{arrow} {chg:+.1f}%",
            "Confidence":     r.get("confidence", "—"),
            "Guardrail":      guardrail,
        })

    # Color-coded change column not possible in st.dataframe natively,
    # so we render a styled summary above and the table below.
    up   = [r for r in results if r.get("change_pct", 0) >  0.1]
    down = [r for r in results if r.get("change_pct", 0) < -0.1]
    flat = [r for r in results if abs(r.get("change_pct", 0)) <= 0.1]
    hit  = [r for r in results if r.get("guardrail_triggered")]

    b1, b2, b3, b4 = st.columns(4)
    b1.metric("Price increases ↑", len(up),   delta=f"+{sum(r['change_pct'] for r in up)/len(up):.1f}% avg" if up else None)
    b2.metric("Price decreases ↓", len(down), delta=f"{sum(r['change_pct'] for r in down)/len(down):.1f}% avg" if down else None, delta_color="inverse")
    b3.metric("No change →",       len(flat))
    b4.metric("Guardrail triggered", len(hit), delta="clamped" if hit else None, delta_color="off")

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # Per-product reasoning expanders
    st.markdown("#### Reasoning per product")
    for r in results:
        chg = r.get("change_pct", 0.0)
        icon = "📈" if chg > 0.1 else ("📉" if chg < -0.1 else "➡️")
        with st.expander(f"{icon} {r.get('name', '')} — {chg:+.1f}%"):
            sc1, sc2, sc3 = st.columns(3)
            sc1.metric("Base price",        f"€{r.get('base_price', 0):.2f}")
            sc2.metric("Recommended price", f"€{r.get('final_price', 0):.2f}", delta=f"{chg:+.1f}%")
            sc3.metric("Confidence",        r.get("confidence", "—"))

            sigs = r.get("signals_applied", [])
            if sigs:
                st.markdown("**Signals applied:** " + " · ".join(f"`{s}`" for s in sigs))
            if r.get("guardrail_triggered"):
                st.warning(f"Guardrail triggered — LLM suggested €{r.get('recommended_price', 0):.2f}, clamped to €{r.get('final_price', 0):.2f} (±{MAX_INCREASE_PCT:.0f}%/{MAX_DECREASE_PCT:.0f}% band)")
            st.markdown(f"**Reasoning:** {r.get('reasoning', '—')}")
