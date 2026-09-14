from pathlib import Path

SOURCE_FILE = Path("knowledge_base/autoscaling.txt")
CHUNK_SIZE = 500


def chunk_text(text, chunk_size=CHUNK_SIZE):
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)

    return chunks


text = SOURCE_FILE.read_text(encoding="utf-8")
chunks = chunk_text(text)

print(f"Created {len(chunks)} chunk(s).")

for index, chunk in enumerate(chunks, start=1):
    print(f"\n--- Chunk {index} ---")
    print(chunk)

