"""
Full import and integrity validation for the AI Research Agent.
Catches: ImportError, ModuleNotFoundError, NameError, circular imports.
Run from workspace root:  python .bob/tmp/validate_imports.py
"""
import ast, sys, traceback

PASS = []
FAIL = []

def check(label, fn):
    try:
        fn()
        PASS.append(label)
        print(f"  OK   {label}")
    except Exception as e:
        FAIL.append((label, str(e)))
        print(f"  FAIL {label}")
        print(f"       {type(e).__name__}: {e}")

# ── 1. Syntax checks (AST parse, no execution) ──────────────────────────────
for fpath in ["app.py", "utils/ibm_client.py",
              "utils/pdf_parser.py", "utils/vector_store.py",
              "utils/__init__.py"]:
    def _syntax(p=fpath):
        with open(p, encoding="utf-8") as f:
            ast.parse(f.read())
    check(f"syntax: {fpath}", _syntax)

# ── 2. Core module imports ────────────────────────────────────────────────────
def _imp_ibm():
    from utils.ibm_client import (
        AnswerResult, CitationResult, InsightResult,
        get_credentials, _get_api_client, get_model,
        summarize_text, answer_question, extract_citations, generate_insights,
        _chat, _truncate, DEFAULT_MODEL_ID, _CHAT_PARAMS, _LONG_CHAT_PARAMS,
    )
check("import: utils.ibm_client (all public symbols)", _imp_ibm)

def _imp_pdf():
    from utils.pdf_parser import (
        PageChunk, extract_pages, extract_text,
        get_page_count, get_statistics,
    )
check("import: utils.pdf_parser (all public symbols)", _imp_pdf)

def _imp_vs():
    from utils.vector_store import (
        RetrievedChunk, IBMEmbeddingsAdapter,
        get_embeddings_model, build_vector_store, query_store,
        EMBEDDING_MODEL_ID,
    )
check("import: utils.vector_store (all public symbols)", _imp_vs)

# ── 3. app.py top-level imports (without running Streamlit) ──────────────────
def _imp_app_utils():
    # Import only the utils symbols that app.py pulls in
    from utils.ibm_client import (
        AnswerResult, CitationResult, InsightResult,
        answer_question, extract_citations, generate_insights, summarize_text,
    )
    from utils.pdf_parser import (
        extract_pages, extract_text, get_page_count, get_statistics,
    )
    from utils.vector_store import build_vector_store, query_store
check("import: all symbols that app.py imports from utils/", _imp_app_utils)

# ── 4. langchain imports (the previously broken ones) ────────────────────────
def _imp_lc_splitter():
    from langchain_text_splitters import RecursiveCharacterTextSplitter
check("import: langchain_text_splitters.RecursiveCharacterTextSplitter", _imp_lc_splitter)

def _imp_lc_faiss():
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        from langchain_community.vectorstores import FAISS
check("import: langchain_community.vectorstores.FAISS", _imp_lc_faiss)

def _imp_lc_core():
    from langchain_core.embeddings import Embeddings
check("import: langchain_core.embeddings.Embeddings", _imp_lc_core)

# ── 5. Verify the old broken path no longer exists anywhere ──────────────────
def _check_no_old_langchain():
    import re
    old = re.compile(r'from langchain\.text_splitter import')
    for fpath in ["utils/vector_store.py", "utils/ibm_client.py",
                  "utils/pdf_parser.py", "app.py"]:
        with open(fpath, encoding="utf-8") as f:
            if old.search(f.read()):
                raise ImportError(
                    f"{fpath} still uses the old 'langchain.text_splitter' import path"
                )
check("no stale 'from langchain.text_splitter import' anywhere", _check_no_old_langchain)

# ── 6. Dataclass integrity ────────────────────────────────────────────────────
def _dataclasses():
    from utils.ibm_client import AnswerResult, CitationResult, InsightResult
    import dataclasses
    assert dataclasses.is_dataclass(AnswerResult)
    assert dataclasses.is_dataclass(CitationResult)
    assert dataclasses.is_dataclass(InsightResult)
    # Spot-check fields
    fields = {f.name for f in dataclasses.fields(AnswerResult)}
    assert "answer" in fields and "confidence" in fields and "not_found" in fields
    fields2 = {f.name for f in dataclasses.fields(CitationResult)}
    assert "ieee" in fields2 and "bibtex" in fields2
    fields3 = {f.name for f in dataclasses.fields(InsightResult)}
    assert "keywords" in fields3 and "research_gaps" in fields3
check("dataclass field integrity: AnswerResult, CitationResult, InsightResult", _dataclasses)

def _page_chunk():
    from utils.pdf_parser import PageChunk
    import dataclasses
    assert dataclasses.is_dataclass(PageChunk)
    fields = {f.name for f in dataclasses.fields(PageChunk)}
    assert "page_number" in fields and "text" in fields
check("dataclass field integrity: PageChunk", _page_chunk)

def _retrieved_chunk():
    from utils.vector_store import RetrievedChunk
    import dataclasses
    assert dataclasses.is_dataclass(RetrievedChunk)
    fields = {f.name for f in dataclasses.fields(RetrievedChunk)}
    assert "text" in fields and "page_number" in fields and "score" in fields
    # confidence property
    rc = RetrievedChunk(text="t", page_number=1, chunk_index=0, score=0.3)
    assert rc.confidence == "High"
    rc2 = RetrievedChunk(text="t", page_number=1, chunk_index=0, score=0.7)
    assert rc2.confidence == "Medium"
    rc3 = RetrievedChunk(text="t", page_number=1, chunk_index=0, score=1.5)
    assert rc3.confidence == "Low"
check("dataclass field integrity + confidence property: RetrievedChunk", _retrieved_chunk)

# ── 7. No circular imports ────────────────────────────────────────────────────
def _circular():
    # Reload in isolation by using a fresh subprocess would be ideal;
    # instead verify that a second import of all modules succeeds cleanly.
    import importlib
    for mod in ["utils.ibm_client", "utils.pdf_parser", "utils.vector_store"]:
        importlib.import_module(mod)
check("no circular import errors (re-import check)", _circular)

# ── Report ─────────────────────────────────────────────────────────────────────
print()
print(f"Results: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    print()
    print("FAILURES:")
    for label, err in FAIL:
        print(f"  - {label}")
        print(f"    {err}")
    sys.exit(1)
else:
    print(f"All {len(PASS)} checks passed — application is ready to start.")
