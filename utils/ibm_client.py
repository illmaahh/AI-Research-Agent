"""
utils/ibm_client.py

Responsibility: IBM watsonx.ai client construction and all AI inference.

This is the single place that imports ibm_watsonx_ai.  Nothing outside
this file should instantiate ModelInference or touch credentials directly.

Public API
----------
get_credentials() -> dict[str, str]
    Reads IBM_API_KEY, IBM_PROJECT_ID, IBM_URL from the environment.
    Raises EnvironmentError if any variable is missing or blank.

get_model(model_id: str) -> ModelInference
    Returns a configured ModelInference instance ready for inference.
    Raises EnvironmentError (missing creds) or RuntimeError (SDK error).

summarize_text(text: str) -> str
    12-section expanded academic summary via IBM Granite chat API.

answer_question(question: str, chunks: list[RetrievedChunk]) -> AnswerResult
    RAG-grounded answer with confidence and source attribution.

extract_citations(text: str) -> CitationResult
    Extract metadata and format IEEE, APA, MLA, and BibTeX citations.

generate_insights(text: str) -> InsightResult
    Keyword, domain, gaps, contributions, strengths/weaknesses analysis.

Configuration (.env)
---------------------
IBM_API_KEY    = <your IBM Cloud API key>
IBM_PROJECT_ID = <your watsonx.ai project ID>
IBM_URL        = https://us-south.ml.cloud.ibm.com  (or your region)

Why scope_validation=False?
----------------------------
When ModelInference is initialised with only (credentials, project_id), the
SDK internally calls APIClient.set.default_project(), which makes a GET
request to the Projects API and verifies that the project has a Watson
Machine Learning (WML) service instance associated with it.

IBM Cloud Lite / IBM SkillsBuild accounts access the WML runtime through the
shared watsonx.ai platform service rather than a separately-provisioned WML
instance, so this association check returns HTTP 403:
    no_associated_service_instance_error

The correct fix is to construct APIClient ourselves with scope_validation=False.
This bypasses the pre-flight service-association check while leaving every
other API call (authentication, text generation) completely unaffected.
The same approach is documented in the IBM watsonx.ai SDK source and used by
the official IBM SkillsBuild notebook examples.
"""

from __future__ import annotations

import json
import os
import textwrap
import warnings
from dataclasses import dataclass, field

from dotenv import load_dotenv
from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference

# Load .env once at import time so every function sees the variables.
load_dotenv()

# ─── Model selection ─────────────────────────────────────────────────────────
# granite-4-h-small is a 30B-parameter long-context instruct/chat model.
# It supports text_generation and text_chat functions, with a 131 072-token
# context window. The previous model (granite-13b-instruct-v2) is no longer
# available on IBM Cloud.
DEFAULT_MODEL_ID = "ibm/granite-4-h-small"

# ─── Context-window budget ───────────────────────────────────────────────────
# granite-4-h-small has a 131 072-token context window.  We cap input at
# ~60 000 characters (~15 000 tokens at ~4 chars/token) to leave ample room
# for the system prompt and the 512-token output, while still being generous
# enough to cover most research-paper abstracts + introductions in full.
_MAX_INPUT_CHARS = 60_000

# ─── Chat inference parameters ───────────────────────────────────────────────
# granite-4-h-small is a chat model: use the /ml/v1/text/chat endpoint.
# The older /ml/v1/text/generation endpoint is deprecated for chat models.
# decoding_method is ignored and set automatically by the API.
_CHAT_PARAMS: dict = {
    "max_tokens": 700,
    "stop":       ["---", "###"],
}

_LONG_CHAT_PARAMS: dict = {   # for summary / insights which need more tokens
    "max_tokens": 1200,
    "stop":       ["---"],
}


# ─── Result data-classes ─────────────────────────────────────────────────────

@dataclass
class AnswerResult:
    """Structured result returned by answer_question()."""
    answer:      str                  # The generated answer text
    confidence:  str                  # "High" | "Medium" | "Low"
    pages:       list[int]            # Source page numbers (deduplicated)
    chunks:      list                 # The RetrievedChunk objects used
    not_found:   bool = False         # True when the answer isn't in the paper


