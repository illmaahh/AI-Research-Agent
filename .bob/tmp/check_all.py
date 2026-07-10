"""Syntax + integrity check for all changed files after the full RAG implementation."""
import ast, sys

# ── Syntax checks ─────────────────────────────────────────────────────────────
files = ["app.py", "utils/ibm_client.py", "utils/pdf_parser.py", "utils/vector_store.py"]
for f in files:
    with open(f, encoding="utf-8") as fh:
        ast.parse(fh.read())
    print(f"syntax OK: {f}")

# ── Integrity: app.py ──────────────────────────────────────────────────────────
with open("app.py", encoding="utf-8") as f:
    app = f.read()

app_checks = [
    ("backend import summarize_text",  "from utils.ibm_client import"),
    ("backend import extract_pages",   "from utils.pdf_parser import"),
    ("backend import build_vector_store", "from utils.vector_store import"),
    ("AnswerResult imported",          "AnswerResult"),
    ("CitationResult imported",        "CitationResult"),
    ("InsightResult imported",         "InsightResult"),
    ("answer_question imported",       "answer_question"),
    ("extract_citations imported",     "extract_citations"),
    ("generate_insights imported",     "generate_insights"),
    ("render_upload_section",          "def render_upload_section"),
    ("render_statistics_section",      "def render_statistics_section"),
    ("render_summary_section",         "def render_summary_section"),
    ("render_qa_section",              "def render_qa_section"),
    ("render_citation_section",        "def render_citation_section"),
    ("render_insights_section",        "def render_insights_section"),
    ("render_footer",                  "def render_footer"),
    ("chat history session key",       '"chat_history"'),
    ("vector_store session key",       '"vector_store"'),
    ("statistics session key",         '"statistics"'),
    ("rag_ready boolean",              "rag_ready"),
    ("text_ready boolean",             "text_ready"),
    ("st.form for Q&A",                "st.form"),
    ("st.rerun after answer",          "st.rerun()"),
    ("_build_rag_index fn",            "def _build_rag_index"),
    ("spinner on RAG build",           "Building RAG index"),
    ("spinner on summary",             "Generating 12-section summary"),
    ("spinner on citations",           "Extracting metadata and formatting"),
    ("spinner on insights",            "Analysing paper"),
    ("12 summary sections in list",    '"Research Objective"'),
    ("footer IBM Granite text",        "Powered by IBM Granite and watsonx.ai"),
    ("footer AICTE text",              "AICTE"),
    ("footer IBM SkillsBuild 2026",    "IBM SkillsBuild Internship 2026"),
    ("conf-high css class",            "conf-high"),
    ("stat-card css class",            "stat-card"),
    ("msg-user css class",             "msg-user"),
    ("msg-ai css class",               "msg-ai"),
    ("tag css class",                  '"tag"'),
]
print()
fail = []
for label, pattern in app_checks:
    ok = pattern in app
    print(f"{'OK  ' if ok else 'FAIL'} app.py: {label}")
    if not ok:
        fail.append(label)

# ── Integrity: ibm_client.py ───────────────────────────────────────────────────
with open("utils/ibm_client.py", encoding="utf-8") as f:
    ibc = f.read()

ibc_checks = [
    ("AnswerResult dataclass",     "class AnswerResult"),
    ("CitationResult dataclass",   "class CitationResult"),
    ("InsightResult dataclass",    "class InsightResult"),
    ("_chat helper",               "def _chat"),
    ("_truncate helper",           "def _truncate"),
    ("summarize_text fn",          "def summarize_text"),
    ("answer_question fn",         "def answer_question"),
    ("extract_citations fn",       "def extract_citations"),
    ("generate_insights fn",       "def generate_insights"),
    ("12-section prompt label",    "Research Objective:"),
    ("BibTeX format",              "@article{"),
    ("NOT_FOUND sentinel",         "NOT_FOUND"),
    ("json import",                "import json"),
    ("_LONG_CHAT_PARAMS",          "_LONG_CHAT_PARAMS"),
]
for label, pattern in ibc_checks:
    ok = pattern in ibc
    print(f"{'OK  ' if ok else 'FAIL'} ibm_client.py: {label}")
    if not ok:
        fail.append(label)

# ── Integrity: pdf_parser.py ───────────────────────────────────────────────────
with open("utils/pdf_parser.py", encoding="utf-8") as f:
    pp = f.read()

pp_checks = [
    ("PageChunk dataclass",   "class PageChunk"),
    ("extract_pages fn",      "def extract_pages"),
    ("extract_text fn",       "def extract_text"),
    ("get_statistics fn",     "def get_statistics"),
    ("figures regex",         "_FIGURE_PATTERN"),
    ("tables regex",          "_TABLE_PATTERN"),
    ("references regex",      "_REFERENCE_PATTERN"),
]
for label, pattern in pp_checks:
    ok = pattern in pp
    print(f"{'OK  ' if ok else 'FAIL'} pdf_parser.py: {label}")
    if not ok:
        fail.append(label)

# ── Integrity: vector_store.py ────────────────────────────────────────────────
with open("utils/vector_store.py", encoding="utf-8") as f:
    vs = f.read()

vs_checks = [
    ("RetrievedChunk dataclass",  "class RetrievedChunk"),
    ("IBMEmbeddingsAdapter",      "class IBMEmbeddingsAdapter"),
    ("get_embeddings_model fn",   "def get_embeddings_model"),
    ("build_vector_store fn",     "def build_vector_store"),
    ("query_store fn",            "def query_store"),
    ("confidence property",       "def confidence"),
    ("FAISS.from_texts call",     "FAISS.from_texts"),
    ("similarity_search call",    "similarity_search_with_score"),
]
for label, pattern in vs_checks:
    ok = pattern in vs
    print(f"{'OK  ' if ok else 'FAIL'} vector_store.py: {label}")
    if not ok:
        fail.append(label)

# ── Summary ───────────────────────────────────────────────────────────────────
print()
if fail:
    print(f"{len(fail)} check(s) FAILED: {fail}")
    sys.exit(1)
else:
    total = len(app_checks) + len(ibc_checks) + len(pp_checks) + len(vs_checks) + len(files)
    print(f"All {total} checks passed.")
