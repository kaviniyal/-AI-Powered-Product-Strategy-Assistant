import streamlit as st
import os
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from utils.data_processor import (
    load_and_summarize, load_from_bytes,
    build_context_string, build_extra_context, extract_text_from_bytes,
)
from agents.orchestrator import Orchestrator
from utils.vector_store import VectorStore
from utils.pdf_generator import generate_pdf

st.set_page_config(
    page_title="Product Strategy Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
/* ── Global ── */
[data-testid="stAppViewContainer"] { background: #f5f7fa; }
[data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid #e2e8f0; }
[data-testid="stSidebar"] * { color: #1e293b !important; }
[data-testid="stSidebar"] .stMarkdown p { color: #475569 !important; }
body, p, li, span { color: #1e293b; }

/* ── Hero banner ── */
.hero {
    background: linear-gradient(135deg, #1e3a8a 0%, #0369a1 50%, #0891b2 100%);
    border-radius: 16px; padding: 36px 40px; margin-bottom: 28px;
    box-shadow: 0 4px 20px rgba(3,105,161,0.2);
}
.hero h1 { color: white !important; font-size: 2.1rem; font-weight: 800; margin: 0 0 8px 0; }
.hero p  { color: rgba(255,255,255,0.9) !important; font-size: 1rem; margin: 0; }

/* ── KPI cards ── */
.kpi-card {
    background: #ffffff; border: 1px solid #e2e8f0;
    border-radius: 12px; padding: 20px 16px; text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06); transition: transform .2s, box-shadow .2s;
}
.kpi-card:hover { transform: translateY(-3px); box-shadow: 0 6px 20px rgba(3,105,161,0.12); }
.kpi-val { font-size: 1.65rem; font-weight: 800; color: #0369a1; margin-bottom: 4px; }
.kpi-lbl { font-size: 0.72rem; color: #64748b; text-transform: uppercase; letter-spacing: 1px; }
.kpi-icon { font-size: 1.4rem; margin-bottom: 6px; }

/* ── Agent result card ── */
.result-card {
    background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px;
    padding: 24px 28px; margin-top: 12px; line-height: 1.8;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.result-card h1, .result-card h2, .result-card h3 { color: #1e3a8a !important; }
.result-card strong { color: #0f172a !important; }
.result-card p, .result-card li { color: #334155 !important; }

/* ── Agent badge ── */
.agent-badge {
    display: inline-block;
    background: linear-gradient(90deg, #1e3a8a, #0369a1);
    color: white; border-radius: 20px; padding: 4px 16px;
    font-size: 0.78rem; font-weight: 600; margin-bottom: 14px; letter-spacing: 0.5px;
}

/* ── Section header ── */
.section-header {
    font-size: 1.05rem; font-weight: 700; color: #1e3a8a;
    border-left: 4px solid #0369a1; padding-left: 12px;
    margin: 20px 0 14px 0;
}

/* ── Download button ── */
.stDownloadButton button {
    background: linear-gradient(90deg, #1e3a8a, #0369a1) !important;
    color: white !important; border: none !important;
    border-radius: 8px !important; font-weight: 600 !important;
    padding: 10px 24px !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #e8f0fe; border-radius: 10px; padding: 4px;
}
.stTabs [data-baseweb="tab"] { color: #475569 !important; border-radius: 8px; font-weight: 500; }
.stTabs [aria-selected="true"] { background: #ffffff !important; color: #1e3a8a !important; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }

/* ── Progress ── */
.stProgress > div > div { background: linear-gradient(90deg,#0369a1,#0891b2) !important; border-radius: 4px; }

/* ── Chat ── */
[data-testid="stChatMessage"] { background: #f0f6ff !important; border-radius: 10px !important; border: 1px solid #e2e8f0 !important; }

/* ── Primary button ── */
.stButton button[kind="primary"] {
    background: linear-gradient(90deg,#1e3a8a,#0369a1) !important;
    color: white !important; border: none !important;
    border-radius: 8px !important; font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
default_path = os.path.join(os.path.dirname(__file__), "Sample Sales Data.csv")

with st.sidebar:
    st.markdown("## 🧠 Strategy Assistant")
    st.markdown("---")

    # ── Primary data source ───────────────────────────────────────────────────
    st.markdown("### 📊 Sales Data *(required)*")
    use_default = st.checkbox("Use bundled sample data", value=True)
    sales_upload = None
    if not use_default:
        sales_upload = st.file_uploader(
            "Upload Sales CSV", type=["csv"],
            help="CSV with columns: Revenue, Profit, Units_Sold, Customer_Rating, etc.",
            key="sales_csv",
        )

    st.markdown("---")

    # ── Additional documents ──────────────────────────────────────────────────
    st.markdown("### 📂 Additional Documents *(optional)*")
    st.caption("Upload any combination of CSV, TXT, or PDF files per category.")

    upload_categories = [
        ("reviews",    "💬 Customer Reviews / Surveys",    ["csv", "txt"]),
        ("features",   "📋 Feature Requests",              ["csv", "txt"]),
        ("market",     "🌍 Market Research Documents",     ["pdf", "txt"]),
        ("competitor", "🏢 Competitor Information",        ["pdf", "txt", "csv"]),
        ("analytics",  "📈 Product Analytics",             ["csv", "txt"]),
    ]

    extra_uploads = {}
    for key, label, ftypes in upload_categories:
        f = st.file_uploader(label, type=ftypes, key=key, label_visibility="visible")
        if f:
            extra_uploads[key] = f

    if extra_uploads:
        st.success(f"✅ {len(extra_uploads)} additional file(s) loaded")

    st.markdown("---")
    st.markdown("### Agent Pipeline")
    for icon, name in [
        ("🔵", "Customer Feedback"), ("🟢", "Sales Analysis"),
        ("🟡", "Market Research"),   ("🔴", "SWOT Analysis"),
        ("🟣", "Feature Priorities"),("⚫", "Executive Report"),
    ]:
        st.markdown(f"{icon} &nbsp; **{name}**", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**Model:** GPT-4o Mini  \n**VectorDB:** ChromaDB  \n**Framework:** Streamlit")

# ── Session state ─────────────────────────────────────────────────────────────
for key in ["results", "kpis", "vector_store", "summary"]:
    if key not in st.session_state:
        st.session_state[key] = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>🧠 AI-Powered Product Strategy Assistant</h1>
  <p>6 specialized AI agents analyze your business data to deliver customer insights, sales trends,
  SWOT analysis, feature priorities, and a downloadable executive report — all in one click.</p>
</div>
""", unsafe_allow_html=True)

col_btn, col_info = st.columns([2, 8])
with col_btn:
    run_btn = st.button("🚀 Run Analysis", type="primary", use_container_width=True)
with col_info:
    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("Uses bundled sample data (Jan–Apr 2026 · 10 products · 5 regions)")

# ── Run pipeline ──────────────────────────────────────────────────────────────
if run_btn:
    # ── Load primary sales data ───────────────────────────────────────────────
    try:
        if use_default:
            summary = load_and_summarize(default_path)
        else:
            if not sales_upload:
                st.error("Please upload a Sales CSV or check 'Use bundled sample data'.")
                st.stop()
            summary = load_from_bytes(sales_upload.read())
    except Exception as e:
        st.error(f"Error loading sales data: {e}")
        st.stop()

    # ── Load extra documents ──────────────────────────────────────────────────
    extra_docs = []
    category_labels = {
        "reviews":    "Customer Reviews / Surveys",
        "features":   "Feature Requests",
        "market":     "Market Research",
        "competitor": "Competitor Information",
        "analytics":  "Product Analytics",
    }
    for cat_key, uploaded_f in extra_uploads.items():
        content = extract_text_from_bytes(uploaded_f.read(), uploaded_f.name)
        extra_docs.append({
            "category": category_labels.get(cat_key, cat_key),
            "filename": uploaded_f.name,
            "content":  content,
        })

    data_context = build_context_string(summary) + build_extra_context(extra_docs)
    kpis = summary["kpis"]

    if extra_docs:
        st.info(f"📂 Included {len(extra_docs)} additional document(s): "
                + ", ".join(d['filename'] for d in extra_docs))

    progress_bar = st.progress(0)
    status = st.empty()
    steps = [
        "Running Customer Feedback Agent...",
        "Running Sales Analysis Agent...",
        "Running Market Research Agent...",
        "Running SWOT Analysis Agent...",
        "Running Feature Prioritization Agent...",
        "Running Executive Report Agent...",
        "Analysis complete!",
    ]
    agent_icons = ["🔵", "🟢", "🟡", "🔴", "🟣", "⚫", "✅"]

    def on_progress(msg):
        if msg in steps:
            idx = steps.index(msg)
            progress_bar.progress((idx + 1) / len(steps))
            status.info(f"{agent_icons[idx]}  {msg}")

    orch = Orchestrator()
    try:
        results = orch.run_all(data_context, kpis, progress_callback=on_progress)
    except Exception as e:
        st.error(f"Agent error: {e}")
        st.stop()

    progress_bar.progress(1.0)
    status.success("✅ All 6 agents completed! Scroll down to explore insights.")

    vs = VectorStore()
    vs.populate(results, data_context)
    st.session_state.results  = results
    st.session_state.kpis     = kpis
    st.session_state.summary  = summary
    st.session_state.vector_store = vs

# ── Results ───────────────────────────────────────────────────────────────────
if st.session_state.results:
    results = st.session_state.results
    kpis    = st.session_state.kpis
    summary = st.session_state.summary

    # ── KPI Dashboard ─────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">📊 Key Metrics Dashboard</div>', unsafe_allow_html=True)
    kpi_data = [
        ("💰", f"${kpis['total_revenue']:,.0f}", "Total Revenue"),
        ("📈", f"${kpis['total_profit']:,.0f}", "Total Profit"),
        ("📦", f"{kpis['total_units']:,}", "Units Sold"),
        ("⭐", f"{kpis['avg_rating']} / 5", "Avg Rating"),
        ("👥", f"{kpis['total_new_customers']:,}", "New Customers"),
    ]
    cols = st.columns(5)
    for col, (icon, val, lbl) in zip(cols, kpi_data):
        col.markdown(
            f'<div class="kpi-card"><div class="kpi-icon">{icon}</div>'
            f'<div class="kpi-val">{val}</div><div class="kpi-lbl">{lbl}</div></div>',
            unsafe_allow_html=True,
        )

    # ── Charts ────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">📉 Data Visualizations</div>', unsafe_allow_html=True)
    ch1, ch2, ch3 = st.columns(3)

    df_prod = pd.DataFrame(summary["product_stats"])
    df_cat  = pd.DataFrame(summary["category_stats"])
    df_mon  = pd.DataFrame(summary["monthly_trend"])
    df_reg  = pd.DataFrame(summary["region_stats"])

    CHART_BG    = "#ffffff"
    CHART_PAPER = "#f5f7fa"
    FONT_COLOR  = "#334155"
    GRID_COLOR  = "#e2e8f0"

    def style(fig):
        fig.update_layout(
            paper_bgcolor=CHART_PAPER, plot_bgcolor=CHART_BG,
            font=dict(color=FONT_COLOR, size=11),
            margin=dict(l=10, r=10, t=40, b=10),
            legend=dict(bgcolor="rgba(0,0,0,0)"),
            xaxis=dict(gridcolor=GRID_COLOR, showline=False),
            yaxis=dict(gridcolor=GRID_COLOR, showline=False),
        )
        return fig

    with ch1:
        fig = px.bar(
            df_prod.sort_values("Total_Revenue", ascending=True),
            x="Total_Revenue", y="Product_Name", orientation="h",
            color="Profit_Margin_Pct", color_continuous_scale="Blues",
            title="Revenue by Product", labels={"Total_Revenue": "Revenue ($)", "Product_Name": ""},
        )
        st.plotly_chart(style(fig), use_container_width=True)

    with ch2:
        fig = px.pie(
            df_cat, values="Revenue", names="Category",
            title="Revenue by Category",
            color_discrete_sequence=["#1e3a8a","#0369a1","#0891b2","#06b6d4","#67e8f9"],
            hole=0.45,
        )
        fig.update_traces(textposition="outside", textinfo="percent+label")
        st.plotly_chart(style(fig), use_container_width=True)

    with ch3:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_mon["Month"], y=df_mon["Revenue"],
            name="Revenue", line=dict(color="#0369a1", width=2.5), fill="tozeroy",
            fillcolor="rgba(3,105,161,0.1)",
        ))
        fig.add_trace(go.Scatter(
            x=df_mon["Month"], y=df_mon["Profit"],
            name="Profit", line=dict(color="#0891b2", width=2.5, dash="dash"),
        ))
        fig.update_layout(title="Monthly Revenue vs Profit")
        st.plotly_chart(style(fig), use_container_width=True)

    ch4, ch5 = st.columns(2)
    with ch4:
        fig = px.bar(
            df_reg.sort_values("Revenue", ascending=False),
            x="Region", y="Revenue", color="Units",
            color_continuous_scale="Blues",
            title="Revenue by Region",
        )
        st.plotly_chart(style(fig), use_container_width=True)

    with ch5:
        fig = px.scatter(
            df_prod, x="Avg_Rating", y="Profit_Margin_Pct",
            size="Total_Revenue", color="Category",
            hover_name="Product_Name",
            title="Rating vs Profit Margin (bubble = revenue)",
            labels={"Avg_Rating": "Avg Rating", "Profit_Margin_Pct": "Profit Margin (%)"},
            color_discrete_sequence=["#1e3a8a","#0369a1","#0891b2","#06b6d4","#0a9396"],
        )
        st.plotly_chart(style(fig), use_container_width=True)

    # ── Agent Tabs ────────────────────────────────────────────────────────────
    st.markdown('<div class="section-header">🤖 AI Agent Insights</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📋 Executive Summary",
        "💬 Customer Insights",
        "📈 Sales Analysis",
        "🌍 Market Research",
        "⚖️ SWOT Analysis",
        "🎯 Feature Priorities",
        "💬 Ask AI",
    ])

    def show_result(key, tab, badge_label):
        with tab:
            st.markdown(f'<div class="agent-badge">🤖 {badge_label}</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="result-card">{results[key]}</div>',
                unsafe_allow_html=True,
            )

    show_result("executive_summary",  tab1, "Executive Report Agent")
    show_result("customer_insights",  tab2, "Customer Feedback Agent")
    show_result("sales_insights",     tab3, "Sales Analysis Agent")
    show_result("market_insights",    tab4, "Market Research Agent")
    show_result("swot",               tab5, "SWOT Analysis Agent")
    show_result("feature_priorities", tab6, "Feature Prioritization Agent")

    with tab7:
        st.markdown('<div class="agent-badge">💬 RAG-Powered Chat — ChromaDB + GPT-4o Mini</div>',
                    unsafe_allow_html=True)
        st.caption("Ask anything about the analysis. The assistant searches all agent outputs to answer.")

        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if prompt := st.chat_input("e.g. Which product has the best ROI? What should we focus on in Q2?"):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("Searching insights..."):
                    answer = st.session_state.vector_store.chat(prompt)
                st.markdown(answer)
                st.session_state.chat_history.append({"role": "assistant", "content": answer})

    # ── Download ──────────────────────────────────────────────────────────────
    st.markdown("---")
    dl_col, _ = st.columns([3, 7])
    with dl_col:
        st.markdown('<div class="section-header">📥 Download Executive Report</div>',
                    unsafe_allow_html=True)
        pdf_bytes = generate_pdf(results, kpis)
        st.download_button(
            label="📥 Download PDF Report",
            data=pdf_bytes,
            file_name="Product_Strategy_Report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
        st.caption("Includes KPI dashboard + all 6 agent reports in a formatted PDF")

# ── Landing page ──────────────────────────────────────────────────────────────
else:
    st.markdown("""
<div style="background:#ffffff;border:1px solid #e2e8f0;border-radius:12px;padding:28px 32px;margin-bottom:24px;box-shadow:0 2px 8px rgba(0,0,0,0.05)">
<h3 style="color:#1e3a8a;margin-top:0">How It Works</h3>
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px">
  <div style="background:#f0f6ff;border:1px solid #bfdbfe;border-radius:8px;padding:16px">
    <div style="font-size:1.8rem;margin-bottom:8px">📁</div>
    <strong style="color:#1e3a8a">1. Data Ingestion</strong>
    <p style="font-size:0.85rem;margin:6px 0 0;color:#475569">Upload CSV, TXT, or PDF files — or use the bundled sample dataset</p>
  </div>
  <div style="background:#f0f6ff;border:1px solid #bfdbfe;border-radius:8px;padding:16px">
    <div style="font-size:1.8rem;margin-bottom:8px">🤖</div>
    <strong style="color:#1e3a8a">2. Multi-Agent Processing</strong>
    <p style="font-size:0.85rem;margin:6px 0 0;color:#475569">6 AI agents analyze different business dimensions sequentially</p>
  </div>
  <div style="background:#f0f6ff;border:1px solid #bfdbfe;border-radius:8px;padding:16px">
    <div style="font-size:1.8rem;margin-bottom:8px">📊</div>
    <strong style="color:#1e3a8a">3. Strategic Insights</strong>
    <p style="font-size:0.85rem;margin:6px 0 0;color:#475569">Charts, reports, chat Q&A and a downloadable PDF report</p>
  </div>
</div>
</div>
""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="section-header">📂 Supported Data Sources</div>', unsafe_allow_html=True)
        sources = {
            "Source": ["📊 Sales Data", "💬 Customer Reviews", "📋 Feature Requests",
                       "🌍 Market Research", "🏢 Competitor Info", "📈 Product Analytics"],
            "Formats": ["CSV", "CSV, TXT", "CSV, TXT", "PDF, TXT", "PDF, TXT, CSV", "CSV, TXT"],
            "Status":  ["Required", "Optional", "Optional", "Optional", "Optional", "Optional"],
        }
        st.dataframe(pd.DataFrame(sources), use_container_width=True, hide_index=True)

    with c2:
        st.markdown('<div class="section-header">🤖 The 6 AI Agents</div>', unsafe_allow_html=True)
        agent_table = {
            "Agent": ["🔵 Customer Feedback", "🟢 Sales Analysis", "🟡 Market Research",
                      "🔴 SWOT Analysis", "🟣 Feature Prioritization", "⚫ Executive Report"],
            "Responsibility": [
                "Sentiment, pain points, satisfaction drivers",
                "Revenue trends, margins, regional performance",
                "Opportunities, consumer behavior, positioning",
                "Strengths, Weaknesses, Opportunities, Threats",
                "Ranked improvements, Q1–Q4 roadmap",
                "Board-level summary, strategic action plan",
            ],
        }
        st.dataframe(pd.DataFrame(agent_table), use_container_width=True, hide_index=True)
