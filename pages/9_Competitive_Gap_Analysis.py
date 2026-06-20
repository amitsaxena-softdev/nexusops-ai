import pandas as pd
import streamlit as st

from agents.competitive_agent import (
    DR_THEISS_PRODUCTS, COMPETITORS, WHITE_SPACE_SEEDS,
    extract_products_from_file, fetch_category_intel,
    analyse_portfolio, send_followup,
)

st.set_page_config(page_title="Competitive Gap Analysis", page_icon="🔭")
st.title("🔭 Competitive Gap Analysis Agent")
st.caption("Upload a product catalog, benchmark it against competitors, and surface white-space gaps.")

# ── Session state ──────────────────────────────────────────────────────────────
for k, v in [("comp_products", []), ("comp_intel", None),
             ("comp_results", None), ("comp_followups", [])]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Step 1: Product input ──────────────────────────────────────────────────────
st.markdown("### Step 1 — Enter your product set")

input_mode = st.radio(
    "How do you want to provide products?",
    ["Upload catalog (PDF / CSV)", "Enter manually", "Use Dr. Theiss sample"],
    horizontal=True,
)

if input_mode == "Upload catalog (PDF / CSV)":
    uploaded = st.file_uploader("Upload product catalog", type=["pdf", "csv", "txt"])
    if uploaded:
        if uploaded.name.endswith(".csv"):
            try:
                df_up = pd.read_csv(uploaded)
                df_up.columns = [c.strip().lower() for c in df_up.columns]
                products = df_up[["name", "category", "price"]].to_dict("records")
                st.success(f"Parsed {len(products)} products from CSV.")
                st.session_state.comp_products = products
            except Exception as e:
                st.error(f"CSV parse error: {e}")
        else:
            if st.button("Extract Products from Document", type="primary"):
                with st.spinner("Extracting product list…"):
                    try:
                        products = extract_products_from_file(
                            uploaded.read(), uploaded.type or "application/pdf"
                        )
                        st.session_state.comp_products = products
                        st.success(f"Extracted {len(products)} products.")
                    except Exception as e:
                        st.error(f"Extraction failed: {e}")

elif input_mode == "Enter manually":
    st.caption("One product per line: `Product Name, Category, Price`")
    default_text = "\n".join(
        f"{p['name']}, {p['category']}, {p['price']}" for p in DR_THEISS_PRODUCTS
    )
    manual_text = st.text_area("Products", value=default_text, height=200)
    if st.button("Load Products", type="secondary"):
        products = []
        for line in manual_text.strip().splitlines():
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 2:
                try:
                    price = float(parts[2]) if len(parts) >= 3 else 0.0
                except ValueError:
                    price = 0.0
                products.append({"name": parts[0], "category": parts[1], "price": price})
        if products:
            st.session_state.comp_products = products
            st.success(f"Loaded {len(products)} products.")
        else:
            st.warning("No products parsed — check format.")

else:  # Dr. Theiss sample
    st.session_state.comp_products = DR_THEISS_PRODUCTS
    st.info("Using Dr. Theiss Naturwaren GmbH sample portfolio.")

# ── Show loaded products ────────────────────────────────────────────────────────
if st.session_state.comp_products:
    products = st.session_state.comp_products
    st.markdown(f"**{len(products)} products loaded:**")
    st.dataframe(
        pd.DataFrame([{"Product": p["name"], "Category": p["category"],
                       "Price (€)": f"€{float(p.get('price', 0)):.2f}"}
                      for p in products]),
        use_container_width=True, hide_index=True,
    )

# ── Competitor context ─────────────────────────────────────────────────────────
with st.expander("⚙️ Competitor context (editable)"):
    comp_input = st.text_area(
        "Competitors to benchmark against (comma-separated)",
        value=", ".join(COMPETITORS),
    )
    competitors = [c.strip() for c in comp_input.split(",") if c.strip()]

    st.caption("White-space hypotheses (optional context for the LLM):")
    seeds_input = st.text_area(
        "White-space seeds",
        value="\n".join(WHITE_SPACE_SEEDS),
        height=140,
    )

# ── Step 2: Run analysis ───────────────────────────────────────────────────────
st.divider()
st.markdown("### Step 2 — Run Competitive Analysis")

if not st.session_state.comp_products:
    st.info("Load your product set above first.")
elif st.button("🔍 Run Full Competitive Analysis", type="primary"):
    products = st.session_state.comp_products
    categories = list({p["category"] for p in products})
    live_intel = {}

    progress = st.progress(0)
    status   = st.empty()

    for i, cat in enumerate(categories):
        status.caption(f"🌐 Fetching live competitor data for **{cat}**…")
        try:
            live_intel[cat] = fetch_category_intel(cat, competitors)
        except Exception as e:
            live_intel[cat] = {"findings": f"Search failed: {e}", "top_competitors": [],
                               "price_range": "N/A", "dominant_format": "N/A",
                               "underserved_segments": "N/A"}
        progress.progress((i + 1) / (len(categories) + 1))

    status.caption("🧠 Generating gap matrix and opportunity ranking…")
    try:
        results = analyse_portfolio(live_intel, products)
        st.session_state.comp_intel   = live_intel
        st.session_state.comp_results = results
        st.session_state.comp_followups = []
    except Exception as e:
        st.error(f"Analysis failed: {e}")

    progress.progress(1.0)
    progress.empty()
    status.empty()

