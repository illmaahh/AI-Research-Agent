"""
pages/2_Dashboard.py — AI Research Agent · Analytics Dashboard

Displays document statistics, charts, and processing metadata for the
currently loaded paper. All data is derived from st.session_state values
populated by the main AI Research Agent page (app.py).

If no paper is loaded, a friendly prompt redirects the user to upload one.
Charts are built with Streamlit's native chart primitives (no extra deps).
Where exact section-level data is unavailable, reasonable estimates are
inferred from word-count proportions and flagged with "(est.)".
"""

from __future__ import annotations

import datetime
import math
import re
from typing import Any

import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard · AI Research Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
        .block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 960px; }

        /* Metric cards */
        .dash-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: .75rem;
            margin-bottom: 1.5rem;
        }
        .dash-card {
            background: #f7f8fa;
            border: 1px solid #e5e7eb;
            border-radius: 10px;
            padding: .9rem 1rem;
            text-align: center;
        }
        .dash-val  { font-size: 1.6rem; font-weight: 800; color: #1f2328; line-height: 1.1; }
        .dash-lbl  { font-size: .72rem; color: #57606a; margin-top: .2rem; }
        .dash-est  { font-size: .65rem; color: #8c959f; font-style: italic; }

        /* Section headings */
        .db-sh { font-size: 1rem; font-weight: 700; color: #1f2328; margin: 0 0 .15rem; }
        .db-st { font-size: .8rem; color: #57606a; margin: 0 0 .75rem; line-height: 1.5; }

        /* Status badge */
        .bdg-ok  { display:inline-block; background:#dafbe1; color:#1a7f37;
                   border-radius:12px; padding:1px 9px; font-size:.7rem;
                   font-weight:600; vertical-align:middle; margin-left:6px; }
        .bdg-off { display:inline-block; background:#f0f0f0; color:#57606a;
                   border-radius:12px; padding:1px 9px; font-size:.7rem;
                   font-weight:600; vertical-align:middle; margin-left:6px; }

        /* Processing timeline */
        .tl-row  { display:flex; align-items:center; gap:.75rem;
                   padding:.55rem 0; border-bottom:1px solid #f0f0f0; }
        .tl-dot  { width:10px; height:10px; border-radius:50%;
                   background:#1a7f37; flex-shrink:0; }
        .tl-dot-off { background:#d0d7de; }
        .tl-step { font-size:.82rem; color:#1f2328; font-weight:600; }
        .tl-sub  { font-size:.73rem; color:#57606a; }

        /* Footer */
        .db-footer { margin-top:2.5rem; padding-top:1rem; border-top:1px solid #e5e7eb;
                     text-align:center; font-size:.75rem; color:#8c959f; }

        /* Sidebar */
        .sb-logo { font-size:1.15rem; font-weight:800; color:#1f2328; margin:.2rem 0 .05rem; }
        .sb-sub  { font-size:.73rem; color:#57606a; margin:0; line-height:1.4; }
        .sb-nav-label { font-size:.7rem; font-weight:700; text-transform:uppercase;
                        letter-spacing:.06em; color:#8c959f; margin:.75rem 0 .25rem; }
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
    st.page_link("pages/1_Home.py",      label="Home",               icon="🏠")
    st.page_link("app.py",               label="AI Research Agent",  icon="🔬")
    st.page_link("pages/2_Dashboard.py", label="Dashboard",          icon="📊")
    st.page_link("pages/3_About.py",     label="About",              icon="ℹ️")

    st.divider()

    # Live paper status in sidebar
    text_ready = bool(st.session_state.get("paper_text"))
    rag_ready  = bool(st.session_state.get("vector_store"))

    if text_ready:
        fname = st.session_state.get("uploaded_file")
        fname = fname.name if fname else "Unknown"
        pages = st.session_state.get("paper_page_count", 0)
        lbl   = f"**{fname}**\n\n{pages} page{'s' if pages != 1 else ''}"
        if rag_ready:
            lbl += "  ·  RAG ready"
        st.success(lbl)
    else:
        st.caption("No paper uploaded yet.")

    st.divider()
    st.caption("Version 1.0  ·  IBM Granite 4")


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _fmt(n: int | float, suffix: str = "") -> str:
    """Format large numbers with comma separators."""
    return f"{n:,}{suffix}" if isinstance(n, int) else f"{n:.1f}{suffix}"


def _estimate_section_words(full_text: str) -> dict[str, int]:
    """
    Estimate word count per paper section using heading heuristics.

    Sections that cannot be detected are assigned a proportional share of
    the remainder.  All estimated values are flagged in the UI.

    Returns a dict: section_name -> word_count
    """
    if not full_text:
        return {}

    # Regex for common section headings (case-insensitive)
    heading_re = re.compile(
        r"^(?:abstract|introduction|related work|background|"
        r"methodology|methods|materials and methods|"
        r"experimental (?:setup|results?)|results?|"
        r"discussion|conclusion|references|acknowledgements?|appendix)",
        re.IGNORECASE | re.MULTILINE,
    )

    matches = list(heading_re.finditer(full_text))
    if len(matches) < 2:
        # Fallback: estimate using fixed proportions typical for CS/ML papers
        total = len(full_text.split())
        return {
            "Abstract (est.)":      max(1, round(total * 0.04)),
            "Introduction (est.)":  max(1, round(total * 0.12)),
            "Methods (est.)":       max(1, round(total * 0.22)),
            "Results (est.)":       max(1, round(total * 0.25)),
            "Discussion (est.)":    max(1, round(total * 0.18)),
            "Conclusion (est.)":    max(1, round(total * 0.08)),
            "References (est.)":    max(1, round(total * 0.11)),
        }

    sections: dict[str, int] = {}
    for i, m in enumerate(matches):
        end   = matches[i + 1].start() if i + 1 < len(matches) else len(full_text)
        words = len(full_text[m.start():end].split())
        # Capitalise and deduplicate section names
        name  = m.group(0).strip().title()
        sections[name] = sections.get(name, 0) + words

    return sections


def _estimate_composition(stats: dict) -> dict[str, float]:
    """
    Estimate document composition percentages for the pie chart.

    Uses reference counts, figure/table mentions to infer ratios.
    """
    wc   = max(1, stats.get("word_count",  1))
    refs = stats.get("references", 0)
    figs = stats.get("figures",    0)
    tabs = stats.get("tables",     0)

    # Rough word budgets for structural elements
    ref_words  = refs * 15         # ~15 words per reference entry
    fig_words  = figs * 30         # ~30 words for caption + label
    tab_words  = tabs * 40         # ~40 words per table
    body_words = max(1, wc - ref_words - fig_words - tab_words)

    # Body further split by fixed CS-paper proportions
    intro    = round(body_words * 0.15)
    methods  = round(body_words * 0.28)
    results  = round(body_words * 0.27)
    disc     = round(body_words * 0.17)
    conc     = round(body_words * 0.13)

    total = intro + methods + results + disc + conc + ref_words + fig_words + tab_words
    total = max(1, total)

    return {
        "Introduction":   round(intro      / total * 100, 1),
        "Methods":        round(methods    / total * 100, 1),
        "Results":        round(results    / total * 100, 1),
        "Discussion":     round(disc       / total * 100, 1),
        "Conclusion":     round(conc       / total * 100, 1),
        "References":     round(ref_words  / total * 100, 1),
        "Figures/Tables": round((fig_words + tab_words) / total * 100, 1),
    }


# ─────────────────────────────────────────────────────────────────────────────
# PAGE HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<p class="db-sh">📊 Analytics Dashboard</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="db-st">Document statistics, composition estimates, and processing '
    'status for the currently loaded research paper.</p>',
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# GATE: no paper loaded
# ─────────────────────────────────────────────────────────────────────────────
text_ready = bool(st.session_state.get("paper_text"))

if not text_ready:
    st.info(
        "**No paper loaded yet.** Upload a research paper on the AI Research Agent "
        "page to populate the dashboard.",
        icon="📄",
    )
    st.page_link("app.py", label="Go to AI Research Agent →", icon="🔬")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# READ SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
stats:     dict       = st.session_state.get("statistics") or {}
full_text: str        = st.session_state.get("paper_text", "")
rag_ready: bool       = bool(st.session_state.get("vector_store"))
summary:   str | None = st.session_state.get("summary")
uploaded              = st.session_state.get("uploaded_file")
fname: str            = uploaded.name if uploaded else "Unknown"

pages       = stats.get("pages",        0)
words       = stats.get("word_count",   0)
chars       = stats.get("char_count",   0)
read_min    = stats.get("reading_time", 0)
references  = stats.get("references",  0)
figures     = stats.get("figures",     0)
tables      = stats.get("tables",      0)
equations   = stats.get("equations",   0)

# File size from the UploadedFile object
file_size_kb: float = (uploaded.size / 1024) if uploaded and hasattr(uploaded, "size") else 0.0

# Rough processing time estimate: 0.05 s per page of text extraction
proc_secs   = max(1, round(pages * 0.05 + len(full_text) / 50_000, 1))

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1 — PAPER IDENTITY
# ─────────────────────────────────────────────────────────────────────────────
rag_badge  = '<span class="bdg-ok">RAG Ready</span>'  if rag_ready else '<span class="bdg-off">RAG not built</span>'
text_badge = '<span class="bdg-ok">Text Extracted</span>'

st.markdown(
    f'<p class="db-sh">📄 {fname}'
    f'{text_badge}{rag_badge}'
    f'</p>',
    unsafe_allow_html=True,
)
st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2 — METRIC CARDS (row 1: primary)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<p class="db-sh">Key Metrics</p>', unsafe_allow_html=True)

metrics_row1 = [
    (_fmt(pages),             "Total Pages",           ""),
    (_fmt(words),             "Word Count",             ""),
    (f"~{read_min} min",      "Est. Reading Time",      "@ 200 wpm"),
    (_fmt(references),        "References Detected",    ""),
]
metrics_row2 = [
    (_fmt(figures),           "Figures",                ""),
    (_fmt(tables),            "Tables",                 ""),
    (_fmt(equations),         "Equations",              ""),
    (f"{file_size_kb:.1f} KB","File Size",              ""),
]

def _card_row(items: list[tuple[str, str, str]]) -> None:
    cols = st.columns(4)
    for col, (val, lbl, sub) in zip(cols, items):
        with col:
            sub_html = f'<div class="dash-est">{sub}</div>' if sub else ""
            st.markdown(
                f'<div class="dash-card">'
                f'<div class="dash-val">{val}</div>'
                f'<div class="dash-lbl">{lbl}</div>'
                f'{sub_html}'
                f'</div>',
                unsafe_allow_html=True,
            )

_card_row(metrics_row1)
_card_row(metrics_row2)
st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3 — AI & PROCESSING INFO CARDS
# ─────────────────────────────────────────────────────────────────────────────
ai_cards = [
    (f"~{proc_secs} s",    "Processing Time",   "Text extraction + indexing (est.)"),
    ("ibm/granite-4-h-small", "AI Model",        "IBM Granite 4 · 131k context"),
    ("pypdf",              "PDF Engine",         "Pure-Python · Python 3.14 safe"),
    ("FAISS",              "Vector Store",       "In-memory · CPU · L2 distance"),
]
cols = st.columns(4)
for col, (val, lbl, sub) in zip(cols, ai_cards):
    with col:
        st.markdown(
            f'<div class="dash-card">'
            f'<div class="dash-val" style="font-size:1rem;font-weight:700">{val}</div>'
            f'<div class="dash-lbl" style="font-weight:600">{lbl}</div>'
            f'<div class="dash-est">{sub}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4 — CHARTS
# ─────────────────────────────────────────────────────────────────────────────
chart_left, chart_right = st.columns([3, 2], gap="large")

# ── Left: Bar chart — section word counts ────────────────────────────────────
with chart_left:
    st.markdown(
        '<p class="db-sh">Section Word Counts <span style="font-size:.7rem;'
        'color:#8c959f;font-weight:400">(est.)</span></p>'
        '<p class="db-st">Estimated word distribution across paper sections, '
        'inferred from heading detection and fixed proportions where headings '
        'are absent.</p>',
        unsafe_allow_html=True,
    )

    section_words = _estimate_section_words(full_text)
    if section_words:
        import pandas as pd
        df_bar = pd.DataFrame({
            "Section":    list(section_words.keys()),
            "Word Count": list(section_words.values()),
        }).sort_values("Word Count", ascending=False)

        st.bar_chart(df_bar.set_index("Section"), use_container_width=True, height=280)
    else:
        st.caption("No section data available.")

# ── Right: Structural element counts ─────────────────────────────────────────
with chart_right:
    st.markdown(
        '<p class="db-sh">Structural Elements</p>'
        '<p class="db-st">Counts of detected structural elements in the paper.</p>',
        unsafe_allow_html=True,
    )

    elements = {
        "References": references,
        "Figures":    figures,
        "Tables":     tables,
        "Equations":  equations,
    }
    # Only show bar chart if at least one element was found
    if any(v > 0 for v in elements.values()):
        import pandas as pd
        df_elem = pd.DataFrame({
            "Element": list(elements.keys()),
            "Count":   list(elements.values()),
        })
        st.bar_chart(df_elem.set_index("Element"), use_container_width=True, height=280)
    else:
        st.info("No structural elements detected. This can happen with "
                "plain-text or minimally formatted PDFs.")

st.markdown("<br>", unsafe_allow_html=True)

# ── Full-width: Document composition pie-like breakdown ───────────────────────
st.markdown(
    '<p class="db-sh">Document Composition <span style="font-size:.7rem;'
    'color:#8c959f;font-weight:400">(est.)</span></p>'
    '<p class="db-st">Estimated percentage breakdown of the document by content type, '
    'derived from structural element counts and word-count proportions.</p>',
    unsafe_allow_html=True,
)

comp = _estimate_composition(stats)
# Render as a horizontal stacked-style bar using st.progress strips
COMP_COLOURS = {
    "Introduction":   "#3b82d4",
    "Methods":        "#7c5cd8",
    "Results":        "#1a7f37",
    "Discussion":     "#9a6700",
    "Conclusion":     "#cf222e",
    "References":     "#57606a",
    "Figures/Tables": "#0969da",
}

comp_cols = st.columns(len(comp))
for col, (section, pct) in zip(comp_cols, comp.items()):
    colour = COMP_COLOURS.get(section, "#57606a")
    with col:
        st.markdown(
            f'<div style="background:{colour};border-radius:6px 6px 0 0;'
            f'height:{max(8, int(pct * 2.5))}px;"></div>'
            f'<div style="font-size:.72rem;font-weight:700;color:{colour};'
            f'margin-top:.3rem">{pct}%</div>'
            f'<div style="font-size:.67rem;color:#57606a">{section}</div>',
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5 — PROCESSING TIMELINE
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    '<p class="db-sh">Processing Pipeline Status</p>'
    '<p class="db-st">Shows which processing stages have been completed '
    'for the currently loaded paper.</p>',
    unsafe_allow_html=True,
)

summary_done  = bool(summary)
cit_done      = bool(st.session_state.get("citations"))
insights_done = bool(st.session_state.get("insights"))

PIPELINE_STEPS = [
    (True,          "PDF Upload",             f"{fname}"),
    (True,          "Text Extraction",        f"{pages} pages  ·  {words:,} words"),
    (rag_ready,     "RAG Index (FAISS)",      "IBM Granite embeddings"  if rag_ready else "Not yet built — go to AI Research Agent"),
    (summary_done,  "AI Summary",             "12-section summary ready" if summary_done  else "Not yet generated"),
    (cit_done,      "Citation Generation",    "IEEE · APA · MLA · BibTeX" if cit_done    else "Not yet generated"),
    (insights_done, "Research Insights",      "Keywords, gaps, contributions" if insights_done else "Not yet generated"),
]

tl_html = ""
for done, step, detail in PIPELINE_STEPS:
    dot_cls  = "tl-dot" if done else "tl-dot tl-dot-off"
    clr      = "#1f2328" if done else "#8c959f"
    tl_html += (
        f'<div class="tl-row">'
        f'<div class="{dot_cls}"></div>'
        f'<div>'
        f'<div class="tl-step" style="color:{clr}">{step}</div>'
        f'<div class="tl-sub">{detail}</div>'
        f'</div>'
        f'</div>'
    )

st.markdown(
    f'<div style="background:#f7f8fa;border:1px solid #e5e7eb;'
    f'border-radius:10px;padding:1rem 1.25rem">{tl_html}</div>',
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="db-footer">'
    'Developed as part of the <strong>AICTE &ndash; Edunet Foundation &ndash; '
    'IBM SkillsBuild Internship 2026</strong>. &nbsp;·&nbsp; '
    'Powered by IBM Granite &amp; watsonx.ai.'
    '</div>',
    unsafe_allow_html=True,
)