@dataclass
class CitationResult:
    """Structured result returned by extract_citations()."""
    title:      str = ""
    authors:    str = ""
    year:       str = ""
    journal:    str = ""
    doi:        str = ""
    publisher:  str = ""
    ieee:       str = ""
    apa:        str = ""
    mla:        str = ""
    bibtex:     str = ""
    raw:        str = ""             # raw model output (fallback display)


@dataclass
class InsightResult:
    """Structured result returned by generate_insights()."""
    keywords:         list[str] = field(default_factory=list)
    domain:           str = ""
    future_directions: list[str] = field(default_factory=list)
    research_gaps:    list[str] = field(default_factory=list)
    contributions:    list[str] = field(default_factory=list)
    strengths:        list[str] = field(default_factory=list)
    weaknesses:       list[str] = field(default_factory=list)
    improvements:     list[str] = field(default_factory=list)
    raw:              str = ""       # raw model output (fallback display)


# ─────────────────────────────────────────────────────────────────────────────
# Credentials
# ─────────────────────────────────────────────────────────────────────────────

def get_credentials() -> dict[str, str]:
    """
    Read IBM Cloud credentials from environment variables.

    Required variables (set in .env or the OS environment):
        IBM_API_KEY    — IBM Cloud API key
        IBM_PROJECT_ID — watsonx.ai project ID
        IBM_URL        — Regional endpoint, e.g.
                         https://us-south.ml.cloud.ibm.com

    Returns:
        {'api_key': ..., 'project_id': ..., 'url': ...}

    Raises:
        EnvironmentError: If any variable is missing or empty.
    """
    required = {
        "api_key":    "IBM_API_KEY",
        "project_id": "IBM_PROJECT_ID",
        "url":        "IBM_URL",
    }

    creds: dict[str, str] = {}
    missing: list[str] = []

    for field, env_var in required.items():
        value = os.getenv(env_var, "").strip()
        if not value:
            missing.append(env_var)
        else:
            creds[field] = value

    if missing:
        raise EnvironmentError(
            f"Missing required environment variable(s): {', '.join(missing)}. "
            "Create a .env file in the project root with these keys — "
            "see .env.example for the expected format."
        )

    return creds


# ─────────────────────────────────────────────────────────────────────────────
# API client factory
# ─────────────────────────────────────────────────────────────────────────────

def _get_api_client(creds: dict[str, str]) -> APIClient:
    """
    Build and return an APIClient with scope_validation disabled.

    IBM Cloud Lite / SkillsBuild accounts do not have a standalone WML service
    instance associated with their watsonx.ai projects; the runtime is provided
    by the shared platform.  The default scope_validation=True causes the SDK
    to pre-flight check this association and raises HTTP 403
    (no_associated_service_instance_error) even though text generation itself
    works fine.

    Passing scope_validation=False skips that GET /projects/{id} validation
    call and sets default_project_id directly on the client, so every
    subsequent API call — including text generation — proceeds normally.

    Args:
        creds: Dict returned by get_credentials().

    Returns:
        A configured APIClient instance with the project ID already set.

    Raises:
        RuntimeError: If the SDK raises during client construction.
    """
    try:
        # Suppress the UserWarning that scope_validation=False emits;
        # it's an internal SDK advisory, not relevant to our users.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            client = APIClient(
                credentials=Credentials(
                    api_key=creds["api_key"],
                    url=creds["url"],
                ),
                project_id=creds["project_id"],
                scope_validation=False,     # bypass WML service-association check
            )
        return client
    except Exception as exc:
        raise RuntimeError(
            f"Failed to create IBM watsonx.ai API client: {exc}"
        ) from exc


# ─────────────────────────────────────────────────────────────────────────────
# Model factory
# ─────────────────────────────────────────────────────────────────────────────

