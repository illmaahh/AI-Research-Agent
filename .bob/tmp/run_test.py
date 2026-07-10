import subprocess, sys
result = subprocess.run(
    [sys.executable, r".bob\tmp\test_pdf_parser.py"],
    capture_output=True, text=True, encoding="utf-8", errors="replace",
    cwd=r"d:\AI-Research-Agent"
)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
sys.exit(result.returncode)
