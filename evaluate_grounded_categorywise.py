import json
import sys
import time
import requests
from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/generate"
RETRIEVAL_URL = "http://localhost:8001/retrieve"

if len(sys.argv) != 2:
    print("Usage: python3 evaluate_grounded_categorywise.py <model>")
    sys.exit(1)

model = sys.argv[1]

with open("evaluation_questions_categorywise.json") as f:
    questions = json.load(f)

with open("evaluation_reference_categorywise.json") as f:
    references = json.load(f)

reference_map = {x["id"]: x for x in references}

def read_file(name):
    return Path(name).read_text()

def project_context(category):
    if category == "Explanation":
        return (
            read_file("knowledge_base/autoscaling.txt")
            + "\n\n--- LLM INFERENCE DOCUMENT ---\n\n"
            + read_file("knowledge_base/llm_inference.txt")
        )

    if category == "Code Retrieval":
        return (
            "--- app.py ---\n"
            + read_file("app.py")
            + "\n\n--- retrieve.py ---\n"
            + read_file("retrieve.py")
            + "\n\n--- create_embeddings.py ---\n"
            + read_file("create_embeddings.py")
        )

    if category == "Dependency Understanding":
        return (
            "--- app.py ---\n"
            + read_file("app.py")
            + "\n\n--- retrieval_service.py ---\n"
            + read_file("retrieval_service.py")
            + "\n\n--- retrieve.py ---\n"
            + read_file("retrieve.py")
            + "\n\n--- inference_service.py ---\n"
            + read_file("inference_service.py")
        )

    if category == "Bug Analysis":
        return (
            "--- app.py ---\n"
            + read_file("app.py")
            + "\n\n--- retrieval_service.py ---\n"
            + read_file("retrieval_service.py")
            + "\n\n--- retrieve.py ---\n"
            + read_file("retrieve.py")
            + "\n\n--- inference_service.py ---\n"
            + read_file("inference_service.py")
        )

    if category == "Code Generation":
        return (
            "--- app.py ---\n"
            + read_file("app.py")
            + "\n\n--- inference_service.py ---\n"
            + read_file("inference_service.py")
            + "\n\n--- retrieve.py ---\n"
            + read_file("retrieve.py")
        )

    if category == "Refactoring":
        return (
            "--- app.py ---\n"
            + read_file("app.py")
            + "\n\n--- retrieval_service.py ---\n"
            + read_file("retrieval_service.py")
            + "\n\n--- retrieve.py ---\n"
            + read_file("retrieve.py")
            + "\n\n--- inference_service.py ---\n"
            + read_file("inference_service.py")
        )

    return ""

def rag_context(question):
    response = requests.get(
        RETRIEVAL_URL,
        params={"query": question},
        timeout=30
    )
    response.raise_for_status()
    data = response.json()

    return data.get("context", ""), {
        "source_document": data.get("source_document", ""),
        "retrieval_similarity": data.get("similarity_score", 0)
    }

filename = (
    model.replace(":", "_").replace("/", "_")
    + "_grounded_categorywise_results.json"
)

results = []
if Path(filename).exists():
    with open(filename) as f:
        results = json.load(f)
existing_ids = {x["question_id"] for x in results}
existing_file = Path(filename) if "filename" in locals() else None

print(f"\n=== Grounded evaluation: {model} ===")
print(f"Questions: {len(questions)}")
print()

for item in questions:
    if item["id"] in existing_ids:
        continue
    qid = item["id"]
    category = item["category"]
    question = item["question"]

    print(
        f"Question {qid}/{len(questions)} [{category}]...",
        flush=True
    )

    retrieval_info = {}

    try:
        if category == "RAG based Question":
            context, retrieval_info = rag_context(question)
        else:
            context = project_context(category)

        prompt = f"""You are evaluating a software engineering project.

Answer the question using ONLY the supplied project context.
Do not invent files, functions, services, technologies, or architecture
that are not present in the context.

Be accurate and concise.

PROJECT CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""

        start = time.perf_counter()

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": 150,
                    "temperature": 0
                }
            },
            timeout=300
        )

        elapsed = time.perf_counter() - start
        response.raise_for_status()
        data = response.json()

        results.append({
            "model": model,
            "question_id": qid,
            "category": category,
            "question": question,
            "reference_answer": reference_map[qid]["reference"],
            "rubric": reference_map[qid]["rubric"],
            "answer": data.get("response", ""),
            "completed": data.get("done", False),
            "done_reason": data.get("done_reason", ""),
            "wall_time_seconds": round(elapsed, 3),
            "total_duration_seconds": round(
                data.get("total_duration", 0) / 1e9, 3
            ),
            "load_duration_seconds": round(
                data.get("load_duration", 0) / 1e9, 3
            ),
            "prompt_eval_count": data.get("prompt_eval_count", 0),
            "prompt_eval_duration_seconds": round(
                data.get("prompt_eval_duration", 0) / 1e9, 3
            ),
            "eval_count": data.get("eval_count", 0),
            "eval_duration_seconds": round(
                data.get("eval_duration", 0) / 1e9, 3
            ),
            **retrieval_info
        })

        with open(filename, "w") as f:
            json.dump(results, f, indent=2)

    except Exception as e:
        print(f"ERROR on question {qid}: {e}")

with open(filename, "w") as f:
    json.dump(results, f, indent=2)

print()
print("Grounded evaluation complete.")
print(f"Results recorded: {len(results)}")
print(f"Saved to: {filename}")
