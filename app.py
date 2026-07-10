"""
app.py — AI Research Agent
Intelligent Research Assistant for Academic Papers

Layout:
  Sidebar  : identity · features · paper status · about · version
  Main     : hero · upload · statistics · summary · Q&A chat · citations ·
             insights · footer
"""

from __future__ import annotations

import datetime

import streamlit as st

from utils.ibm_client import (
    AnswerResult,
    CitationResult,
    InsightResult,
    answer_question,
    extract_citations,
    generate_insights,
    summarize_text,
)
from utils.pdf_parser import extract_pages, extract_text, get_page_count, get_statistics
from utils.vector_store import build_vector_store, query_store

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL STYLES
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
        .block-container { padding-top: 2rem; padding-bottom: 1rem; max-width: 820px; }

        /* Hero */
        .hero { padding: 1.75rem 0 1.5rem; border-bottom: 1px solid #e5e7eb; margin-bottom: 1.75rem; }
        .hero-title    { font-size: 2rem; font-weight: 700; color: #1f2328; margin: 0 0 .25rem; letter-spacing: -.02em; }
        .hero-subtitle { font-size: 1rem;  color: #57606a; margin: 0 0 .6rem; }
        .hero-desc     { font-size: .875rem; color: #6e7781; line-height: 1.6; margin: 0; max-width: 620px; }

        /* Section headings */
        .sh { font-size: 1.05rem; font-weight: 600; color: #1f2328; margin: 0 0 .2rem; }
        .st { font-size: .82rem; color: #57606a; margin: 0 0 .9rem; line-height: 1.5; }

        /* Status badges */
        .bdg { display: inline-block; border-radius: 12px; padding: 1px 9px;
               font-size: .7rem; font-weight: 600; vertical-align: middle;
               margin-left: 6px; line-height: 1.8; }
        .bdg-locked { background: #f0f0f0; color: #57606a; }
        .bdg-ready  { background: #dafbe1; color: #1a7f37; }

        /* Summary blocks */
        .sb  { border-left: 3px solid #d0d7de; padding: .55rem .85rem;
               margin-bottom: .65rem; background: #f9fafb; border-radius: 0 6px 6px 0; }
        .slbl{ font-size: .72rem; font-weight: 700; text-transform: uppercase;
               letter-spacing: .05em; color: #57606a; margin-bottom: .15rem; }
        .sct { font-size: .9rem; color: #1f2328; line-height: 1.6; margin: 0; }

        /* Chat messages */
        .msg-user { background: #f0f6ff; border-radius: 12px 12px 4px 12px;
                    padding: .7rem 1rem; margin: .5rem 0; font-size: .9rem; }
        .msg-ai   { background: #f9fafb; border: 1px solid #e5e7eb;
                    border-radius: 12px 12px 12px 4px;
                    padding: .7rem 1rem; margin: .5rem 0; font-size: .9rem; }
        .msg-meta { font-size: .72rem; color: #8c959f; margin-top: .3rem; }

        /* Confidence tags */
        .conf-high { color: #1a7f37; font-weight: 600; }
        .conf-med  { color: #9a6700; font-weight: 600; }
        .conf-low  { color: #cf222e; font-weight: 600; }

        /* Statistics cards */
        .stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: .75rem; margin-bottom: 1rem; }
        .stat-card { background: #f9fafb; border: 1px solid #e5e7eb;
                     border-radius: 8px; padding: .75rem; text-align: center; }
        .stat-val  { font-size: 1.4rem; font-weight: 700; color: #1f2328; }
        .stat-lbl  { font-size: .72rem; color: #57606a; margin-top: .1rem; }

        /* Insight tags */
        .tag { display: inline-block; background: #f0f6ff; color: #0969da;
               border-radius: 12px; padding: 2px 10px; font-size: .78rem;
               margin: 2px 3px 2px 0; }

        /* Citation block */
        .cite-lbl { font-size: .72rem; font-weight: 700; text-transform: uppercase;
                    letter-spacing: .05em; color: #57606a; margin-bottom: .2rem; }

        /* Footer */
        .app-footer { margin-top: 3rem; padding-top: 1.25rem;
                      border-top: 1px solid #e5e7eb; text-align: center; }
        .fl1 { font-size: .8rem; color: #57606a; margin: 0 0 .2rem; }
        .fl2 { font-size: .72rem; color: #8c959f; margin: 0; font-style: italic; }

        /* Sidebar */
        .sb-title   { font-size: 1.1rem; font-weight: 800; color: #1f2328; margin: .2rem 0 .05rem; }
        .sb-tagline { font-size: .73rem; color: #57606a; margin: 0; line-height: 1.4; }
        .sb-nav-label { font-size: .7rem; font-weight: 700; text-transform: uppercase;
                        letter-spacing: .06em; color: #8c959f; margin: .75rem 0 .25rem; }

        table { width: 100%; font-size: .81rem; border-collapse: collapse; }
        td, th { padding: .2rem .35rem; }
        th { color: #57606a; font-weight: 600; text-align: left; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
_DEFAULTS: dict = {
    # Upload + extraction
    "uploaded_file":    None,   # st.UploadedFile
    "pdf_bytes":        None,   # bytes — stored so we can re-parse if needed
    "paper_text":       None,   # str — full plain text
    "page_chunks":      None,   # list[PageChunk] — page-level text objects
    "paper_page_count": 0,
    "extraction_error": None,
    "statistics":       None,   # dict from get_statistics()
    # RAG
    "vector_store":     None,   # FAISS store
    "rag_building":     False,  # True while index is being built
    "rag_error":        None,
    # Summary
    "summary":          None,
    "summary_error":    None,
    # Q&A chat history  — list of dicts {role, content, meta}
    "chat_history":     [],
    # Citations
    "citations":        None,   # CitationResult
    "citation_error":   None,
    # Insights
    "insights":         None,   # InsightResult
    "insights_error":   None,
}
for _k, _v in _DEFAULTS.items():
    st.session_state.setdefault(_k, _v)

paper_loaded: bool = st.session_state["uploaded_file"] is not None
text_ready:   bool = paper_loaded and st.session_state["paper_text"] is not None
rag_ready:    bool = st.session_state["vector_store"] is not None


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _now() -> str:
    return datetime.datetime.now().strftime("%H:%M")


def _conf_class(conf: str) -> str:
    return {"High": "conf-high", "Medium": "conf-med", "Low": "conf-low"}.get(conf, "")


def _badge(ready: bool) -> str:
    if ready:
        return '<span class="bdg bdg-ready">Ready</span>'
    return '<span class="bdg bdg-locked">Upload PDF first</span>'


def _section(icon: str, title: str, subtext: str, ready: bool = True) -> None:
    """Render a consistent section heading with badge."""
    st.markdown(
        f'<p class="sh">{icon} {title}{_badge(ready)}</p>'
        f'<p class="st">{subtext}</p>',
        unsafe_allow_html=True,
    )


def _primary_btn(label: str, key: str, disabled: bool = False) -> bool:
    cols = st.columns([2, 3])
    with cols[0]:
        return st.button(label, key=key, disabled=disabled,
                         type="primary", use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
def render_sidebar() -> None:
    sb = st.sidebar

    sb.markdown(
        '<p class="sb-title">🔬 AI Research Agent</p>'
        '<p class="sb-tagline">IBM Granite · watsonx.ai<br>AICTE SkillsBuild Internship 2026</p>',
        unsafe_allow_html=True,
    )
    sb.divider()

    # ── Page navigation ───────────────────────────────────────────────────────
    sb.markdown('<p class="sb-nav-label">Navigation</p>', unsafe_allow_html=True)
    sb.page_link("pages/1_Home.py",      label="Home",               icon="🏠")
    sb.page_link("app.py",               label="AI Research Agent",  icon="🔬")
    sb.page_link("pages/2_Dashboard.py", label="Dashboard",          icon="📊")
    sb.page_link("pages/3_About.py",     label="About",              icon="ℹ️")
    sb.divider()

    # ── Paper status ──────────────────────────────────────────────────────────
    sb.markdown('<p class="sb-nav-label">Paper Status</p>', unsafe_allow_html=True)
    if paper_loaded:
        fname  = st.session_state["uploaded_file"].name
        pages  = st.session_state["paper_page_count"]
        if text_ready:
            label = f"**{fname}**\n\n{pages} page{'s' if pages != 1 else ''}"
            if rag_ready:
                label += "  ·  RAG index built"
            sb.success(label)
        else:
            sb.warning(f"**{fname}** — text extraction failed")
    else:
        sb.caption("No paper uploaded yet.")
    sb.divider()

    sb.caption("Version 1.0  ·  IBM Granite 4")


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1 — UPLOAD
# ─────────────────────────────────────────────────────────────────────────────
def render_upload_section() -> None:
    """PDF upload, immediate text extraction, async RAG index trigger."""
    _section("📄", "Upload Research Paper",
             "Upload a PDF to enable AI summarization, Q&amp;A, citations, and insights.")

    uploaded = st.file_uploader(
        label="Drop a PDF here or click to browse",
        type=["pdf"],
        help="Text-based PDFs only. Scanned documents require an OCR layer.",
    )

    if uploaded is not None:
        pdf_bytes: bytes = uploaded.read()

        with st.spinner("Extracting text…"):
            try:
                pages      = extract_pages(pdf_bytes)
                full_text  = extract_text(pdf_bytes)
                page_count = get_page_count(pdf_bytes)
                stats      = get_statistics(pdf_bytes)

                st.session_state.update({
                    "uploaded_file":    uploaded,
                    "pdf_bytes":        pdf_bytes,
                    "paper_text":       full_text,
                    "page_chunks":      pages,
                    "paper_page_count": page_count,
                    "extraction_error": None,
                    "statistics":       stats,
                    # Clear stale results when a new file is loaded
                    "summary":          None,
                    "summary_error":    None,
                    "citations":        None,
                    "citation_error":   None,
                    "insights":         None,
                    "insights_error":   None,
                    "vector_store":     None,
                    "rag_error":        None,
                    "chat_history":     [],
                })
            except ValueError as exc:
                st.session_state.update({
                    "uploaded_file":    uploaded,
                    "pdf_bytes":        pdf_bytes,
                    "paper_text":       None,
                    "page_chunks":      None,
                    "paper_page_count": 0,
                    "extraction_error": str(exc),
                })

        if st.session_state["extraction_error"]:
            st.error(f"**Could not extract text.** {st.session_state['extraction_error']}", icon="🚫")
            st.caption("This usually means the PDF is scanned. Try adding an OCR layer first.")
        else:
            pc   = st.session_state["paper_page_count"]
            size = uploaded.size / 1024
            st.success(
                f"**{uploaded.name}** uploaded — "
                f"{pc} page{'s' if pc != 1 else ''},  {size:.1f} KB",
                icon="✅",
            )
            # Build the RAG index immediately after successful extraction
            _build_rag_index()

    elif paper_loaded:
        fname = st.session_state["uploaded_file"].name
        pc    = st.session_state["paper_page_count"]
        st.info(
            f"**{fname}** is loaded ({pc} page{'s' if pc != 1 else ''})."
            "  Upload a different file to replace it.",
            icon="📄",
        )


def _build_rag_index() -> None:
    """Build the FAISS vector index from the current page_chunks."""
    pages = st.session_state.get("page_chunks")
    if not pages:
        return
    with st.spinner("Building RAG index with IBM embeddings…"):
        try:
            store = build_vector_store(pages)
            st.session_state["vector_store"] = store
            st.session_state["rag_error"]    = None
            st.success("RAG index built — Q&A is ready.", icon="🗂️")
        except Exception as exc:  # noqa: BLE001
            st.session_state["vector_store"] = None
            st.session_state["rag_error"]    = str(exc)
            st.warning(
                f"RAG index could not be built: {exc}\n\n"
                "Q&A will be unavailable, but Summary and Citations still work.",
                icon="⚠️",
            )


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2 — PAPER STATISTICS
# ─────────────────────────────────────────────────────────────────────────────
def render_statistics_section() -> None:
    """Document statistics dashboard and extracted-text expander."""
    if not text_ready:
        return

    stats = st.session_state.get("statistics") or {}
    text  = st.session_state["paper_text"]

    # ── Stats grid ────────────────────────────────────────────────────────────
    st.markdown('<p class="sh">📊 Paper Statistics</p>', unsafe_allow_html=True)

    items = [
        (stats.get("pages",        0), "Pages"),
        (f"{stats.get('word_count', 0):,}", "Words"),
        (f"~{stats.get('reading_time', 0)} min", "Reading Time"),
        (stats.get("references",   0), "References"),
        (stats.get("figures",      0), "Figures"),
        (stats.get("tables",       0), "Tables"),
        (stats.get("equations",    0), "Equations"),
        (f"{stats.get('char_count', 0):,}", "Characters"),
    ]

    cols = st.columns(4)
    for i, (val, lbl) in enumerate(items):
        with cols[i % 4]:
            st.markdown(
                f'<div class="stat-card">'
                f'<div class="stat-val">{val}</div>'
                f'<div class="stat-lbl">{lbl}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ── Extracted text expander ───────────────────────────────────────────────
    wc = stats.get("word_count", len(text.split()))
    with st.expander(
        f"📃 Extracted Text — {stats.get('pages', 0)} pages,  {wc:,} words",
        expanded=False,
    ):
        st.text_area(
            label="Full extracted text",
            value=text,
            height=320,
            disabled=True,
            label_visibility="collapsed",
            help="Read-only view of the full extracted text.",
        )


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3 — AI SUMMARY
# ─────────────────────────────────────────────────────────────────────────────

# 12-section labels and icons
_SUMMARY_SECTIONS = [
    ("Research Objective",    "🎯"),
    ("Background",            "📖"),
    ("Methodology",           "🔬"),
    ("Dataset",               "🗄️"),
    ("Models/Algorithms",     "🤖"),
    ("Experimental Setup",    "⚙️"),
    ("Key Findings",          "💡"),
    ("Results",               "📈"),
    ("Limitations",           "⚠️"),
    ("Future Work",           "🚀"),
    ("Practical Applications","🌐"),
    ("Conclusion",            "✅"),
]


def _parse_summary(raw: str) -> dict[str, str]:
    """Extract section contents from the 12-section summary string."""
    sections: dict[str, str] = {}
    labels = [lbl for lbl, _ in _SUMMARY_SECTIONS]

    for i, label in enumerate(labels):
        idx = raw.find(f"{label}:")
        if idx == -1:
            continue
        start = idx + len(label) + 1
        end   = len(raw)
        for nxt in labels[i + 1:]:
            ni = raw.find(f"{nxt}:", start)
            if ni != -1:
                end = min(end, ni)
        sections[label] = raw[start:end].strip()

    return sections


def render_summary_section() -> None:
    """Section 3 — 12-section academic summary via IBM Granite."""
    _section("✨", "AI Summary", (
        "Generates a structured 12-section academic summary covering objective, "
        "methodology, findings, limitations, and more."
    ), ready=text_ready)

    cols = st.columns([2, 3])
    with cols[0]:
        clicked = st.button("Generate Summary", key="btn_summary",
                            disabled=not text_ready, type="primary",
                            use_container_width=True)
    with cols[1]:
        if not text_ready:
            st.caption("Upload a PDF above to enable this feature.")
        else:
            st.caption("Powered by IBM Granite · ~30–60 s")

    if not text_ready:
        return

    if clicked:
        with st.spinner("Generating 12-section summary…"):
            try:
                result = summarize_text(st.session_state["paper_text"])
                st.session_state["summary"]       = result
                st.session_state["summary_error"] = None
            except EnvironmentError as exc:
                st.session_state["summary"]       = None
                st.session_state["summary_error"] = f"**Config error:** {exc}"
            except RuntimeError as exc:
                st.session_state["summary"]       = None
                st.session_state["summary_error"] = f"**API error:** {exc}"
            except Exception as exc:  # noqa: BLE001
                st.session_state["summary"]       = None
                st.session_state["summary_error"] = f"**Error:** {exc}"

    err = st.session_state.get("summary_error")
    summary = st.session_state.get("summary")

    if err:
        st.error(err, icon="🚫")
        st.caption("Check credentials: https://cloud.ibm.com/iam/apikeys")
    elif summary:
        st.markdown("---")
        sections = _parse_summary(summary)

        if not sections:
            st.markdown(summary)
        else:
            parts = []
            for label, icon in _SUMMARY_SECTIONS:
                content = sections.get(label, "")
                if content:
                    parts.append(
                        f'<div class="sb">'
                        f'<div class="slbl">{icon} {label}</div>'
                        f'<p class="sct">{content}</p>'
                        f'</div>'
                    )
            st.markdown("\n".join(parts), unsafe_allow_html=True)

        # Download
        dl_text = "\n\n".join(
            f"{lbl}:\n{sections.get(lbl, '')}"
            for lbl, _ in _SUMMARY_SECTIONS
            if sections.get(lbl)
        )
        st.download_button(
            "⬇ Download Summary (.txt)",
            data=dl_text, file_name="summary.txt", mime="text/plain",
        )


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4 — RESEARCH Q&A (RAG CHAT)
# ─────────────────────────────────────────────────────────────────────────────

def _render_chat_message(role: str, content: str, meta: dict | None = None) -> None:
    """Render a single chat bubble."""
    if role == "user":
        st.markdown(
            f'<div class="msg-user">🧑 {content}'
            f'<div class="msg-meta">{meta.get("ts", "") if meta else ""}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        answer: AnswerResult = meta.get("result") if meta else None
        if answer and not answer.not_found:
            conf_cls = _conf_class(answer.confidence)
            pages_str = ", ".join(str(p) for p in answer.pages) if answer.pages else "—"
            header = (
                f'<span class="{conf_cls}">▲ {answer.confidence} confidence</span>'
                f'  ·  Pages: {pages_str}'
            )
            st.markdown(
                f'<div class="msg-ai">'
                f'<div style="font-size:.72rem;color:#57606a;margin-bottom:.35rem">'
                f'🤖 IBM Granite  ·  {meta.get("ts","")}</div>'
                f'{content}'
                f'<div class="msg-meta">{header}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            with st.expander("View retrieved context"):
                for i, chunk in enumerate(answer.chunks):
                    st.markdown(
                        f"**Context {i+1}** — Page {chunk.page_number} "
                        f"(score: {chunk.score:.3f})"
                    )
                    st.text(chunk.text[:600] + ("…" if len(chunk.text) > 600 else ""))
        elif answer and answer.not_found:
            st.markdown(
                f'<div class="msg-ai">'
                f'<div style="font-size:.72rem;color:#57606a;margin-bottom:.35rem">'
                f'🤖 IBM Granite  ·  {meta.get("ts","")}</div>'
                f'ℹ️ {content}'
                f'</div>',
                unsafe_allow_html=True,
            )
        else:
            # Fallback for legacy entries
            st.markdown(
                f'<div class="msg-ai">🤖 {content}'
                f'<div class="msg-meta">{meta.get("ts","") if meta else ""}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )


def render_qa_section() -> None:
    """Section 4 — RAG-powered conversational Q&A with chat history."""
    _section(
        "💬", "Research Q&A",
        "Ask questions about the paper. Answers are grounded strictly in the "
        "uploaded document using Retrieval-Augmented Generation — no hallucinations.",
        ready=rag_ready,
    )

    if not text_ready:
        st.caption("Upload a PDF above to enable this feature.")
        return

    rag_err = st.session_state.get("rag_error")
    if not rag_ready:
        if rag_err:
            st.warning(
                f"RAG index unavailable: {rag_err}\n\n"
                "Q&A requires the embedding index. Check your IBM credentials.",
                icon="⚠️",
            )
        else:
            if st.button("Build RAG Index", key="btn_build_rag", type="primary"):
                _build_rag_index()
                st.rerun()
        return

    # ── Chat history ──────────────────────────────────────────────────────────
    history = st.session_state["chat_history"]
    if history:
        for msg in history:
            _render_chat_message(msg["role"], msg["content"], msg.get("meta"))
    else:
        st.caption("No questions yet. Ask your first question below.")

    st.markdown("")

    # ── Input row ─────────────────────────────────────────────────────────────
    with st.form(key="qa_form", clear_on_submit=True):
        question = st.text_input(
            label="Ask a question about the paper",
            placeholder="e.g. What dataset was used? · What are the key contributions?",
            key="qa_input_field",
        )
        submitted = st.form_submit_button("Ask", type="primary", use_container_width=False)

    if submitted and question and question.strip():
        ts = _now()
        # Add user message to history
        st.session_state["chat_history"].append({
            "role":    "user",
            "content": question,
            "meta":    {"ts": ts},
        })

        with st.spinner("Searching paper and generating answer…"):
            try:
                store  = st.session_state["vector_store"]
                chunks = query_store(store, question, k=4)
                result = answer_question(question, chunks)

                ai_content = result.answer
                st.session_state["chat_history"].append({
                    "role":    "assistant",
                    "content": ai_content,
                    "meta":    {"ts": _now(), "result": result},
                })
            except EnvironmentError as exc:
                st.session_state["chat_history"].append({
                    "role":    "assistant",
                    "content": f"**Config error:** {exc}",
                    "meta":    {"ts": _now()},
                })
            except RuntimeError as exc:
                st.session_state["chat_history"].append({
                    "role":    "assistant",
                    "content": f"**API error:** {exc}",
                    "meta":    {"ts": _now()},
                })
            except Exception as exc:  # noqa: BLE001
                st.session_state["chat_history"].append({
                    "role":    "assistant",
                    "content": f"**Unexpected error:** {exc}",
                    "meta":    {"ts": _now()},
                })

        st.rerun()

    # ── Clear chat button ─────────────────────────────────────────────────────
    if history:
        if st.button("Clear conversation", key="btn_clear_chat"):
            st.session_state["chat_history"] = []
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5 — CITATION GENERATOR
# ─────────────────────────────────────────────────────────────────────────────

def render_citation_section() -> None:
    """Section 5 — Extract metadata and generate IEEE, APA, MLA, BibTeX."""
    _section(
        "📚", "Citation Generator",
        "Extracts title, authors, year, journal, and DOI then formats "
        "IEEE, APA 7th, MLA, and BibTeX citations automatically.",
        ready=text_ready,
    )

    cols = st.columns([2, 3])
    with cols[0]:
        clicked = st.button("Generate Citations", key="btn_citations",
                            disabled=not text_ready, type="primary",
                            use_container_width=True)
    with cols[1]:
        if not text_ready:
            st.caption("Upload a PDF above to enable this feature.")
        else:
            st.caption("Extracts metadata then formats 4 citation styles · ~15–30 s")

    if not text_ready:
        return

    if clicked:
        with st.spinner("Extracting metadata and formatting citations…"):
            try:
                result = extract_citations(st.session_state["paper_text"])
                st.session_state["citations"]      = result
                st.session_state["citation_error"] = None
            except EnvironmentError as exc:
                st.session_state["citations"]      = None
                st.session_state["citation_error"] = f"**Config error:** {exc}"
            except RuntimeError as exc:
                st.session_state["citations"]      = None
                st.session_state["citation_error"] = f"**API error:** {exc}"
            except Exception as exc:  # noqa: BLE001
                st.session_state["citations"]      = None
                st.session_state["citation_error"] = f"**Error:** {exc}"

    err     = st.session_state.get("citation_error")
    cit: CitationResult | None = st.session_state.get("citations")

    if err:
        st.error(err, icon="🚫")
        return

    if cit:
        st.markdown("---")

        # ── Metadata summary ──────────────────────────────────────────────────
        if any([cit.title, cit.authors, cit.year]):
            with st.expander("Extracted Metadata", expanded=True):
                cols = st.columns(2)
                if cit.title:   cols[0].markdown(f"**Title:** {cit.title}")
                if cit.authors: cols[0].markdown(f"**Authors:** {cit.authors}")
                if cit.year:    cols[1].markdown(f"**Year:** {cit.year}")
                if cit.journal: cols[1].markdown(f"**Journal:** {cit.journal}")
                if cit.doi:     cols[0].markdown(f"**DOI:** {cit.doi}")
                if cit.publisher: cols[1].markdown(f"**Publisher:** {cit.publisher}")

        # ── Citation formats ──────────────────────────────────────────────────
        formats = [
            ("IEEE",       cit.ieee),
            ("APA 7th",    cit.apa),
            ("MLA",        cit.mla),
            ("BibTeX",     cit.bibtex),
        ]

        tab_labels = [f[0] for f in formats if f[1]]
        if tab_labels:
            tabs = st.tabs(tab_labels)
            tab_idx = 0
            for fmt_name, fmt_text in formats:
                if not fmt_text:
                    continue
                with tabs[tab_idx]:
                    st.code(fmt_text, language=None)
                    st.download_button(
                        f"⬇ Download {fmt_name}",
                        data=fmt_text,
                        file_name=f"citation_{fmt_name.lower().replace(' ','')}.txt",
                        mime="text/plain",
                        key=f"dl_cit_{fmt_name}",
                    )
                tab_idx += 1
        else:
            # Fallback: show raw model output
            st.info("Could not parse structured citation. Raw model output:")
            st.text(cit.raw)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 6 — AI RESEARCH INSIGHTS
# ─────────────────────────────────────────────────────────────────────────────

def render_insights_section() -> None:
    """Section 6 — Keywords, domain, gaps, contributions, strengths/weaknesses."""
    _section(
        "🔍", "AI Research Insights",
        "Analyses the paper for keywords, research domain, gaps, "
        "novel contributions, and improvement areas.",
        ready=text_ready,
    )

    cols = st.columns([2, 3])
    with cols[0]:
        clicked = st.button("Generate Insights", key="btn_insights",
                            disabled=not text_ready, type="primary",
                            use_container_width=True)
    with cols[1]:
        if not text_ready:
            st.caption("Upload a PDF above to enable this feature.")
        else:
            st.caption("Structured analysis of the paper's academic contribution · ~30 s")

    if not text_ready:
        return

    if clicked:
        with st.spinner("Analysing paper for research insights…"):
            try:
                result = generate_insights(st.session_state["paper_text"])
                st.session_state["insights"]       = result
                st.session_state["insights_error"] = None
            except EnvironmentError as exc:
                st.session_state["insights"]       = None
                st.session_state["insights_error"] = f"**Config error:** {exc}"
            except RuntimeError as exc:
                st.session_state["insights"]       = None
                st.session_state["insights_error"] = f"**API error:** {exc}"
            except Exception as exc:  # noqa: BLE001
                st.session_state["insights"]       = None
                st.session_state["insights_error"] = f"**Error:** {exc}"

    err = st.session_state.get("insights_error")
    ins: InsightResult | None = st.session_state.get("insights")

    if err:
        st.error(err, icon="🚫")
        return

    if ins:
        st.markdown("---")

        # ── Domain + Keywords ─────────────────────────────────────────────────
        if ins.domain:
            st.markdown(f"**Research Domain:** {ins.domain}")

        if ins.keywords:
            kw_html = " ".join(f'<span class="tag">{kw}</span>' for kw in ins.keywords)
            st.markdown(f"**Keywords:**")
            st.markdown(kw_html, unsafe_allow_html=True)

        st.markdown("")

        # ── Insight grids ─────────────────────────────────────────────────────
        def _render_list(title: str, items: list[str], icon: str = "•") -> None:
            if not items:
                return
            st.markdown(f"**{title}**")
            for item in items:
                st.markdown(f"{icon} {item}")
            st.markdown("")

        col_l, col_r = st.columns(2)
        with col_l:
            _render_list("Novel Contributions",      ins.contributions,     "🟢")
            _render_list("Research Gaps",            ins.research_gaps,     "🔶")
            _render_list("Future Research Directions", ins.future_directions, "🚀")
        with col_r:
            _render_list("Strengths",     ins.strengths,    "✅")
            _render_list("Weaknesses",    ins.weaknesses,   "❌")
            _render_list("Potential Improvements", ins.improvements, "💡")


# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
def render_footer() -> None:
    st.markdown(
        '<div class="app-footer">'
        '<p class="fl1">Powered by IBM Granite and watsonx.ai</p>'
        '<p class="fl2">Developed as part of the AICTE &#8211; Edunet Foundation '
        '&#8211; IBM SkillsBuild Internship 2026.</p>'
        '</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    render_sidebar()

    st.markdown(
        '<div class="hero">'
        '<p class="hero-title">AI Research Agent</p>'
        '<p class="hero-subtitle">Intelligent Research Assistant for Academic Papers</p>'
        '<p class="hero-desc">Upload research papers, generate concise AI-powered '
        'summaries, ask context-aware questions, create citations, and accelerate '
        'your literature review using IBM Granite.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    render_upload_section()

    if text_ready:
        st.divider()
        render_statistics_section()

    st.divider()
    render_summary_section()

    st.divider()
    render_qa_section()

    st.divider()
    render_citation_section()

    st.divider()
    render_insights_section()

    render_footer()


if __name__ == "__main__":
    main()
