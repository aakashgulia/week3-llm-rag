from pathlib import Path
import json
from fastembed import TextEmbedding

KNOWLEDGE_BASE = Path("knowledge_base")
OUTPUT_FILE = KNOWLEDGE_BASE / "embeddings.json"

CHUNK_SIZE = 500

model = TextEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)

documents = []
embeddings = []


def chunk_text(text, chunk_size=CHUNK_SIZE):
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])

        if chunk.strip():
            chunks.append(chunk)

    return chunks


for file_path in sorted(KNOWLEDGE_BASE.glob("*.txt")):
    text = file_path.read_text(encoding="utf-8").strip()

    if not text:
        continue

    chunks = chunk_text(text)

    for chunk in chunks:
        documents.append({
            "filename": file_path.name,
            "text": chunk
        })

        embedding = list(model.embed([chunk]))[0]
        embeddings.append(embedding.tolist())


data = {
    "documents": documents,
    "embeddings": embeddings
}

OUTPUT_FILE.write_text(
    json.dumps(data),
    encoding="utf-8"
)

print(f"Chunks embedded: {len(documents)}")
print(f"Embedding dimensions: {len(embeddings[0])}")
print(f"Saved to: {OUTPUT_FILE}")
