"""
End-to-end smoke test for utils/pdf_parser.py using pypdf on Python 3.14.
Run from the workspace root:  python .bob/tmp/test_parser.py
"""
import sys
import os

# Ensure workspace root is on the path so 'utils' resolves correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from utils.pdf_parser import extract_text, get_page_count  # noqa: E402

# ── Minimal valid PDF with one page of selectable text ────────────────────────
# Hand-crafted so the test has no external file dependency.
PDF_WITH_TEXT = (
    b"%PDF-1.4\n"
    b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
    b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
    b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R"
    b"/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>endobj\n"
    b"4 0 obj<</Length 44>>\nstream\n"
    b"BT /F1 12 Tf 100 700 Td (Hello Research World) Tj ET\n"
    b"endstream\nendobj\n"
    b"5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj\n"
    b"xref\n0 6\n"
    b"0000000000 65535 f\r\n"
    b"0000000009 00000 n\r\n"
    b"0000000058 00000 n\r\n"
    b"0000000115 00000 n\r\n"
    b"0000000266 00000 n\r\n"
    b"0000000360 00000 n\r\n"
    b"trailer<</Size 6/Root 1 0 R>>\n"
    b"startxref\n441\n%%EOF"
)

results = []

# Test 1: normal extraction
try:
    text = extract_text(PDF_WITH_TEXT)
    assert text and len(text) > 0
    results.append(f"  PASS  extract_text — normal PDF [{len(text)} chars extracted]")
except Exception as e:
    results.append(f"  FAIL  extract_text — normal PDF: {e}")

# Test 2: page count
try:
    count = get_page_count(PDF_WITH_TEXT)
    assert count == 1, f"Expected 1, got {count}"
    results.append(f"  PASS  get_page_count = {count}")
except Exception as e:
    results.append(f"  FAIL  get_page_count: {e}")

# Test 3: empty bytes raises ValueError
try:
    extract_text(b"")
    results.append("  FAIL  empty bytes — should have raised ValueError")
except ValueError as e:
    assert "empty" in str(e).lower(), f"Wrong message: {e}"
    results.append(f'  PASS  empty bytes -> ValueError: "{e}"')
except Exception as e:
    results.append(f"  FAIL  empty bytes — wrong exception type: {e}")

# Test 4: corrupt bytes raises ValueError
try:
    extract_text(b"not a pdf at all")
    results.append("  FAIL  corrupt bytes — should have raised ValueError")
except ValueError as e:
    results.append(f'  PASS  corrupt bytes -> ValueError: "{e}"')
except Exception as e:
    results.append(f"  FAIL  corrupt bytes — wrong exception type: {type(e).__name__}: {e}")

# Test 5: get_page_count on bad input returns 0 (never raises)
try:
    result = get_page_count(b"")
    assert result == 0, f"Expected 0, got {result}"
    results.append(f"  PASS  get_page_count on bad input = {result} (no raise)")
except Exception as e:
    results.append(f"  FAIL  get_page_count raised unexpectedly: {e}")

# Report
print()
print(f"Python {sys.version}")
print()
for r in results:
    print(r)

failed = [r for r in results if r.startswith("  FAIL")]
print()
if failed:
    print(f"{len(failed)} test(s) FAILED.")
    sys.exit(1)
else:
    print(f"All {len(results)} tests passed with pypdf on Python {sys.version_info.major}.{sys.version_info.minor}.")
