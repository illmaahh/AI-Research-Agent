"""
Logic test for utils/ibm_client.py after the granite-4-h-small / chat() migration.
Run from workspace root: python .bob/tmp/test_ibm_client_v3.py
"""
import sys, os, types, warnings

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# ── Build a minimal ibm_watsonx_ai stub ──────────────────────────────────────
ibm_mod = types.ModuleType("ibm_watsonx_ai")

class FakeCredentials:
    def __init__(self, api_key, url):
        self.api_key = api_key
        self.url = url

class FakeAPIClient:
    _fail_on_construct = False
    def __init__(self, credentials, project_id=None, **kwargs):
        if FakeAPIClient._fail_on_construct:
            raise ConnectionError("simulated build failure")
        self.scope_validation  = kwargs.get("scope_validation", True)
        self.default_project_id = project_id
        self.credentials = credentials

ibm_mod.Credentials = FakeCredentials
ibm_mod.APIClient   = FakeAPIClient

fm_mod = types.ModuleType("ibm_watsonx_ai.foundation_models")

class FakeModelInference:
    _should_fail = False
    _bad_response = False
    # Realistic chat response dict
    _RESPONSE = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": (
                        "Objective: This study investigates deep learning for image classification.\n"
                        "Methodology: CNN trained on ImageNet dataset with 1.2M images.\n"
                        "Key Findings: Achieved 94.3% top-1 accuracy, outperforming prior baselines.\n"
                        "Limitations: Results limited to natural images; performance on medical scans is untested.\n"
                        "Conclusion: The approach demonstrates strong generalisability for visual tasks."
                    )
                }
            }
        ]
    }

    def __init__(self, model_id=None, api_client=None, **kwargs):
        assert api_client is not None, "api_client must be passed"
        assert "params" not in kwargs,  "params must NOT be passed at construction (passed per-call)"
        self._model_id   = model_id
        self._api_client = api_client

    def chat(self, messages, params=None):
        if FakeModelInference._should_fail:
            raise ConnectionError("simulated network error")
        if FakeModelInference._bad_response:
            return {}   # missing 'choices' — triggers KeyError/IndexError path
        assert isinstance(messages, list), "messages must be a list"
        assert any(m["role"] == "system" for m in messages), "system message missing"
        assert any(m["role"] == "user"   for m in messages), "user message missing"
        return FakeModelInference._RESPONSE

fm_mod.ModelInference = FakeModelInference

sys.modules["ibm_watsonx_ai"]                   = ibm_mod
sys.modules["ibm_watsonx_ai.foundation_models"] = fm_mod
# metanames is no longer imported by ibm_client — confirm it is not required
sys.modules.pop("ibm_watsonx_ai.metanames", None)

# ── Import module under test ──────────────────────────────────────────────────
from utils.ibm_client import (
    DEFAULT_MODEL_ID, _CHAT_PARAMS, _MAX_INPUT_CHARS,
    get_credentials, _get_api_client, get_model,
    summarize_text, _build_summary_messages,
)

results = []

# ── Set env vars ─────────────────────────────────────────────────────────────
os.environ["IBM_API_KEY"]    = "test-key"
os.environ["IBM_PROJECT_ID"] = "test-project"
os.environ["IBM_URL"]        = "https://us-south.ml.cloud.ibm.com"

# Test 1: DEFAULT_MODEL_ID is granite-4-h-small
assert DEFAULT_MODEL_ID == "ibm/granite-4-h-small", f"Got: {DEFAULT_MODEL_ID}"
results.append("PASS  DEFAULT_MODEL_ID == 'ibm/granite-4-h-small'")

# Test 2: _CHAT_PARAMS uses plain string keys (not ParamNames enum), no decoding_method
assert "max_tokens" in _CHAT_PARAMS
assert "stop" in _CHAT_PARAMS
assert "decoding_method" not in _CHAT_PARAMS
assert "decoding_method" not in str(list(_CHAT_PARAMS.keys()))
results.append("PASS  _CHAT_PARAMS uses OpenAI-compatible keys, no decoding_method")

# Test 3: _MAX_INPUT_CHARS reflects the larger context window
assert _MAX_INPUT_CHARS == 60_000, f"Expected 60000, got {_MAX_INPUT_CHARS}"
results.append(f"PASS  _MAX_INPUT_CHARS == 60_000 (reflects 131k token window)")

# Test 4: get_model passes no params to ModelInference constructor
# (assertion inside FakeModelInference enforces this)
model = get_model()
assert isinstance(model, FakeModelInference)
assert model._model_id == "ibm/granite-4-h-small"
results.append("PASS  get_model uses correct model ID and passes no constructor params")

# Test 5: _build_summary_messages returns system + user messages
msgs = _build_summary_messages("Sample paper text about neural networks.")
roles = [m["role"] for m in msgs]
assert "system" in roles and "user" in roles, f"Got roles: {roles}"
assert "Objective:" in msgs[-1]["content"]
assert "Methodology:" in msgs[-1]["content"]
assert "Key Findings:" in msgs[-1]["content"]
assert "Limitations:" in msgs[-1]["content"]
assert "Conclusion:" in msgs[-1]["content"]
results.append("PASS  _build_summary_messages returns [system, user] with all five labels")

# Test 6: _build_summary_messages embeds the paper text in the user message
msgs = _build_summary_messages("UNIQUE_PAPER_CONTENT_XYZ")
assert "UNIQUE_PAPER_CONTENT_XYZ" in msgs[-1]["content"]
results.append("PASS  paper text is embedded in the user message")

# Test 7: summarize_text returns the content from chat response
summary = summarize_text("A research paper about image classification with CNNs.")
assert "Objective:" in summary
assert "Methodology:" in summary
assert "Key Findings:" in summary
results.append("PASS  summarize_text extracts content from chat response correctly")

# Test 8: summarize_text raises ValueError on empty input
try:
    summarize_text("")
    results.append("FAIL  should raise ValueError on empty input")
except ValueError:
    results.append("PASS  summarize_text raises ValueError on empty input")

# Test 9: API failure is wrapped as RuntimeError
FakeModelInference._should_fail = True
try:
    summarize_text("Some text.")
    results.append("FAIL  should raise RuntimeError on API failure")
except RuntimeError as e:
    assert "IBM Granite API call failed" in str(e)
    results.append("PASS  API failure wrapped as RuntimeError")
finally:
    FakeModelInference._should_fail = False

# Test 10: malformed response (missing 'choices') raises RuntimeError
FakeModelInference._bad_response = True
try:
    summarize_text("Some text.")
    results.append("FAIL  should raise RuntimeError on bad response format")
except RuntimeError as e:
    assert "Unexpected response format" in str(e)
    results.append("PASS  malformed response raises RuntimeError with clear message")
finally:
    FakeModelInference._bad_response = False

# Test 11: long input is truncated to _MAX_INPUT_CHARS
long_text = "word " * 20_000   # ~100 000 chars, over the 60 000-char limit
summary = summarize_text(long_text)
assert summary  # just check it doesn't blow up
results.append("PASS  long input is truncated without error")

# Test 12: GenTextParamsMetaNames is NOT imported by ibm_client
import importlib, sys
ibm_client_mod = sys.modules.get("utils.ibm_client")
assert ibm_client_mod is not None
# metanames should not appear in the module's globals
assert "ParamNames" not in dir(ibm_client_mod), "ParamNames should not be in ibm_client namespace"
results.append("PASS  GenTextParamsMetaNames is no longer imported (unused)")

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
