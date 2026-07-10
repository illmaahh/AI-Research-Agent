"""Probe: full FAISS round-trip with IBM granite-embedding-278m-multilingual."""
from dotenv import load_dotenv
load_dotenv()

import os, warnings
from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import Embeddings
from langchain_community.vectorstores import FAISS

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    client = APIClient(
        credentials=Credentials(api_key=os.environ["IBM_API_KEY"], url=os.environ["IBM_URL"]),
        project_id=os.environ["IBM_PROJECT_ID"],
        scope_validation=False,
    )

emb = Embeddings(model_id="ibm/granite-embedding-278m-multilingual", api_client=client)

texts = [
    "The transformer architecture revolutionized natural language processing.",
    "BERT uses bidirectional training with masked language modelling.",
    "GPT models are autoregressive and trained with next-token prediction.",
    "Attention mechanisms allow models to focus on relevant tokens.",
]
metadatas = [{"page": 1, "chunk": i} for i in range(len(texts))]

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    store = FAISS.from_texts(texts, emb, metadatas=metadatas)
    results = store.similarity_search_with_score("How does BERT work?", k=2)

print("Top-2 results for 'How does BERT work?':")
for doc, score in results:
    print(f"  score={score:.4f}  page={doc.metadata.get('page')}  text={doc.page_content[:70]!r}")

print()
print("FAISS round-trip OK")
