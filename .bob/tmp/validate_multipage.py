"""
Validate that all four Streamlit pages can be parsed and their
non-Streamlit imports resolve without errors.

We cannot execute the pages (they call st.set_page_config() which
requires a running Streamlit server), but we can:
  1. Parse each file's AST to check for syntax errors.
  2. Import every non-Streamlit, non-utils module they use.
  3. Confirm that all utils symbols referenced actually exist.
"""
import sys, os, ast, importlib

_workspace = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _workspace)

PASS = 0
FAIL = 0

def check(name, condition, got=None):
    global PASS, FAIL
    if condition:
        print("  PASS  " + name)
        PASS += 1
    else:
        print("  FAIL  " + name + (("  got=" + repr(got)) if got is not None else ""))
        FAIL += 1

def check_syntax(path):
    """Return True if the file parses without SyntaxError."""
    try:
        with open(path, encoding="utf-8") as f:
            source = f.read()
        ast.parse(source)
        return True
    except SyntaxError as e:
        return str(e)

print("-" * 55)
print("Multi-page app validation")
print("-" * 55)

# --- Syntax checks ---
PAGES = [
    ("app.py",               "AI Research Agent (main)"),
    ("pages/1_Home.py",      "Home"),
    ("pages/2_Dashboard.py", "Dashboard"),
    ("pages/3_About.py",     "About"),
]

print("[1] Syntax check — all four pages")
for rel_path, label in PAGES:
    abs_path = os.path.join(_workspace, rel_path)
    result   = check_syntax(abs_path)
    check(label + " (" + rel_path + ")", result is True, result)

# --- Utils import chain ---
print("[2] Utils import chain")
try:
    from utils.pdf_parser import (
        PageChunk, extract_pages, extract_text, get_page_count, get_statistics,
    )
    check("utils.pdf_parser", True)
except Exception as e:
    check("utils.pdf_parser", False, str(e))

try:
    from utils.ibm_client import (
        AnswerResult, CitationResult, InsightResult,
        answer_question, extract_citations, generate_insights, summarize_text,
    )
    check("utils.ibm_client", True)
except Exception as e:
    check("utils.ibm_client", False, str(e))

try:
    from utils.vector_store import build_vector_store, query_store
    check("utils.vector_store", True)
except Exception as e:
    check("utils.vector_store", False, str(e))

# --- Non-Streamlit stdlib/third-party imports in new pages ---
print("[3] Non-Streamlit imports used in pages/")
for mod in ("re", "math", "datetime", "pandas"):
    try:
        importlib.import_module(mod)
        check(mod + " importable", True)
    except ImportError as e:
        check(mod + " importable", False, str(e))

# --- pages/ directory exists ---
print("[4] File existence")
for rel_path, label in PAGES:
    abs_path = os.path.join(_workspace, rel_path)
    check(label + " file exists", os.path.isfile(abs_path))

pages_dir = os.path.join(_workspace, "pages")
check("pages/ directory exists", os.path.isdir(pages_dir))

print("-" * 55)
print("Results: " + str(PASS) + " passed, " + str(FAIL) + " failed")
print("-" * 55)
sys.exit(0 if FAIL == 0 else 1)