# ── Results ────────────────────────────────────────────────────────────────────
if st.session_state.comp_results:
    results = st.session_state.comp_results

    st.info(f"💡 **Market summary:** {results.get('market_summary', '')}")

    # ── Gap matrix ────────────────────────────────────────────────────────────
    st.markdown("### 📊 Competitive Gap Matrix")

    _ICONS = {"Strong": "✅", "Partial": "⚠️", "Absent": "❌",
              "Large": "🔴", "Medium": "🟡", "Small": "🟢"}

    matrix = results.get("gap_matrix", [])
    if matrix:
        rows = []
        for row in matrix:
            dr   = row.get("dr_theiss_coverage", row.get("your_coverage", "?"))
            comp = row.get("competitor_coverage", "?")
            gap  = row.get("gap_size", "?")
            rows.append({
                "Consumer Need": row.get("need", ""),
                "Your Coverage": f"{_ICONS.get(dr, '')} {dr}",
                "Competitors":   f"{_ICONS.get(comp, '')} {comp}",
                "Gap Size":      f"{_ICONS.get(gap, '')} {gap}",
                "White Space":   row.get("white_space", ""),
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # ── Opportunities ─────────────────────────────────────────────────────────
    st.markdown("### 🚀 Product Opportunities")
    opps = results.get("opportunities", [])
    if opps:
        _PRIORITY_COLOR = {"High": "#7f1d1d", "Medium": "#78350f", "Low": "#14532d"}
        _PRIORITY_BG    = {"High": "#fff1f2", "Medium": "#fffbeb", "Low": "#f0fdf4"}

        cols = st.columns(min(len(opps), 2))
        for i, opp in enumerate(opps):
            pri = opp.get("priority", "Medium")
            col = cols[i % len(cols)]
            with col:
                st.markdown(f"""
<div style="background:{_PRIORITY_BG.get(pri,'#f9fafb')}; border:1.5px solid {_PRIORITY_COLOR.get(pri,'#6b7280')};
            border-radius:10px; padding:14px 16px; margin-bottom:12px;">
  <div style="font-weight:800; font-size:14px; color:{_PRIORITY_COLOR.get(pri,'#111')}; margin-bottom:6px;">
    {opp.get('title','')}
    <span style="font-size:11px; font-weight:500; float:right;">{pri} priority · {opp.get('market_size','')} market</span>
  </div>
  <div style="font-size:12px; color:#374151; margin-bottom:4px;">
    👥 <b>Target:</b> {opp.get('target','')}
  </div>
  <div style="font-size:12px; color:#374151; margin-bottom:4px;">
    📦 <b>Format:</b> {opp.get('format','')}
  </div>
  <div style="font-size:12px; color:#6b7280; font-style:italic;">
    {opp.get('rationale','')}
  </div>
</div>""", unsafe_allow_html=True)

    # ── Live intel details ─────────────────────────────────────────────────────
    if st.session_state.comp_intel:
        with st.expander("📡 Live competitor intelligence (per category)"):
            for cat, data in st.session_state.comp_intel.items():
                st.markdown(f"**{cat}**")
                st.markdown(f"- Findings: {data.get('findings', '—')}")
                top = data.get('top_competitors', [])
                if top:
                    st.markdown(f"- Top competitors: {', '.join(top)}")
                st.markdown(f"- Price range: {data.get('price_range', 'N/A')}  |  "
                            f"Dominant format: {data.get('dominant_format', 'N/A')}")
                st.markdown(f"- Underserved: {data.get('underserved_segments', 'N/A')}")
                st.divider()

    # ── Follow-up chat ─────────────────────────────────────────────────────────
    st.divider()
    st.markdown("### 💬 Drill Down")
    st.caption("Ask follow-up questions about competitors, gaps, or opportunities.")

    for msg in st.session_state.comp_followups:
        icon  = "👤" if msg["role"] == "user" else "🔭"
        label = "You" if msg["role"] == "user" else "Analyst"
        st.markdown(f"{icon} **{label}:** {msg['content']}")

    with st.form("comp_followup_form"):
        q = st.text_input("Your question", placeholder="e.g. Who dominates the foot care segment in Germany?")
        ask_clicked = st.form_submit_button("Ask", type="primary")

    if ask_clicked and q.strip():
        with st.spinner("Researching…"):
            try:
                reply = send_followup(st.session_state.comp_followups, q.strip())
                st.session_state.comp_followups.append({"role": "user",    "content": q.strip()})
                st.session_state.comp_followups.append({"role": "analyst", "content": reply})
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