def get_model(model_id: str = DEFAULT_MODEL_ID) -> ModelInference:
    """
    Instantiate and return a ModelInference object ready for inference.

    The client is constructed first (scope_validation=False) and passed
    directly to ModelInference via the api_client parameter.  This avoids the
    second call to set.default_project() that ModelInference would otherwise
    make when given raw credentials, which would re-trigger the 403 error.

    Args:
        model_id: A valid watsonx.ai model identifier string.
                  Defaults to ``DEFAULT_MODEL_ID``.

    Returns:
        A configured ``ModelInference`` instance (no params set here;
        params are passed per-call in summarize_text so the model object
        remains reusable for other call sites with different param needs).

    Raises:
        EnvironmentError: If credentials are missing from the environment.
        RuntimeError: If the SDK raises during object construction.
    """
    creds = get_credentials()  # raises EnvironmentError if incomplete
    client = _get_api_client(creds)

    try:
        return ModelInference(
            model_id=model_id,
            api_client=client,   # pre-built client; skips internal set.default_project()
        )
    except Exception as exc:
        raise RuntimeError(
            f"Failed to initialise IBM Granite model '{model_id}': {exc}"
        ) from exc


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _chat(messages: list[dict], params: dict | None = None) -> str:
    """
    Call the IBM Granite chat API and return the assistant content string.

    Centralises error handling so every public function has a single call site.

    Args:
        messages: OpenAI-compatible message list.
        params:   Chat parameters dict (defaults to _CHAT_PARAMS).

    Returns:
        The assistant's reply as a stripped string.

    Raises:
        EnvironmentError: If credentials are missing.
        RuntimeError:     On any API / network / format error.
    """
    model = get_model()
    p = params if params is not None else _CHAT_PARAMS
    try:
        response: dict = model.chat(messages=messages, params=p)
        return response["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError) as exc:
        raise RuntimeError(f"Unexpected response format from IBM Granite: {exc}") from exc
    except Exception as exc:
        raise RuntimeError(f"IBM Granite API call failed: {exc}") from exc


def _truncate(text: str, max_chars: int = _MAX_INPUT_CHARS) -> str:
    """Truncate text to max_chars and append a continuation note if cut."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[... document continues — excerpt shown above ...]"


# ─────────────────────────────────────────────────────────────────────────────
# Summarisation
# ─────────────────────────────────────────────────────────────────────────────

def summarize_text(text: str) -> str:
    """
    Generate a 12-section expanded academic summary using IBM Granite.

    Sections: Research Objective · Background · Methodology · Dataset ·
    Models/Algorithms · Experimental Setup · Key Findings · Results ·
    Limitations · Future Work · Practical Applications · Conclusion.

    Args:
        text: Full extracted text from the research paper.

    Returns:
        Raw summary string with labelled sections.

    Raises:
        ValueError:       If text is empty.
        EnvironmentError: If IBM credentials are missing.
        RuntimeError:     On API failure.
    """
    if not text or not text.strip():
        raise ValueError("Cannot summarise empty text.")

    input_text = _truncate(text)

    system = (
        "You are an expert academic research assistant. "
        "Read the research paper and produce a precise, structured summary "
        "for academic audiences. Do not hallucinate. If a section has no "
        "relevant content in the paper, write 'Not specified'."
    )

    user = textwrap.dedent(f"""
        Read the research paper excerpt and write a structured academic summary.

        Your response MUST contain exactly these 12 sections, each on its own
        line starting with the label shown. Do not add preamble or extra text.

        Research Objective: <what the paper aims to achieve>
        Background: <prior work and motivation>
        Methodology: <research approach, techniques, and frameworks>
        Dataset: <data used, size, source>
        Models/Algorithms: <specific models or algorithms employed>
        Experimental Setup: <hardware, software, evaluation metrics>
        Key Findings: <most important results>
        Results: <quantitative outcomes, tables, metrics>
        Limitations: <acknowledged weaknesses>
        Future Work: <suggested next steps by the authors>
        Practical Applications: <real-world use cases>
        Conclusion: <overall significance>

        Rules:
        - Do not copy sentences verbatim.
        - Be precise and academic in tone.
        - Start directly with "Research Objective:" — no preamble.

        --- PAPER EXCERPT ---
        {input_text}
        --- END ---
    """).strip()

    return _chat(
        [{"role": "system", "content": system},
         {"role": "user",   "content": user}],
        params=_LONG_CHAT_PARAMS,
    )


# ─────────────────────────────────────────────────────────────────────────────
# RAG Question Answering
# ─────────────────────────────────────────────────────────────────────────────

def answer_question(question: str, chunks: list) -> "AnswerResult":
    """
    Answer a research question using RAG-retrieved context chunks.

    The model is instructed to answer ONLY from the provided context and to
    explicitly say when the answer cannot be found — preventing hallucination.

    Args:
        question: The user's natural-language question.
        chunks:   List of RetrievedChunk objects from vector_store.query_store().

    Returns:
        AnswerResult with answer text, confidence, source pages, and chunks.

    Raises:
        ValueError:       If question or chunks are empty.
        EnvironmentError: If IBM credentials are missing.
        RuntimeError:     On API failure.
    """
    if not question or not question.strip():
        raise ValueError("Question must not be empty.")
    if not chunks:
        raise ValueError("No context chunks provided.")

    # Build the context block with page attribution for each chunk
    context_parts = []
    for i, chunk in enumerate(chunks):
        context_parts.append(
            f"[Context {i+1} | Page {chunk.page_number}]\n{chunk.text}"
        )
    context_block = "\n\n".join(context_parts)

    system = (
        "You are an expert research assistant answering questions about an "
        "academic paper. You MUST answer ONLY using the provided context. "
        "If the answer is not found in the context, reply with exactly: "
        "'NOT_FOUND: The answer to this question is not available in the "
        "uploaded document.' Do not guess or use outside knowledge."
    )

    user = textwrap.dedent(f"""
        Answer the following question using ONLY the context below.

        QUESTION: {question}

        CONTEXT:
        {context_block}

        Instructions:
        - Answer concisely and accurately.
        - Cite which context number(s) you used.
        - If the answer is not in the context, start with NOT_FOUND:
    """).strip()

    raw = _chat(
        [{"role": "system", "content": system},
         {"role": "user",   "content": user}],
    )

    not_found = raw.upper().startswith("NOT_FOUND")

    # Compute overall confidence from the best-scoring chunk
    best_score = min(c.score for c in chunks) if chunks else 1.0
    if best_score < 0.5:
        confidence = "High"
    elif best_score < 1.0:
        confidence = "Medium"
    else:
        confidence = "Low"

    pages = sorted({c.page_number for c in chunks if c.page_number})

    return AnswerResult(
        answer=raw,
        confidence=confidence,
        pages=pages,
        chunks=chunks,
        not_found=not_found,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Citation extraction
# ─────────────────────────────────────────────────────────────────────────────

def extract_citations(text: str) -> "CitationResult":
    """
    Extract bibliographic metadata and format four citation styles.

    Sends the first 4 000 characters of the paper (title page / header area)
    to IBM Granite and asks for structured JSON metadata, then formats it.

    Args:
        text: Full extracted text from the research paper.

    Returns:
        CitationResult with IEEE, APA, MLA, and BibTeX strings.

    Raises:
        ValueError:       If text is empty.
        EnvironmentError: If IBM credentials are missing.
        RuntimeError:     On API failure.
    """
    if not text or not text.strip():
        raise ValueError("Cannot extract citations from empty text.")

    # Use just the first portion — metadata is almost always on the title page
    excerpt = text[:4000]

    system = (
        "You are an expert academic librarian. Extract bibliographic metadata "
        "from the research paper header and return ONLY valid JSON. "
        "Use empty string for any field not found. Do not add explanation."
    )

    user = textwrap.dedent(f"""
        Extract metadata from this research paper header and return ONLY this
        JSON object (no markdown, no explanation):

        {{
          "title": "",
          "authors": "",
          "year": "",
          "journal": "",
          "doi": "",
          "publisher": "",
          "volume": "",
          "issue": "",
          "pages": ""
        }}

        PAPER HEADER:
        {excerpt}
    """).strip()

    raw = _chat(
        [{"role": "system", "content": system},
         {"role": "user",   "content": user}],
    )

    # ── Parse the JSON response ───────────────────────────────────────────────
    meta: dict = {}
    try:
        # Strip any accidental markdown fences
        clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        meta = json.loads(clean)
    except (json.JSONDecodeError, ValueError):
        # Fall back to empty metadata if parsing fails
        meta = {}

    title     = meta.get("title", "").strip()
    authors   = meta.get("authors", "").strip()
    year      = meta.get("year", "").strip()
    journal   = meta.get("journal", "").strip()
    doi       = meta.get("doi", "").strip()
    publisher = meta.get("publisher", "").strip()
    volume    = meta.get("volume", "").strip()
    issue     = meta.get("issue", "").strip()
    pages     = meta.get("pages", "").strip()

    doi_str = f" doi: {doi}" if doi else ""

    # ── IEEE ──────────────────────────────────────────────────────────────────
    author_list = [a.strip() for a in authors.split(",") if a.strip()]
    ieee_authors = ", ".join(
        f"{a.split()[-1]}, {' '.join(x[0] + '.' for x in a.split()[:-1])}"
        if len(a.split()) > 1 else a
        for a in author_list[:3]
    )
    if len(author_list) > 3:
        ieee_authors += " et al."
    vol_issue = f", vol. {volume}" if volume else ""
    if issue:
        vol_issue += f", no. {issue}"
    pp = f", pp. {pages}" if pages else ""
    ieee = f'{ieee_authors}, "{title}," {journal}{vol_issue}{pp}, {year}.{doi_str}'.strip(", .")

    # ── APA 7th ───────────────────────────────────────────────────────────────
    apa_authors = authors if authors else "Unknown Author"
    apa = f"{apa_authors} ({year}). {title}. {journal}"
    if volume:
        apa += f", {volume}"
    if issue:
        apa += f"({issue})"
    if pages:
        apa += f", {pages}"
    apa += "."
    if doi:
        apa += f" https://doi.org/{doi}"

    # ── MLA ───────────────────────────────────────────────────────────────────
    mla_authors = authors if authors else "Unknown Author"
    mla = f'{mla_authors}. "{title}." {journal}'
    if volume:
        mla += f", vol. {volume}"
    if issue:
        mla += f", no. {issue}"
    mla += f", {year}"
    if pages:
        mla += f", pp. {pages}"
    mla += "."

    # ── BibTeX ────────────────────────────────────────────────────────────────
    key = (authors.split(",")[0].split()[-1] if authors else "Author") + year
    bibtex = textwrap.dedent(f"""
        @article{{{key},
          title   = {{{title}}},
          author  = {{{authors}}},
          journal = {{{journal}}},
          year    = {{{year}}},
          volume  = {{{volume}}},
          number  = {{{issue}}},
          pages   = {{{pages}}},
          doi     = {{{doi}}}
        }}
    """).strip()

    return CitationResult(
        title=title, authors=authors, year=year,
        journal=journal, doi=doi, publisher=publisher,
        ieee=ieee, apa=apa, mla=mla, bibtex=bibtex,
        raw=raw,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Research insights
# ─────────────────────────────────────────────────────────────────────────────

def generate_insights(text: str) -> "InsightResult":
    """
    Generate AI research insights including keywords, gaps, and contributions.

    Args:
        text: Full extracted text from the research paper.

    Returns:
        InsightResult with structured analysis lists.

    Raises:
        ValueError:       If text is empty.
        EnvironmentError: If IBM credentials are missing.
        RuntimeError:     On API failure.
    """
    if not text or not text.strip():
        raise ValueError("Cannot generate insights from empty text.")

    input_text = _truncate(text, max_chars=30_000)

    system = (
        "You are an expert academic researcher analysing a research paper. "
        "Return ONLY valid JSON. No markdown, no explanation outside the JSON."
    )

    user = textwrap.dedent(f"""
        Analyse the research paper and return ONLY this JSON object:

        {{
          "keywords": ["kw1", "kw2", ...],
          "domain": "main research domain",
          "future_directions": ["direction 1", ...],
          "research_gaps": ["gap 1", ...],
          "contributions": ["contribution 1", ...],
          "strengths": ["strength 1", ...],
          "weaknesses": ["weakness 1", ...],
          "improvements": ["improvement 1", ...]
        }}

        Each list should have 3–6 items. Be specific and academic.

        PAPER:
        {input_text}
    """).strip()

    raw = _chat(
        [{"role": "system", "content": system},
         {"role": "user",   "content": user}],
        params=_LONG_CHAT_PARAMS,
    )

    meta: dict = {}
    try:
        clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        meta  = json.loads(clean)
    except (json.JSONDecodeError, ValueError):
        meta = {}

    def _list(key: str) -> list[str]:
        val = meta.get(key, [])
        return val if isinstance(val, list) else []

    return InsightResult(
        keywords=_list("keywords"),
        domain=meta.get("domain", ""),
        future_directions=_list("future_directions"),
        research_gaps=_list("research_gaps"),
        contributions=_list("contributions"),
        strengths=_list("strengths"),
        weaknesses=_list("weaknesses"),
        improvements=_list("improvements"),
        raw=raw,
    )
