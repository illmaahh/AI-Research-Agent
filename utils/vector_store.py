"""
utils/vector_store.py

Responsibility: Build and query the RAG vector index for a research paper.

Pipeline:
  1. Split page text into overlapping character-level chunks.
  2. Embed each chunk via IBM granite-embedding-278m-multilingual.
  3. Index chunks in an in-memory FAISS store (no disk I/O needed).
  4. Retrieve the top-k most semantically relevant chunks for any query.

Public API
----------
build_vector_store(pages: list[PageChunk]) -> FAISS
    Chunks, embeds, and indexes all pages.  Returns the FAISS store.

query_store(store: FAISS, question: str, k: int) -> list[RetrievedChunk]
    Semantic search; returns ranked RetrievedChunk objects with metadata.

get_embeddings_model() -> IBMEmbeddingsAdapter
    Returns a configured LangChain-compatible embedding object.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings as LCEmbeddings

from utils.ibm_client import _get_api_client, get_credentials

# ─── Embedding model ──────────────────────────────────────────────────────────
EMBEDDING_MODEL_ID = "ibm/granite-embedding-278m-multilingual"

# ─── Chunking parameters ─────────────────────────────────────────────────────
# Chunk size and overlap are in characters.
# ~1 000 chars ≈ 200–250 tokens, well within the embedding model's limit.
# 200-char overlap preserves sentence context across chunk boundaries.
_CHUNK_SIZE    = 1_000
_CHUNK_OVERLAP = 200


# ─── Data model ──────────────────────────────────────────────────────────────

@dataclass
class RetrievedChunk:
    """A single retrieved chunk with its relevance metadata."""
    text:        str    # chunk content
    page_number: int    # 1-based page number this chunk came from
    chunk_index: int    # position of this chunk within the page
    score:       float  # L2 distance (lower = more similar)

    @property
    def confidence(self) -> str:
        """
        Map L2 distance to a human-readable confidence label.

        Thresholds are calibrated empirically against
        granite-embedding-278m-multilingual 768-d vectors.
        """
        if self.score < 0.5:
            return "High"
        if self.score < 1.0:
            return "Medium"
        return "Low"


# ─── LangChain adapter ────────────────────────────────────────────────────────

class IBMEmbeddingsAdapter(LCEmbeddings):
    """
    Thin adapter that makes ``ibm_watsonx_ai.foundation_models.Embeddings``
    comply with the LangChain ``Embeddings`` interface.

    The IBM class has the right methods (``embed_query``, ``embed_documents``)
    but is not a subclass of ``langchain_core.embeddings.Embeddings``, which
    FAISS.from_texts() requires when validating the embedding function.
    """

    def __init__(self, ibm_embeddings) -> None:
        self._emb = ibm_embeddings

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of document strings."""
        return self._emb.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query string."""
        return self._emb.embed_query(text)


# ─── Public helpers ───────────────────────────────────────────────────────────

def get_embeddings_model() -> IBMEmbeddingsAdapter:
    """
    Construct and return a LangChain-compatible IBM embedding model.

    Reads credentials from the environment (same path as get_model).

    Returns:
        IBMEmbeddingsAdapter wrapping granite-embedding-278m-multilingual.

    Raises:
        EnvironmentError: If IBM credentials are missing.
        RuntimeError:     If the SDK raises during construction.
    """
    from ibm_watsonx_ai.foundation_models import Embeddings as IBMEmbeddings

    creds  = get_credentials()
    client = _get_api_client(creds)

    try:
        raw = IBMEmbeddings(
            model_id=EMBEDDING_MODEL_ID,
            api_client=client,
        )
    except Exception as exc:
        raise RuntimeError(
            f"Failed to initialise IBM embedding model '{EMBEDDING_MODEL_ID}': {exc}"
        ) from exc

    return IBMEmbeddingsAdapter(raw)


def build_vector_store(pages) -> FAISS:
    """
    Chunk, embed, and index all pages from a research paper.

    Each page is split into overlapping chunks.  Every chunk is stored in
    FAISS with metadata (page_number, chunk_index) so retrieval can report
    which page the evidence came from.

    Args:
        pages: list[PageChunk] — output of pdf_parser.extract_pages().

    Returns:
        A FAISS vector store ready for similarity_search_with_score().

    Raises:
        ValueError:       If pages is empty.
        EnvironmentError: If IBM credentials are missing.
        RuntimeError:     If embedding or FAISS construction fails.
    """
    if not pages:
        raise ValueError("Cannot build vector store from an empty page list.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=_CHUNK_SIZE,
        chunk_overlap=_CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""],
    )

    texts:     list[str]  = []
    metadatas: list[dict] = []

    for page in pages:
        page_chunks = splitter.split_text(page.text)
        for chunk_idx, chunk_text in enumerate(page_chunks):
            texts.append(chunk_text)
            metadatas.append({
                "page_number": page.page_number,
                "chunk_index": chunk_idx,
            })

    if not texts:
        raise ValueError("No text chunks produced — the document may be too short.")

    embeddings = get_embeddings_model()

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        store = FAISS.from_texts(texts, embeddings, metadatas=metadatas)

    return store


def query_store(
    store: FAISS,
    question: str,
    k: int = 4,
) -> list[RetrievedChunk]:
    """
    Retrieve the top-k most relevant chunks for ``question``.

    Args:
        store:    A FAISS store built by build_vector_store().
        question: The user's natural-language question.
        k:        Number of chunks to return (default 4).

    Returns:
        List of RetrievedChunk sorted by relevance (most relevant first).

    Raises:
        RuntimeError: If the similarity search fails.
    """
    if not question or not question.strip():
        raise ValueError("Question must not be empty.")

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            raw_results = store.similarity_search_with_score(question, k=k)
    except Exception as exc:
        raise RuntimeError(f"Vector store search failed: {exc}") from exc

    chunks: list[RetrievedChunk] = []
    for doc, score in raw_results:
        meta = doc.metadata or {}
        chunks.append(RetrievedChunk(
            text=doc.page_content,
            page_number=meta.get("page_number", 0),
            chunk_index=meta.get("chunk_index", 0),
            score=float(score),
        ))

    # Sort ascending by score (lower L2 = more similar)
    chunks.sort(key=lambda c: c.score)
    return chunks
