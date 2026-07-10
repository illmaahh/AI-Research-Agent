"""
Validation script for utils/pdf_parser.py
Run from workspace root: python .bob/tmp/test_pdf_parser.py
"""
import sys, os

# .bob/tmp/ is two levels below workspace root
_workspace = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _workspace)

from utils.pdf_parser import extract_pages, extract_text, get_page_count, get_statistics, PageChunk

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
print("utils/pdf_parser.py - validation")
print("-" * 55)

# --- Error path: empty bytes ---------------------------------
print("[1] Empty bytes input")
try:
    extract_pages(b"")
    check("raises ValueError", False)
except ValueError as e:
    check("raises ValueError", True)
    check("message mentions empty", "empty" in str(e).lower(), str(e))

# --- Error path: garbage bytes -------------------------------
print("[2] Garbage (non-PDF) bytes")
try:
    extract_pages(b"this is not a pdf")
    check("raises ValueError", False)
except ValueError as e:
    check("raises ValueError", True)
    check("message mentions PDF", "pdf" in str(e).lower(), str(e))

# --- Safe fallback: get_page_count ---------------------------
print("[3] get_page_count on bad input - must return 0, not raise")
result = get_page_count(b"garbage")
check("returns int", isinstance(result, int), result)
check("returns 0", result == 0, result)

# --- Safe fallback: get_statistics ---------------------------
print("[4] get_statistics on bad input - must return zero-dict, not raise")
stats = get_statistics(b"garbage")
check("returns dict", isinstance(stats, dict), stats)
check("has all 8 keys", len(stats) == 8, list(stats.keys()))
check("all values are 0", all(v == 0 for v in stats.values()), stats)

# --- Happy path: minimal valid PDF ---------------------------
print("[5] Happy path - minimal valid PDF with text layer")
try:
    # Minimal valid single-page PDF constructed entirely in memory
    MINIMAL_PDF = (
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]\n"
        b"   /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
        b"4 0 obj\n<< /Length 44 >>\nstream\n"
        b"BT /F1 12 Tf 100 700 Td (Hello World) Tj ET\n"
        b"endstream\nendobj\n"
        b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
        b"xref\n0 6\n"
        b"0000000000 65535 f \n"
        b"0000000009 00000 n \n"
        b"0000000058 00000 n \n"
        b"0000000115 00000 n \n"
        b"0000000274 00000 n \n"
        b"0000000370 00000 n \n"
        b"trailer\n<< /Size 6 /Root 1 0 R >>\n"
        b"startxref\n451\n%%EOF\n"
    )
    pc = get_page_count(MINIMAL_PDF)
    check("get_page_count returns int >= 1", isinstance(pc, int) and pc >= 1, pc)
except Exception as e:
    check("no unhandled exception", False, str(e))

# --- PageChunk dataclass -------------------------------------
print("[6] PageChunk dataclass")
chunk = PageChunk(page_number=3, text="sample text")
check("page_number set", chunk.page_number == 3)
check("text set", chunk.text == "sample text")

# --- extract_text wrapper ------------------------------------
print("[7] extract_text raises ValueError on bad input")
try:
    extract_text(b"")
    check("raises ValueError", False)
except ValueError as e:
    check("raises ValueError", True)

# --- Summary --------------------------------------------------
print("-" * 55)
print("Results: " + str(PASS) + " passed, " + str(FAIL) + " failed")
print("-" * 55)
sys.exit(0 if FAIL == 0 else 1)
