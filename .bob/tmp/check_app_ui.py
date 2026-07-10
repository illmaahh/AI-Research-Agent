"""Quick integrity check for app.py after the UI redesign."""
import ast

with open("app.py", encoding="utf-8") as f:
    src = f.read()

ast.parse(src)
print("Syntax OK")

checks = [
    ("summarize_text call",     "summarize_text(paper_text)"),
    ("extract_text call",       "extract_text(pdf_bytes)"),
    ("get_page_count call",     "get_page_count(pdf_bytes)"),
    ("EnvironmentError catch",  "except EnvironmentError"),
    ("RuntimeError catch",      "except RuntimeError"),
    ("st.download_button",      "st.download_button"),
    ("render_footer call",      "render_footer()"),
    ("render_sidebar call",     "render_sidebar()"),
    ("st.spinner on upload",    'with st.spinner("Reading paper'),
    ("expander for text",       "st.expander"),
    ("type=primary button",     'type="primary"'),
    ("footer IBM Granite text", "Powered by IBM Granite and watsonx.ai"),
    ("footer AICTE text",       "AICTE"),
    ("footer Edunet text",      "Edunet Foundation"),
    ("footer IBM SkillsBuild",  "IBM SkillsBuild Internship 2026"),
    ("hero-title class",        "hero-title"),
    ("hero-subtitle class",     "hero-subtitle"),
    ("hero-description class",  "hero-description"),
    ("summary-block class",     "summary-block"),
    ("sb-title class",          "sb-title"),
    ("sb-tagline class",        "sb-tagline"),
    ("badge-ready class",       "badge-ready"),
    ("badge-locked class",      "badge-locked"),
    ("app-footer class",        "app-footer"),
    ("session_state summary",   '"summary"'),
    ("session_state paper_text",'"paper_text"'),
    ("IBM Granite backend ref", "Generating summary with IBM Granite"),
]

failures = []
for label, pattern in checks:
    if pattern in src:
        print(f"  OK   {label}")
    else:
        print(f"  FAIL {label}  (missing: {pattern!r})")
        failures.append(label)

print()
if failures:
    print(f"{len(failures)} check(s) FAILED: {failures}")
    raise SystemExit(1)
else:
    print(f"All {len(checks)} checks passed.")
