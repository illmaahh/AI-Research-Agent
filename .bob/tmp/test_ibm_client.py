"""
Logic test for utils/ibm_client.py — no live IBM credentials required.
Stubs ModelInference and Credentials so every code path can be exercised.
Run from workspace root: python .bob/tmp/test_ibm_client.py
"""
import sys, os, types

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# ── Stub the entire ibm_watsonx_ai namespace ─────────────────────────────────
ibm_mod = types.ModuleType("ibm_watsonx_ai")

class FakeCredentials:
    def __init__(self, api_key, url): pass

ibm_mod.Credentials = FakeCredentials

fm_mod = types.ModuleType("ibm_watsonx_ai.foundation_models")

class FakeModelInference:
    _should_fail = False
    _response = "The study aims to evaluate deep learning. Methodology: CNN on ImageNet. Key Findings: 94% accuracy. Limitations: small dataset. Conclusion: promising direction."
    def __init__(self, **kwargs): pass
    def generate_text(self, prompt):
        if FakeModelInference._should_fail:
            raise ConnectionError("simulated network error")
        return FakeModelInference._response

fm_mod.ModelInference = FakeModelInference

meta_mod = types.ModuleType("ibm_watsonx_ai.metanames")
class FakeParamNames:
    DECODING_METHOD    = "decoding_method"
    MAX_NEW_TOKENS     = "max_new_tokens"
    MIN_NEW_TOKENS     = "min_new_tokens"
    REPETITION_PENALTY = "repetition_penalty"
    STOP_SEQUENCES     = "stop_sequences"
meta_mod.GenTextParamsMetaNames = FakeParamNames

sys.modules["ibm_watsonx_ai"] = ibm_mod
sys.modules["ibm_watsonx_ai.foundation_models"] = fm_mod
sys.modules["ibm_watsonx_ai.metanames"] = meta_mod

# ── Now import the real module ────────────────────────────────────────────────
from utils.ibm_client import get_credentials, get_model, summarize_text, _build_summary_prompt

results = []

# Test 1: get_credentials raises EnvironmentError when vars missing
os.environ.pop("IBM_API_KEY",    None)
os.environ.pop("IBM_PROJECT_ID", None)
os.environ.pop("IBM_URL",        None)
try:
    get_credentials()
    results.append("FAIL  get_credentials — should raise EnvironmentError when vars missing")
except EnvironmentError as e:
    assert "IBM_API_KEY" in str(e)
    results.append(f'PASS  get_credentials raises EnvironmentError: "{str(e)[:60]}..."')

# Test 2: get_credentials returns dict when all vars present
os.environ["IBM_API_KEY"]    = "test-key"
os.environ["IBM_PROJECT_ID"] = "test-project"
os.environ["IBM_URL"]        = "https://us-south.ml.cloud.ibm.com"
creds = get_credentials()
assert creds == {"api_key": "test-key", "project_id": "test-project", "url": "https://us-south.ml.cloud.ibm.com"}
results.append("PASS  get_credentials returns correct dict")

# Test 3: get_model returns a ModelInference instance
model = get_model()
assert isinstance(model, FakeModelInference)
results.append("PASS  get_model returns ModelInference instance")

# Test 4: summarize_text raises ValueError for empty input
try:
    summarize_text("")
    results.append("FAIL  summarize_text — should raise ValueError on empty string")
except ValueError:
    results.append("PASS  summarize_text raises ValueError on empty input")

# Test 5: summarize_text raises ValueError for whitespace-only input
try:
    summarize_text("   \n  ")
    results.append("FAIL  summarize_text — should raise ValueError on whitespace input")
except ValueError:
    results.append("PASS  summarize_text raises ValueError on whitespace-only input")

# Test 6: summarize_text returns string starting with "Objective:"
summary = summarize_text("This is a test paper about machine learning.")
assert summary.startswith("Objective:"), f"Got: {summary[:40]!r}"
results.append(f'PASS  summarize_text returns summary starting with "Objective:"')

# Test 7: long input is truncated (> _MAX_INPUT_CHARS)
long_text = "word " * 5000   # ~25 000 chars, well over the 11 000-char limit
summary2 = summarize_text(long_text)
assert summary2.startswith("Objective:")
results.append("PASS  summarize_text handles long input without error")

# Test 8: API failure is wrapped as RuntimeError
FakeModelInference._should_fail = True
try:
    summarize_text("Short text about research.")
    results.append("FAIL  summarize_text — should raise RuntimeError on API failure")
except RuntimeError as e:
    assert "IBM Granite API call failed" in str(e)
    results.append(f'PASS  API failure wrapped as RuntimeError: "{str(e)[:60]}..."')
finally:
    FakeModelInference._should_fail = False

# Test 9: prompt builder contains all five section labels
prompt = _build_summary_prompt("sample text")
for label in ["Objective:", "Methodology:", "Key Findings:", "Limitations:", "Conclusion:"]:
    assert label in prompt, f"Missing label in prompt: {label}"
results.append("PASS  prompt template contains all five section labels")

# ── Report ────────────────────────────────────────────────────────────────────
print()
print(f"Python {sys.version}")
print()
for r in results:
    prefix = "  OK" if r.startswith("PASS") else "  !!"
    print(f"{prefix}  {r}")

failed = [r for r in results if r.startswith("FAIL")]
print()
if failed:
    print(f"{len(failed)} test(s) FAILED.")
    sys.exit(1)
else:
    print(f"All {len(results)} tests passed.")
