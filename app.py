from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from pathlib import Path
import json

import numpy as np
import requests
import psutil

from fastembed import TextEmbedding


app = FastAPI(title="Hybrid LLM Inference Assistant")


# =========================================================
# EXISTING SERVICE CONFIGURATION
# =========================================================

OLLAMA_URL = "http://localhost:11434/api/generate"
RETRIEVAL_SERVICE_URL = "http://localhost:8001/retrieve"
INFERENCE_SERVICE_URL = "http://localhost:8002/generate"

EMBEDDINGS_FILE = Path("knowledge_base/embeddings.json")

FRONTEND_DIR = Path("frontend")
FRONTEND_INDEX = FRONTEND_DIR / "index.html"


# =========================================================
# EXISTING EMBEDDING DATA
# =========================================================

data = json.loads(
    EMBEDDINGS_FILE.read_text(encoding="utf-8")
)

documents = data["documents"]

document_embeddings = np.array(
    data["embeddings"],
    dtype=np.float32
)

embedding_model = TextEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)


# =========================================================
# EXISTING RETRIEVAL LOGIC
# =========================================================

def cosine_similarity(a, b):
    return np.dot(a, b) / (
        np.linalg.norm(a) * np.linalg.norm(b)
    )


def retrieve_context(question):
    query_embedding = list(
        embedding_model.embed([question])
    )[0]

    query_vector = np.array(
        query_embedding,
        dtype=np.float32
    )

    scores = [
        cosine_similarity(
            query_vector,
            document_vector
        )
        for document_vector in document_embeddings
    ]

    best_index = int(np.argmax(scores))

    best_document = documents[best_index]

    return (
        best_document["filename"],
        best_document["text"],
        float(scores[best_index])
    )


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def home():
    return {
        "message": "Hybrid LLM Inference Assistant is running",
        "status": "ok"
    }


# =========================================================
# HTML FRONTEND
# =========================================================

@app.get("/ui")
def ui():
    return FileResponse(
        FRONTEND_INDEX,
        media_type="text/html"
    )


# =========================================================
# FRONTEND STATIC FILES
# =========================================================

@app.get("/frontend/styles.css")
def frontend_styles():
    return FileResponse(
        FRONTEND_DIR / "styles.css",
        media_type="text/css"
    )


@app.get("/frontend/app.js")
def frontend_javascript():
    return FileResponse(
        FRONTEND_DIR / "app.js",
        media_type="application/javascript"
    )


# =========================================================
# HEALTH
# =========================================================

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# =========================================================
# SYSTEM RESOURCE STATISTICS
# =========================================================

@app.get("/system-stats")
def system_stats():

    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()

    return {
        "cpu_percent": psutil.cpu_percent(interval=0.5),

        "memory": {
            "total_gb": round(
                memory.total / (1024 ** 3),
                2
            ),
            "used_gb": round(
                memory.used / (1024 ** 3),
                2
            ),
            "available_gb": round(
                memory.available / (1024 ** 3),
                2
            ),
            "percent": memory.percent
        },

        "swap": {
            "total_gb": round(
                swap.total / (1024 ** 3),
                2
            ),
            "used_gb": round(
                swap.used / (1024 ** 3),
                2
            ),
            "percent": swap.percent
        }
    }


# =========================================================
# EXISTING DIRECT OLLAMA ENDPOINT
# =========================================================

@app.get("/ask")
def ask(question: str):

    filename, context, similarity = retrieve_context(
        question
    )

    prompt = f"""Context:
{context[:8000]}

Question:
{question}

Answer:"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "codellama:7b-instruct",
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": 30,
                "temperature": 0
            }
        },
        timeout=600
    )

    response.raise_for_status()

    result = response.json()

    return {
        "question": question,
        "source_document": filename,
        "similarity_score": round(
            similarity,
            4
        ),
        "answer": result["response"]
    }


# =========================================================
# STREAMING SERVICE-BASED RAG ENDPOINT
# =========================================================

@app.get("/ask-services")
def ask_services(
    question: str,
    model: str = "phi3:mini"
):

    retrieval_response = requests.get(
        RETRIEVAL_SERVICE_URL,
        params={
            "query": question
        },
        timeout=60
    )

    retrieval_response.raise_for_status()

    retrieval_data = retrieval_response.json()

    context = retrieval_data["context"]

    prompt = f"""The following information is from the Kubernetes documentation.

Context:
{context[:8000]}

Question:
{question}

A concise and accurate answer based on the context is:"""

    inference_response = requests.get(
        INFERENCE_SERVICE_URL,
        params={
            "prompt": prompt,
            "model": model
        },
        stream=True,
        timeout=600
    )

    inference_response.raise_for_status()

    def generate_stream():
        try:
            for chunk in inference_response.iter_content(
                chunk_size=None,
                decode_unicode=True
            ):
                if chunk:
                    yield chunk
        finally:
            inference_response.close()

    return StreamingResponse(
        generate_stream(),
        media_type="text/plain"
    )
