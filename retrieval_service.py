from fastapi import FastAPI
from retrieve import retrieve

app = FastAPI(title="Retrieval Service")


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/retrieve")
def retrieve_endpoint(query: str):
    filename, document, score = retrieve(query)

    return {
        "query": query,
        "source_document": filename,
        "similarity_score": round(float(score), 4),
        "context": document
    }
