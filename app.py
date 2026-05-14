"""
InsightAI — Concept Intelligence for Teachers
Upload corrected answer sheets → AI finds weak concepts automatically
Run: streamlit run app.py
"""

import os
import streamlit as st
from dotenv import load_dotenv
from modules.image_reader import read_all_sheets
from modules.insights import (
    build_dataframe, concept_summary, bar_chart,
    mistake_chart, question_heatmap, class_stats,
)

load_dotenv()

st.set_page_config(
    page_title="InsightAI", page_icon="🎓",
    layout="wide", initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"] { background: #0f1624 !important; }
    [data-testid="stSidebar"] { background: #111827 !important; border-right: 1px solid #1f2d3d; }
    h1,h2,h3,h4,p,label,span { color: #e2e8f0 !important; }

    .hero-title {
        font-size: 3rem; font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; line-height: 1.2; margin-bottom: 0.3rem;
    }
    .hero-sub {
        font-size: 1.1rem; color: #94a3b8 !important;
        max-width: 540px; margin: 0 auto 2rem auto; line-height: 1.7;
    }
    .step-card {
        background: linear-gradient(135deg, #1e293b, #1a2035);
        border: 1px solid #334155; border-radius: 14px;
        padding: 24px 20px; text-align: center;
    }
    .step-icon  { font-size: 2rem; margin-bottom: 10px; }
    .step-title { font-weight: 700; font-size: 1rem; color: #e2e8f0 !important; }
    .step-desc  { font-size: 0.85rem; color: #94a3b8 !important; margin-top: 6px; }

    .kpi-card {
        background: linear-gradient(135deg, #1e293b, #162032);
        border: 1px solid #334155; border-radius: 14px;
        padding: 20px 16px; text-align: center;
    }
    .kpi-val { font-size: 2rem; font-weight: 800; margin: 0; }
    .kpi-lbl { font-size: 0.78rem; color: #94a3b8 !important; margin-top: 4px; }

    .concept-card {
        border-left: 4px solid; padding: 14px 18px;
        margin-bottom: 10px; border-radius: 8px;
        background: linear-gradient(135deg, #1e293b, #162032);
        border-top: 1px solid #334155;
        border-right: 1px solid #334155;
        border-bottom: 1px solid #334155;
    }
    .focus-alert {
        background: linear-gradient(135deg,#1e1030,#2d1b4e);
        border: 1px solid #7c3aed; border-radius: 12px;
        padding: 16px 22px; margin: 16px 0;
    }
    .focus-alert-warn {
        background: linear-gradient(135deg,#1c1200,#2d2000);
        border: 1px solid #d97706; border-radius: 12px;
        padding: 16px 22px; margin: 16px 0;
    }
    .focus-alert-good {
        background: linear-gradient(135deg,#022c22,#052e16);
        border: 1px solid #16a34a; border-radius: 12px;
        padding: 16px 22px; margin: 16px 0;
    }
    .brand-block { text-align:center; padding: 10px 0 16px; }
    .brand-name {
        font-size: 1.5rem; font-weight: 800;
        background: linear-gradient(135deg,#667eea,#f093fb);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .brand-sub { font-size: 0.78rem; color: #64748b !important; }
    .key-badge {
        background: #052e16; border: 1px solid #16a34a;
        border-radius: 8px; padding: 8px 12px;
        font-size: 0.82rem; color: #4ade80 !important;
    }
    [data-testid="stButton"] button[kind="primary"] {
        background: linear-gradient(135deg,#667eea,#764ba2) !important;
        border: none !important; border-radius: 10px !important;
        font-weight: 700 !important; font-size: 1rem !important;
        color: white !important;
    }
    hr { border-color: #1f2d3d !important; }
</style>
""", unsafe_allow_html=True)


# ── API key ───────────────────────────────────────────────────────────────────
env_key = os.getenv("GEMINI_API_KEY", "").strip()

with st.sidebar:
    st.markdown("""
    <div class="brand-block">
        <div style="font-size:2.2rem;">🎓</div>
        <div class="brand-name">InsightAI</div>
        <div class="brand-sub">Concept Intelligence for Teachers</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    if env_key:
        st.markdown('<div class="key-badge">✅ &nbsp; API key loaded</div>',
                    unsafe_allow_html=True)
        api_key = env_key
    else:
        st.markdown("api key here")
        st.markdown(
            "<a href='https://openrouter.ai' target='_blank' "
            "style='color:#a78bfa;font-size:0.85rem;'>Get FREE key → openrouter.ai</a>",
            unsafe_allow_html=True,
        )
        api_key = st.text_input("Paste your key", type="password",
                                placeholder="sk-or-...", label_visibility="collapsed")

    st.divider()

    st.markdown("**📸 Upload Answer Sheets**")
    st.caption("One photo per corrected answer sheet.")
    uploaded_images = st.file_uploader(
        "drop", type=["jpg","jpeg","png","webp"],
        accept_multiple_files=True, label_visibility="collapsed",
    )
    if uploaded_images:
        st.success(f"✅ {len(uploaded_images)} sheet(s) ready")

    st.divider()

    ready   = bool(api_key and uploaded_images)
    run_btn = st.button("🚀  Analyse Papers", type="primary",
                        use_container_width=True, disabled=not ready)
    if not ready:
        if not api_key:         st.caption("⚠️ Add your Gemini API key above.")
        elif not uploaded_images: st.caption("⚠️ Upload at least one answer sheet.")

    st.divider()
    st.caption("Built with Python · OpenRouter · Streamlit")


# ── Session state ─────────────────────────────────────────────────────────────
if "results_df" not in st.session_state:
    st.session_state.results_df = None


# ── Landing ───────────────────────────────────────────────────────────────────
if st.session_state.results_df is None and not run_btn:
    st.markdown("""
    <div style="text-align:center; padding:48px 20px 36px;">
        <div class="hero-title">InsightAI</div>
        <p class="hero-sub">
            Upload photos of corrected answer sheets.<br>
            AI reads every paper and tells you exactly
            <strong style="color:#a78bfa !important;">which concepts to re-teach next class.</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    for col, icon, title, desc in zip(
        [c1, c2, c3],
        ["📸", "🤖", "📊"],
        ["Upload Sheets", "AI Reads Everything", "Get Insights"],
        [
            "Take photos of corrected answer sheets and upload them",
            "Gemini reads each paper, finds concepts & mistakes automatically",
            "See which topics to re-teach — no manual input needed",
        ],
    ):
        with col:
            st.markdown(f"""
            <div class="step-card">
                <div class="step-icon">{icon}</div>
                <div class="step-title">{title}</div>
                <div class="step-desc">{desc}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;color:#64748b;font-size:0.9rem;padding:20px 0 0;">
        👈 Upload answer sheets in the sidebar and hit Analyse — that's it.
    </div>""", unsafe_allow_html=True)
    st.stop()


# ── Run Analysis ──────────────────────────────────────────────────────────────
if run_btn and ready:
    st.markdown("## ⚙️ Reading Answer Sheets…")
    prog  = st.progress(0)
    label = st.empty()

    def on_progress(i, total):
        prog.progress(i / total)
        label.caption(f"Reading paper {i} of {total}…")

    try:
        raw_results = read_all_sheets(uploaded_images, api_key, on_progress)
        prog.progress(1.0)
        label.caption("✅ All papers read!")

        df = build_dataframe(raw_results)
        if df.empty:
            st.error("Could not extract answers from the images.")
            st.markdown("**Debug — Raw Gemini responses:**")
            for r in raw_results:
                st.json(r)
            st.stop()

        st.session_state.results_df = df
        st.rerun()

    except Exception as e:
        st.error(f"Something went wrong: {e}")
        st.stop()


# ── Dashboard ─────────────────────────────────────────────────────────────────
if st.session_state.results_df is not None:
    df         = st.session_state.results_df
    summary_df = concept_summary(df)
    stats      = class_stats(df)

    st.markdown("""
    <div style="padding:10px 0 6px;">
        <span style="font-size:1.6rem;font-weight:800;
            background:linear-gradient(135deg,#667eea,#f093fb);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            background-clip:text;">📊 Class Insight Dashboard</span>
    </div>""", unsafe_allow_html=True)

    # KPI row
    cols = st.columns(5)
    for col, lbl, val, color in zip(cols, [
        "Papers Analysed","Concepts Found","Questions/Paper",
        "Class Error Rate","Correct Rate"
    ], [
        stats["papers"], stats["concepts"], stats["questions"],
        f"{stats['error_rate']}%", f"{stats['correct_rate']}%"
    ], ["#667eea","#a78bfa","#38bdf8","#f87171","#4ade80"]):
        with col:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-val" style="color:{color};">{val}</div>
                <div class="kpi-lbl">{lbl}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Focus callout
    weakest = summary_df[summary_df["error_rate"] >= 50]
    medium  = summary_df[(summary_df["error_rate"] > 0) & (summary_df["error_rate"] < 50)]

    if not weakest.empty:
        topics = " · ".join(weakest["concept"].tolist())
        st.markdown(f"""
        <div class="focus-alert">
            🔴 &nbsp;<strong>Re-teach these next class:</strong>
            &nbsp;<span style="color:#c084fc;font-weight:700;">{topics}</span>
        </div>""", unsafe_allow_html=True)
    elif not medium.empty:
        topics = " · ".join(medium["concept"].tolist())
        st.markdown(f"""
        <div class="focus-alert-warn">
            🟡 &nbsp;<strong>Minor gaps in:</strong>
            &nbsp;<span style="color:#fbbf24;font-weight:700;">{topics}</span>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="focus-alert-good">
            🟢 &nbsp;<strong>No major concept gaps — great class performance!</strong>
        </div>""", unsafe_allow_html=True)

    st.divider()

    tab1, tab2, tab3 = st.tabs(["🏆  Weak Concepts","🗺️  Paper Heatmap","🍩  Mistake Types"])

    with tab1:
        left, right = st.columns([1, 1.5])
        with left:
            st.markdown("#### Concepts Ranked by Error Rate")
            for _, row in summary_df.iterrows():
                rate  = row["error_rate"]
                color = "#f87171" if rate >= 60 else "#fb923c" if rate >= 30 else "#4ade80"
                st.markdown(f"""
                <div class="concept-card" style="border-left-color:{color};">
                    <span style="font-size:1rem;font-weight:700;color:#e2e8f0;">
                        {row['concept']}
                    </span>
                    &nbsp;&nbsp;
                    <span style="color:{color};font-weight:800;">{rate}%</span>
                    <br>
                    <span style="color:#64748b;font-size:0.82rem;">
                        {int(row['errors'])} of {int(row['total'])} papers wrong
                        &nbsp;·&nbsp;<i>{row['top_mistake']}</i>
                    </span>
                </div>""", unsafe_allow_html=True)
        with right:
            st.plotly_chart(bar_chart(summary_df), use_container_width=True)

        st.markdown("#### Full Table")
        st.dataframe(summary_df.rename(columns={
            "concept":"Concept","total":"Papers","errors":"Errors",
            "error_rate":"Error Rate (%)","top_mistake":"Most Common Mistake",
        }), use_container_width=True, hide_index=True)

    with tab2:
        st.caption("🟢 Correct  ·  🔴 Incorrect")
        st.plotly_chart(question_heatmap(df), use_container_width=True)

    with tab3:
        fig = mistake_chart(df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("No mistakes found!")

    st.divider()
    if st.button("🔄  Analyse New Papers", use_container_width=True):
        st.session_state.pop("results_df", None)
        st.rerun()
