import json
import csv

files = {
    "Code Llama": "codellama_7b-instruct_evaluation_results.json",
    "StarCoder2": "starcoder2_3b_evaluation_results.json",
    "Phi-3 Mini": "phi3_mini_evaluation_results.json",
}

with open("quality_scoring.csv", "w", newline="") as f:
    writer = csv.writer(f)

    writer.writerow([
        "model",
        "question_id",
        "question",
        "reference_answer",
        "answer",
        "correctness_score",
        "notes"
    ])

    for model, filename in files.items():
        with open(filename, "r") as result_file:
            results = json.load(result_file)

        for r in results:
            writer.writerow([
                model,
                r["question_id"],
                r["question"],
                r["reference_answer"],
                r["answer"].strip(),
                "",
                ""
            ])

print("Created quality_scoring.csv")
print("Rows:", 60)

