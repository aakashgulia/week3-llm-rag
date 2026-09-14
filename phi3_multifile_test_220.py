import json
import requests

MODEL = "phi3:mini"
OLLAMA_URL = "http://localhost:11434/api/generate"
CONTEXT_FILE = "multifile_project_context.txt"
QUESTIONS_FILE = "multifile_questions.json"
OUTPUT_FILE = "phi3_multifile_results_220.json"

with open(CONTEXT_FILE, "r") as f:
    context = f.read()

with open(QUESTIONS_FILE, "r") as f:
    questions = json.load(f)

results = []

for q in questions:
    prompt = f"""Answer the question using ONLY the project context below.
Do not invent files, endpoints, technologies, or architecture.
If the information is not present in the context, say so.

PROJECT CONTEXT:
{context}

QUESTION:
{q["question"]}

ANSWER:"""

    print(f"Running Q{q['id']}...", flush=True)

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0,
                "num_predict": 220
            }
        },
        timeout=300
    )

    data = response.json()

    results.append({
        "id": q["id"],
        "question": q["question"],
        "answer": data.get("response", ""),
        "eval_count": data.get("eval_count"),
        "prompt_eval_count": data.get("prompt_eval_count"),
        "total_duration": data.get("total_duration")
    })

    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)

print(f"Completed {len(results)}/{len(questions)} questions.")
print(f"Saved to {OUTPUT_FILE}")
