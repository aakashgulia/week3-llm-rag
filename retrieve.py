from pathlib import Path
import json
import numpy as np
from fastembed import TextEmbedding

EMBEDDINGS_FILE = Path("knowledge_base/embeddings.json")

TOP_K = 3

data = json.loads(
    EMBEDDINGS_FILE.read_text(encoding="utf-8")
)

documents = data["documents"]

document_embeddings = np.array(
    data["embeddings"],
    dtype=np.float32
)

model = TextEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)


def cosine_similarity(a, b):
    return np.dot(a, b) / (
        np.linalg.norm(a) * np.linalg.norm(b)
    )


def retrieve(query):
    query_embedding = list(
        model.embed([query])
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

    ranked_indices = np.argsort(scores)[::-1]

    top_indices = ranked_indices[:TOP_K]

    selected_documents = [
        documents[index]
        for index in top_indices
    ]

    selected_scores = [
        scores[index]
        for index in top_indices
    ]

    best_document = selected_documents[0]

    combined_context = "\n\n".join(
        document["text"]
        for document in selected_documents
    )

    return (
        best_document["filename"],
        combined_context,
        selected_scores[0]
    )


if __name__ == "__main__":
    question = input("Enter your question: ")

    filename, document, score = retrieve(question)

    print("\nSelected document:", filename)
    print("Similarity score:", round(float(score), 4))

    print("\nRelevant context:")
    print(document)
