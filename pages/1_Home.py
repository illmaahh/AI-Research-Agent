"""
pages/1_Home.py — AI Research Agent · Landing Page

A professional hero landing page that introduces the application,
showcases its features, and guides the user to the main tool.

No backend calls are made here; this page is purely presentational.
"""

from __future__ import annotations

import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Home · AI Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# SHARED STYLES
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
        /* ── Layout ── */
        .block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 900px; }

        /* ── Hero ── */
        .home-hero {
            background: #f7f8fa;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 3rem 2.5rem 2.5rem;
            margin-bottom: 2.25rem;
            text-align: center;
        }
        .home-badge {
            display: inline-block;
            background: #e8f0fe;
            color: #1a56db;
            border-radius: 20px;
            padding: 3px 14px;
            font-size: .75rem;
            font-weight: 600;
            letter-spacing: .04em;
            text-transform: uppercase;
            margin-bottom: 1rem;
        }
        .home-title {
            font-size: 2.6rem;
            font-weight: 800;
            color: #1f2328;
            margin: 0 0 .6rem;
            letter-spacing: -.03em;
            line-height: 1.15;
        }
        .home-subtitle {
            font-size: 1.1rem;
            color: #57606a;
            margin: 0 auto .5rem;
            max-width: 620px;
            line-height: 1.65;
        }
        .home-powered {
            font-size: .78rem;
            color: #8c959f;
            margin: .5rem 0 1.75rem;
        }

        /* ── Feature cards ── */
        .feat-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1rem;
            margin-bottom: 2rem;
        }
        .feat-card {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 10px;
            padding: 1.25rem 1.1rem;
            text-align: left;
        }
        .feat-icon  { font-size: 1.6rem; margin-bottom: .5rem; }
        .feat-title {
            font-size: .92rem;
            font-weight: 700;
            color: #1f2328;
            margin: 0 0 .3rem;
        }
        .feat-desc  { font-size: .82rem; color: #57606a; line-height: 1.55; margin: 0; }

        /* ── Workflow ── */
        .wf-section {
            background: #f7f8fa;
            border: 1px solid #e5e7eb;
            border-radius: 10px;
            padding: 1.6rem 1.5rem 1.4rem;
            margin-bottom: 2rem;
        }
        .wf-title {
            font-size: .85rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: .06em;
            color: #57606a;
            margin: 0 0 1.1rem;
            text-align: center;
        }
        .wf-row {
            display: flex;
            align-items: center;
            justify-content: center;
            flex-wrap: wrap;
            gap: 0;
        }
        .wf-step {
            background: #ffffff;
            border: 1px solid #d0d7de;
            border-radius: 8px;
            padding: .55rem .85rem;
            text-align: center;
            min-width: 100px;
        }
        .wf-step-icon  { font-size: 1.1rem; display: block; }
        .wf-step-label { font-size: .74rem; font-weight: 600; color: #1f2328; margin: .15rem 0 0; }
        .wf-step-sub   { font-size: .67rem; color: #8c959f; margin: 0; }
        .wf-arrow {
            color: #8c959f;
            font-size: .95rem;
            padding: 0 .4rem;
            font-weight: 300;
        }

        /* ── Stats strip ── */
        .stats-strip {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: .75rem;
            margin-bottom: 2rem;
        }
        .stat-pill {
            background: #f7f8fa;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: .9rem .75rem;
            text-align: center;
        }
        .stat-pill-val { font-size: 1.5rem; font-weight: 800; color: #1f2328; }
        .stat-pill-lbl { font-size: .72rem; color: #57606a; margin-top: .1rem; }

        /* ── Footer ── */
        .home-footer {
            margin-top: 2.5rem;
            padding-top: 1rem;
            border-top: 1px solid #e5e7eb;
            text-align: center;
            font-size: .75rem;
            color: #8c959f;
        }

        /* ── Sidebar ── */
        .sb-logo { font-size: 1.15rem; font-weight: 800; color: #1f2328; margin: .2rem 0 .05rem; }
        .sb-sub  { font-size: .73rem; color: #57606a; margin: 0; line-height: 1.4; }
        .sb-nav-label {
            font-size: .7rem; font-weight: 700; text-transform: uppercase;
            letter-spacing: .06em; color: #8c959f; margin: .75rem 0 .25rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<p class="sb-logo">🔬 AI Research Agent</p>'
        '<p class="sb-sub">IBM Granite · watsonx.ai<br>AICTE SkillsBuild Internship 2026</p>',
        unsafe_allow_html=True,
    )
    st.divider()

    st.markdown('<p class="sb-nav-label">Navigation</p>', unsafe_allow_html=True)
    st.page_link("pages/1_Home.py",             label="Home",               icon="🏠")
    st.page_link("app.py",                      label="AI Research Agent",  icon="🔬")
    st.page_link("pages/2_Dashboard.py",        label="Dashboard",          icon="📊")
    st.page_link("pages/3_About.py",            label="About",              icon="ℹ️")

    st.divider()
    st.caption("Version 1.0  ·  IBM Granite 4")


# ─────────────────────────────────────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="home-hero">
        <div class="home-badge">IBM SkillsBuild Internship Project</div>
        <h1 class="home-title">AI Research Agent</h1>
        <p class="home-subtitle">
            An intelligent assistant that reads academic research papers, extracts insights,
            answers questions, and generates citations — powered by IBM Granite on watsonx.ai.
        </p>
        <p class="home-powered">Powered by IBM Granite 4 &nbsp;·&nbsp; watsonx.ai &nbsp;·&nbsp; Streamlit &nbsp;·&nbsp; FAISS RAG</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─── "Get Started" button (centred) ──────────────────────────────────────────
col_l, col_c, col_r = st.columns([2, 2, 2])
with col_c:
    st.page_link(
        "app.py",
        label="Get Started →",
        icon="🔬",
        use_container_width=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# STATS STRIP
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="stats-strip">
        <div class="stat-pill">
            <div class="stat-pill-val">12</div>
            <div class="stat-pill-lbl">Summary Sections</div>
        </div>
        <div class="stat-pill">
            <div class="stat-pill-val">4</div>
            <div class="stat-pill-lbl">Citation Formats</div>
        </div>
        <div class="stat-pill">
            <div class="stat-pill-val">RAG</div>
            <div class="stat-pill-lbl">Powered Q&amp;A</div>
        </div>
        <div class="stat-pill">
            <div class="stat-pill-val">131k</div>
            <div class="stat-pill-lbl">Context Window</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# FEATURE CARDS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("### Features")

FEATURES = [
    ("📄", "PDF Analysis",
     "Upload any text-based research paper. Instantly extract full text, "
     "page count, word count, reading time, figures, tables, and equations."),
    ("✨", "AI Summarization",
     "Generate a structured 12-section academic summary covering objective, "
     "methodology, dataset, findings, limitations, and conclusion."),
    ("💬", "Research Q&A",
     "Ask natural-language questions about the paper. Answers are grounded "
     "in the document via FAISS Retrieval-Augmented Generation — no hallucinations."),
    ("📚", "Citation Generator",
     "Automatically extract title, authors, year, and DOI, then format "
     "IEEE, APA 7th, MLA, and BibTeX citations ready to copy or download."),
    ("🔍", "Research Insights",
     "Identify keywords, research domain, novel contributions, knowledge gaps, "
     "strengths, weaknesses, and future research directions."),
    ("📊", "Analytics Dashboard",
     "Visualise document statistics with bar charts, pie charts, and metric "
     "cards — useful for quick paper assessment before deep reading."),
]

# Render 2 rows × 3 columns
for row_start in range(0, len(FEATURES), 3):
    cols = st.columns(3, gap="medium")
    for col, (icon, title, desc) in zip(cols, FEATURES[row_start:row_start + 3]):
        with col:
            st.markdown(
                f'<div class="feat-card">'
                f'<div class="feat-icon">{icon}</div>'
                f'<p class="feat-title">{title}</p>'
                f'<p class="feat-desc">{desc}</p>'
                f'</div>',
                unsafe_allow_html=True,
            )

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# WORKFLOW DIAGRAM
# ─────────────────────────────────────────────────────────────────────────────
STEPS = [
    ("📤", "Upload PDF",   "Drop file"),
    ("📃", "Extract Text", "pypdf"),
    ("🧠", "IBM Granite",  "watsonx.ai"),
    ("✨", "Summary",      "12 sections"),
    ("💬", "Q&A",          "RAG / FAISS"),
    ("📚", "Citation",     "IEEE · APA"),
]

arrows = ""
for i, (icon, label, sub) in enumerate(STEPS):
    arrows += (
        f'<div class="wf-step">'
        f'<span class="wf-step-icon">{icon}</span>'
        f'<div class="wf-step-label">{label}</div>'
        f'<div class="wf-step-sub">{sub}</div>'
        f'</div>'
    )
    if i < len(STEPS) - 1:
        arrows += '<span class="wf-arrow">›</span>'

st.markdown(
    f'<div class="wf-section">'
    f'<p class="wf-title">How It Works — End-to-End Workflow</p>'
    f'<div class="wf-row">{arrows}</div>'
    f'</div>',
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# QUICK START GUIDE
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("### Quick Start")

guide_cols = st.columns(3, gap="medium")
STEPS_GUIDE = [
    ("1", "Upload a PDF",
     "Go to the AI Research Agent page and upload any text-based academic paper "
     "using the file uploader. Scanned PDFs require an OCR layer."),
    ("2", "Explore AI Features",
     "Once the paper is loaded, use the Generate Summary, Research Q&A, "
     "Citation Generator, and Insights sections on the main page."),
    ("3", "View the Dashboard",
     "Visit the Dashboard page for charts and statistics about the uploaded paper. "
     "All metrics update automatically when a paper is loaded."),
]
for col, (num, title, body) in zip(guide_cols, STEPS_GUIDE):
    with col:
        st.markdown(
            f'<div class="feat-card">'
            f'<div style="width:28px;height:28px;background:#1f2328;color:#fff;'
            f'border-radius:50%;display:flex;align-items:center;justify-content:center;'
            f'font-size:.82rem;font-weight:700;margin-bottom:.6rem">{num}</div>'
            f'<p class="feat-title">{title}</p>'
            f'<p class="feat-desc">{body}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="home-footer">'
    'Developed as part of the <strong>AICTE &ndash; Edunet Foundation &ndash; '
    'IBM SkillsBuild Internship 2026</strong>. &nbsp;·&nbsp; '
    'Powered by IBM Granite &amp; watsonx.ai.'
    '</div>',
    unsafe_allow_html=True,
)
