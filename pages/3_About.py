"""
pages/3_About.py — AI Research Agent · About Page

Describes the project purpose, objectives, features, system architecture,
and the technology stack. Entirely presentational — no backend calls.
"""

from __future__ import annotations

import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="About · AI Research Agent",
    page_icon="ℹ️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
        .block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 900px; }

        /* Section headings */
        .ab-sh { font-size: 1.05rem; font-weight: 700; color: #1f2328; margin: 0 0 .15rem; }
        .ab-st { font-size: .82rem; color: #57606a; margin: 0 0 .9rem; line-height: 1.55; }

        /* Tech / feature cards */
        .ab-card {
            background: #f7f8fa;
            border: 1px solid #e5e7eb;
            border-radius: 10px;
            padding: 1.1rem 1rem;
        }
        .ab-card-icon  { font-size: 1.5rem; margin-bottom: .4rem; }
        .ab-card-title { font-size: .9rem; font-weight: 700; color: #1f2328; margin: 0 0 .25rem; }
        .ab-card-body  { font-size: .79rem; color: #57606a; line-height: 1.55; margin: 0; }

        /* Architecture boxes */
        .arch-row {
            display: flex;
            align-items: center;
            justify-content: center;
            flex-wrap: wrap;
            gap: 0;
            margin: .5rem 0 .75rem;
        }
        .arch-box {
            background: #ffffff;
            border: 1px solid #d0d7de;
            border-radius: 8px;
            padding: .65rem 1rem;
            text-align: center;
            min-width: 105px;
        }
        .arch-box-icon  { font-size: 1.2rem; }
        .arch-box-label { font-size: .74rem; font-weight: 700; color: #1f2328; margin: .1rem 0 0; }
        .arch-box-sub   { font-size: .65rem; color: #8c959f; margin: 0; }
        .arch-arrow { color: #8c959f; font-size: .95rem; padding: 0 .35rem; }

        /* Objective / feature list */
        .obj-item {
            display: flex;
            gap: .6rem;
            align-items: flex-start;
            margin-bottom: .55rem;
        }
        .obj-dot {
            width: 8px; height: 8px; border-radius: 50%;
            background: #1f2328; flex-shrink: 0; margin-top: .4rem;
        }
        .obj-text { font-size: .85rem; color: #1f2328; line-height: 1.55; }

        /* Acknowledgement box */
        .ack-box {
            background: #f7f8fa;
            border: 1px solid #e5e7eb;
            border-radius: 10px;
            padding: 1.25rem 1.5rem;
            text-align: center;
            margin-top: 1.5rem;
        }
        .ack-title { font-size: .82rem; font-weight: 700; text-transform: uppercase;
                     letter-spacing: .05em; color: #57606a; margin-bottom: .4rem; }
        .ack-text  { font-size: .9rem; color: #1f2328; line-height: 1.6; margin: 0; }
        .ack-sub   { font-size: .75rem; color: #8c959f; margin-top: .35rem; }

        /* Footer */
        .ab-footer { margin-top: 2.5rem; padding-top: 1rem; border-top: 1px solid #e5e7eb;
                     text-align: center; font-size: .75rem; color: #8c959f; }

        /* Sidebar */
        .sb-logo { font-size: 1.15rem; font-weight: 800; color: #1f2328; margin: .2rem 0 .05rem; }
        .sb-sub  { font-size: .73rem; color: #57606a; margin: 0; line-height: 1.4; }
        .sb-nav-label { font-size: .7rem; font-weight: 700; text-transform: uppercase;
                        letter-spacing: .06em; color: #8c959f; margin: .75rem 0 .25rem; }
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
    st.caption("Version 1.0  ·  IBM Granite 4")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<p class="ab-sh">ℹ️ About AI Research Agent</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="ab-st">Project purpose, objectives, architecture, and technology stack.</p>',
    unsafe_allow_html=True,
)
st.markdown("---")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1 — PROJECT OVERVIEW
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("### Project Overview")
st.markdown(
    """
    **AI Research Agent** is an intelligent assistant designed to help students,
    researchers, and academics process research papers faster and more effectively.
    By combining IBM Granite's large language model capabilities with Retrieval-Augmented
    Generation (RAG), the application extracts meaningful insights from academic PDFs
    without requiring any AI or machine learning expertise from the user.

    The project was developed as part of the **AICTE – Edunet Foundation – IBM
    SkillsBuild Internship 2026**, demonstrating practical application of generative
    AI in a real-world academic workflow.
    """
)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2 — OBJECTIVES
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("### Objectives")

OBJECTIVES = [
    "Automate the extraction and analysis of text from academic research papers.",
    "Generate structured, multi-section summaries that capture the paper's key contributions.",
    "Enable context-aware question answering strictly grounded in the uploaded document.",
    "Produce correctly formatted citations in IEEE, APA 7th, MLA, and BibTeX styles.",
    "Surface research insights such as knowledge gaps, novel contributions, and future directions.",
    "Provide a clean, accessible UI that works equally well for first-time users and power users.",
    "Demonstrate production-quality Python and a modular, maintainable codebase architecture.",
]

for obj in OBJECTIVES:
    st.markdown(
        f'<div class="obj-item">'
        f'<div class="obj-dot"></div>'
        f'<div class="obj-text">{obj}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3 — KEY FEATURES
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("### Key Features")

FEATURES = [
    ("📄", "PDF Text Extraction",
     "Uploads processed via pypdf — pure-Python, compatible with Python 3.14+. "
     "Extracts text page-by-page, detects figures, tables, equations, and references."),
    ("✨", "12-Section AI Summary",
     "IBM Granite generates a structured summary covering Objective, Background, "
     "Methodology, Dataset, Models, Setup, Findings, Results, Limitations, "
     "Future Work, Applications, and Conclusion."),
    ("💬", "RAG-Powered Q&A",
     "Document chunks are embedded using IBM Granite Embedding (278M params), "
     "indexed with FAISS, and retrieved semantically. Answers cite source pages "
     "and display a High / Medium / Low confidence indicator."),
    ("📚", "Multi-Format Citations",
     "Extracts title, authors, year, journal, DOI, and publisher metadata, "
     "then formats IEEE, APA 7th, MLA, and BibTeX citations — downloadable as .txt."),
    ("🔍", "Research Insights",
     "Analyses keywords, research domain, novel contributions, knowledge gaps, "
     "methodological strengths and weaknesses, and potential improvements."),
    ("📊", "Analytics Dashboard",
     "Visualises document statistics, estimated section word counts, document "
     "composition, structural element counts, and processing pipeline status."),
]

for row_start in range(0, len(FEATURES), 3):
    cols = st.columns(3, gap="medium")
    for col, (icon, title, body) in zip(cols, FEATURES[row_start:row_start + 3]):
        with col:
            st.markdown(
                f'<div class="ab-card">'
                f'<div class="ab-card-icon">{icon}</div>'
                f'<p class="ab-card-title">{title}</p>'
                f'<p class="ab-card-body">{body}</p>'
                f'</div>',
                unsafe_allow_html=True,
            )
    st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4 — SYSTEM ARCHITECTURE
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("### System Architecture")
st.markdown(
    '<p class="ab-st">The application is structured in three layers: '
    'the UI layer (Streamlit), the business-logic layer (utils/), '
    'and the external services layer (IBM watsonx.ai).</p>',
    unsafe_allow_html=True,
)

# Architecture diagram — rendered as styled containers
ARCH_LAYERS = [
    {
        "label": "UI Layer",
        "colour": "#e8f0fe",
        "border": "#3b82d4",
        "boxes": [
            ("🏠", "Home",       "Landing page"),
            ("🔬", "Agent",      "Main tool"),
            ("📊", "Dashboard",  "Analytics"),
            ("ℹ️",  "About",     "Project info"),
        ],
    },
    {
        "label": "Business Logic (utils/)",
        "colour": "#f0ebff",
        "border": "#7c5cd8",
        "boxes": [
            ("📃", "pdf_parser", "pypdf"),
            ("🧠", "ibm_client", "Granite chat"),
            ("🗂️",  "vector_store","FAISS RAG"),
        ],
    },
    {
        "label": "External Services",
        "colour": "#dafbe1",
        "border": "#1a7f37",
        "boxes": [
            ("☁️",  "watsonx.ai", "IBM Cloud"),
            ("🤖", "Granite 4",  "LLM inference"),
            ("🔢", "Granite Emb","Embeddings"),
        ],
    },
]

for layer in ARCH_LAYERS:
    boxes_html = ""
    for i, (icon, label, sub) in enumerate(layer["boxes"]):
        boxes_html += (
            f'<div class="arch-box">'
            f'<div class="arch-box-icon">{icon}</div>'
            f'<div class="arch-box-label">{label}</div>'
            f'<div class="arch-box-sub">{sub}</div>'
            f'</div>'
        )
        if i < len(layer["boxes"]) - 1:
            boxes_html += '<span class="arch-arrow">·</span>'

    st.markdown(
        f'<div style="background:{layer["colour"]};border:1px solid {layer["border"]};'
        f'border-radius:10px;padding:.9rem 1rem;margin-bottom:.65rem">'
        f'<div style="font-size:.7rem;font-weight:700;text-transform:uppercase;'
        f'letter-spacing:.05em;color:{layer["border"]};margin-bottom:.5rem">'
        f'{layer["label"]}</div>'
        f'<div class="arch-row">{boxes_html}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

# Data flow arrows between layers
st.markdown(
    '<div style="text-align:center;color:#8c959f;font-size:.82rem;margin:.2rem 0 .7rem">'
    'User Input &darr;&nbsp;&nbsp;&nbsp;'
    'PDF Bytes &darr;&nbsp;&nbsp;&nbsp;'
    'PageChunks &darr;&nbsp;&nbsp;&nbsp;'
    'Text/Embeddings &darr;&nbsp;&nbsp;&nbsp;'
    'AI Response &uarr;'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5 — TECHNOLOGIES
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("### Technologies Used")

TECHNOLOGIES = [
    ("🤖", "IBM Granite 4",
     "ibm/granite-4-h-small — a 131k-context chat model served via IBM watsonx.ai. "
     "Used for structured summarization, grounded Q&A, citation extraction, and "
     "research insight generation."),
    ("☁️", "IBM watsonx.ai",
     "IBM's enterprise AI platform. Provides the Model Inference API, the Embeddings "
     "API (granite-embedding-278m-multilingual), and managed GPU infrastructure "
     "so no local GPU is required."),
    ("🐍", "Python 3.14",
     "Core language. Pure-Python dependencies (pypdf, langchain-text-splitters) "
     "ensure full compatibility with the latest CPython release without binary-wheel issues."),
    ("🌐", "Streamlit 1.59",
     "Browser-based UI framework. Handles file uploads, session state, "
     "multi-page navigation, charts, and all interactive widgets with minimal boilerplate."),
    ("📄", "pypdf 6",
     "Pure-Python PDF parser. Chosen over PyMuPDF (fitz) because PyMuPDF's compiled "
     "wheel links against CPython internals removed in Python 3.14, causing a "
     "DLL load failure. pypdf works on any CPython version."),
    ("🗂️", "FAISS + LangChain",
     "facebook/faiss-cpu provides in-process L2 vector similarity search. "
     "LangChain's text splitter (langchain-text-splitters 1.x) chunks pages "
     "into ~1 000-char overlapping segments for embedding and retrieval."),
]

for row_start in range(0, len(TECHNOLOGIES), 3):
    cols = st.columns(3, gap="medium")
    for col, (icon, title, body) in zip(cols, TECHNOLOGIES[row_start:row_start + 3]):
        with col:
            st.markdown(
                f'<div class="ab-card">'
                f'<div class="ab-card-icon">{icon}</div>'
                f'<p class="ab-card-title">{title}</p>'
                f'<p class="ab-card-body">{body}</p>'
                f'</div>',
                unsafe_allow_html=True,
            )
    st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 6 — PROJECT WORKFLOW
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("### Project Workflow")

WORKFLOW = [
    ("1", "Upload PDF",
     "User uploads a research paper PDF via the file uploader on the AI Research "
     "Agent page. The file is read into memory as raw bytes."),
    ("2", "Text Extraction",
     "utils/pdf_parser.py uses pypdf to extract text from each page, returning "
     "a list of PageChunk objects. Statistics (words, figures, tables) are computed "
     "using regex heuristics. Errors surface as user-friendly messages."),
    ("3", "RAG Index Build",
     "utils/vector_store.py splits page text into 1 000-char overlapping chunks, "
     "embeds them using IBM Granite Embedding (768-d vectors), and stores them in "
     "an in-memory FAISS index. The index is cached in st.session_state."),
    ("4", "AI Inference",
     "All IBM Granite calls are routed through utils/ibm_client.py. The module "
     "constructs APIClient(scope_validation=False) to bypass the 403 pre-flight "
     "check on IBM Cloud Lite accounts, then calls the /ml/v1/text/chat endpoint."),
    ("5", "Results Display",
     "Structured results (dataclasses: AnswerResult, CitationResult, InsightResult) "
     "are stored in st.session_state and rendered across the four feature sections "
     "of app.py and the Dashboard page."),
]

for num, title, body in WORKFLOW:
    with st.container():
        st.markdown(
            f'<div style="display:flex;gap:.85rem;align-items:flex-start;'
            f'margin-bottom:.75rem;background:#f7f8fa;border:1px solid #e5e7eb;'
            f'border-radius:8px;padding:.8rem 1rem">'
            f'<div style="width:28px;height:28px;background:#1f2328;color:#fff;'
            f'border-radius:50%;display:flex;align-items:center;justify-content:center;'
            f'font-size:.82rem;font-weight:700;flex-shrink:0;margin-top:.1rem">{num}</div>'
            f'<div>'
            f'<div style="font-size:.9rem;font-weight:700;color:#1f2328;margin-bottom:.2rem">{title}</div>'
            f'<div style="font-size:.81rem;color:#57606a;line-height:1.55">{body}</div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 7 — CODEBASE STRUCTURE
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("### Codebase Structure")

st.code(
    """
AI-Research-Agent/
├── app.py                   # Main Streamlit page — AI Research Agent tool
├── pages/
│   ├── 1_Home.py            # Landing page with hero, features, workflow
│   ├── 2_Dashboard.py       # Analytics dashboard (stats, charts, timeline)
│   └── 3_About.py           # This page — architecture, objectives, tech
├── utils/
│   ├── __init__.py          # Package marker
│   ├── pdf_parser.py        # PDF text extraction (pypdf) — PageChunk, extract_pages,
│   │                        #   extract_text, get_page_count, get_statistics
│   ├── ibm_client.py        # IBM watsonx.ai client — AnswerResult, CitationResult,
│   │                        #   InsightResult, summarize_text, answer_question,
│   │                        #   extract_citations, generate_insights
│   └── vector_store.py      # RAG pipeline — IBMEmbeddingsAdapter, build_vector_store,
│                            #   query_store, RetrievedChunk
├── requirements.txt         # Python dependencies
├── .env                     # IBM credentials (not committed)
└── .env.example             # Credential template
    """.strip(),
    language="text",
)

# ─────────────────────────────────────────────────────────────────────────────
# ACKNOWLEDGEMENT
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="ack-box">'
    '<div class="ack-title">Acknowledgement</div>'
    '<p class="ack-text">'
    'Developed as part of the <strong>AICTE &ndash; Edunet Foundation &ndash; '
    'IBM SkillsBuild Internship 2026</strong>.'
    '</p>'
    '<p class="ack-sub">'
    'This project was built to demonstrate practical applications of generative AI '
    'in academic research workflows, using IBM Granite models on IBM watsonx.ai.'
    '</p>'
    '</div>',
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="ab-footer">'
    'Powered by IBM Granite &amp; watsonx.ai &nbsp;·&nbsp; '
    'Built with Streamlit &nbsp;·&nbsp; Python 3.14'
    '</div>',
    unsafe_allow_html=True,
)
