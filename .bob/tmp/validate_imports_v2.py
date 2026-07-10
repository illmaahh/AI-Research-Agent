"""
Full import chain validation for app.py
Checks every symbol that app.py imports at startup.
"""
import sys, os
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
        print("  FAIL  " + name + "  got=" + repr(got))
        FAIL += 1

print("-" * 55)
print("Full import chain validation")
print("-" * 55)

# utils/pdf_parser
print("[1] utils.pdf_parser")
try:
    from utils.pdf_parser import (
        PageChunk, extract_pages, extract_text,
        get_page_count, get_statistics,
    )
    check("extract_pages callable", callable(extract_pages))
    check("extract_text callable", callable(extract_text))
    check("get_page_count callable", callable(get_page_count))
    check("get_statistics callable", callable(get_statistics))
    check("PageChunk dataclass", hasattr(PageChunk, "__dataclass_fields__"))
except Exception as e:
    check("import ok", False, str(e))

# utils/ibm_client
print("[2] utils.ibm_client")
try:
    from utils.ibm_client import (
        AnswerResult, CitationResult, InsightResult,
        answer_question, extract_citations, generate_insights, summarize_text,
    )
    check("AnswerResult is dataclass", hasattr(AnswerResult, "__dataclass_fields__"))
    check("CitationResult is dataclass", hasattr(CitationResult, "__dataclass_fields__"))
    check("InsightResult is dataclass", hasattr(InsightResult, "__dataclass_fields__"))
    check("summarize_text callable", callable(summarize_text))
    check("answer_question callable", callable(answer_question))
    check("extract_citations callable", callable(extract_citations))
    check("generate_insights callable", callable(generate_insights))
    # Field presence checks
    ar_fields = list(AnswerResult.__dataclass_fields__.keys())
    check("AnswerResult has answer", "answer" in ar_fields)
    check("AnswerResult has confidence", "confidence" in ar_fields)
    check("AnswerResult has not_found", "not_found" in ar_fields)
    cr_fields = list(CitationResult.__dataclass_fields__.keys())
    check("CitationResult has ieee", "ieee" in cr_fields)
    check("CitationResult has bibtex", "bibtex" in cr_fields)
    ir_fields = list(InsightResult.__dataclass_fields__.keys())
    check("InsightResult has keywords", "keywords" in ir_fields)
    check("InsightResult has research_gaps", "research_gaps" in ir_fields)
except Exception as e:
    check("import ok", False, str(e))

# utils/vector_store
print("[3] utils.vector_store")
try:
    from utils.vector_store import build_vector_store, query_store
    check("build_vector_store callable", callable(build_vector_store))
    check("query_store callable", callable(query_store))
except Exception as e:
    check("import ok", False, str(e))

print("-" * 55)
print("Results: " + str(PASS) + " passed, " + str(FAIL) + " failed")
print("-" * 55)
sys.exit(0 if FAIL == 0 else 1)
