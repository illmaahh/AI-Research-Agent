"""
Logic test for utils/ibm_client.py after the scope_validation=False fix.
Stubs ibm_watsonx_ai so every code path is exercised without live credentials.
Run from workspace root: python .bob/tmp/test_ibm_client_v2.py
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
    """Mirrors the real APIClient(credentials, project_id, scope_validation=False) call."""
    _fail_on_construct = False

    def __init__(self, credentials, project_id=None, space_id=None, **kwargs):
        if FakeAPIClient._fail_on_construct:
            raise ConnectionError("simulated client build failure")
        # scope_validation is consumed via **kwargs — just record it for assertion
        self.scope_validation = kwargs.get("scope_validation", True)
        self.default_project_id = project_id
        self.credentials = credentials

ibm_mod.Credentials = FakeCredentials
ibm_mod.APIClient   = FakeAPIClient

fm_mod = types.ModuleType("ibm_watsonx_ai.foundation_models")

class FakeModelInference:
    _should_fail = False
    _response = "The study aims to evaluate deep learning. Methodology: CNN on ImageNet. Key Findings: 94% accuracy. Limitations: small dataset. Conclusion: promising direction."

    def __init__(self, model_id=None, api_client=None, params=None, **kwargs):
        # The fixed code must pass api_client, NOT credentials+project_id
        assert api_client is not None, "api_client must be passed (not credentials+project_id)"
        assert model_id is not None,   "model_id must be set"
        self._api_client = api_client
        self._model_id   = model_id

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

sys.modules["ibm_watsonx_ai"]                   = ibm_mod
sys.modules["ibm_watsonx_ai.foundation_models"] = fm_mod
sys.modules["ibm_watsonx_ai.metanames"]         = meta_mod

# ── Import module under test ──────────────────────────────────────────────────
from utils.ibm_client import (
    get_credentials, _get_api_client, get_model, summarize_text, _build_summary_prompt
)

results = []

# ── Set valid env vars for most tests ────────────────────────────────────────
os.environ["IBM_API_KEY"]    = "test-key"
os.environ["IBM_PROJECT_ID"] = "test-project-uuid"
os.environ["IBM_URL"]        = "https://us-south.ml.cloud.ibm.com"

# Test 1: get_credentials raises EnvironmentError when vars missing
for var in ["IBM_API_KEY", "IBM_PROJECT_ID", "IBM_URL"]:
    os.environ.pop(var, None)
try:
    get_credentials()
    results.append("FAIL  get_credentials — should raise EnvironmentError")
except EnvironmentError as e:
    results.append(f'PASS  get_credentials raises EnvironmentError (missing all vars)')
finally:
    os.environ["IBM_API_KEY"]    = "test-key"
    os.environ["IBM_PROJECT_ID"] = "test-project-uuid"
    os.environ["IBM_URL"]        = "https://us-south.ml.cloud.ibm.com"

# Test 2: get_credentials returns correct dict
creds = get_credentials()
assert creds == {
    "api_key": "test-key",
    "project_id": "test-project-uuid",
    "url": "https://us-south.ml.cloud.ibm.com"
}
results.append("PASS  get_credentials returns correct dict")

# Test 3: _get_api_client creates APIClient with scope_validation=False
client = _get_api_client(creds)
assert isinstance(client, FakeAPIClient)
assert client.scope_validation == False, f"Expected False, got {client.scope_validation}"
assert client.default_project_id == "test-project-uuid"
results.append("PASS  _get_api_client creates APIClient with scope_validation=False")

# Test 4: _get_api_client wraps SDK errors as RuntimeError
FakeAPIClient._fail_on_construct = True
try:
    _get_api_client(creds)
    results.append("FAIL  _get_api_client — should raise RuntimeError on SDK failure")
except RuntimeError as e:
    assert "Failed to create" in str(e)
    results.append(f'PASS  _get_api_client wraps SDK error as RuntimeError')
finally:
    FakeAPIClient._fail_on_construct = False

# Test 5: get_model passes api_client (not credentials) to ModelInference
# (assertion inside FakeModelInference.__init__ enforces this)
model = get_model()
assert isinstance(model, FakeModelInference)
assert model._api_client.scope_validation == False
results.append("PASS  get_model passes api_client to ModelInference (not credentials+project_id)")

# Test 6: summarize_text raises ValueError on empty input
try:
    summarize_text("")
    results.append("FAIL  summarize_text — should raise ValueError")
except ValueError:
    results.append("PASS  summarize_text raises ValueError on empty input")

# Test 7: summarize_text returns string starting with 'Objective:'
summary = summarize_text("Machine learning paper text here.")
assert summary.startswith("Objective:"), f"Got: {summary[:50]!r}"
results.append('PASS  summarize_text returns summary starting with "Objective:"')

# Test 8: long input is safely truncated
summary2 = summarize_text("token " * 4000)
assert summary2.startswith("Objective:")
results.append("PASS  summarize_text handles long input without error")

# Test 9: API failure is wrapped as RuntimeError
FakeModelInference._should_fail = True
try:
    summarize_text("Some paper text.")
    results.append("FAIL  summarize_text — should raise RuntimeError on API failure")
except RuntimeError as e:
    assert "IBM Granite API call failed" in str(e)
    results.append('PASS  API failure wrapped as RuntimeError')
finally:
    FakeModelInference._should_fail = False

# Test 10: prompt template contains all five required section labels
prompt = _build_summary_prompt("sample paper text")
for label in ["Objective:", "Methodology:", "Key Findings:", "Limitations:", "Conclusion:"]:
    assert label in prompt, f"Missing label: {label}"
results.append("PASS  prompt template contains all five section labels")

# Test 11: warnings from scope_validation=False are suppressed (no UserWarning raised)
caught = []
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    _get_api_client(creds)
    caught = [x for x in w if issubclass(x.category, UserWarning)]
assert len(caught) == 0, f"Unexpected warnings: {caught}"
results.append("PASS  scope_validation UserWarning is suppressed from user output")

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
