import json
import sys
import time
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

if len(sys.argv) != 2:
    print("Usage: python3 evaluate_models.py <model>")
    sys.exit(1)

model = sys.argv[1]

with open("evaluation_questions.json", "r") as f:
    questions = json.load(f)

with open("evaluation_reference.json", "r") as f:
    references = json.load(f)

reference_map = {
    item["id"]: item["reference_answer"]
    for item in references
}

results = []

filename = (
    model.replace(":", "_").replace("/", "_")
    + "_evaluation_results.json"
)
print(f"\n=== Testing {model} ===")
print(f"Questions: {len(questions)}")
print()

for item in questions:
    qid = item["id"]
    question = item["question"]

    print(f"Question {qid}/{len(questions)}...", flush=True)

    prompt = (
        "Answer the following question accurately and concisely. "
        "If the question asks about the project architecture or codebase, "
        "answer based on the Week 3 project context.\n\n"
        f"Question: {question}"
    )

    start = time.perf_counter()

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": 100,
                    "temperature": 0
                }
            },
            timeout=300
        )

        elapsed = time.perf_counter() - start
        data = response.json()

        results.append({
            "model": model,
            "question_id": qid,
            "question": question,
            "reference_answer": reference_map[qid],
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
            )
        })

        with open(filename, "w") as f:
            json.dump(results, f, indent=2)


    except Exception as e:
        print(f"ERROR on question {qid}: {e}")


with open(filename, "w") as f:
    json.dump(results, f, indent=2)

print()
print("Evaluation complete.")
print(f"Results recorded: {len(results)}")
print(f"Saved to: {filename}")

