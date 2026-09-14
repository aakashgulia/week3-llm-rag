import csv
from statistics import mean

rows = list(csv.DictReader(open("categorywise_scored_results.csv")))

models = ["Phi-3 Mini", "StarCoder2", "Code Llama"]
categories = [
    "Explanation",
    "Code Retrieval",
    "Dependency Understanding",
    "Bug Analysis",
    "Code Generation",
    "Refactoring",
    "RAG based Question"
]

with open("FINAL_7_CATEGORY_REPORT.txt", "w") as f:
    f.write("LLM WEEK 4 - 7 CATEGORY EVALUATION REPORT\n")
    f.write("=" * 55 + "\n\n")

    f.write("CATEGORY-WISE SCORES\n")
    f.write("-" * 55 + "\n")
    f.write(f"{'Category':30} {'Phi-3':>10} {'StarCoder2':>12} {'CodeLlama':>12}\n")

    for cat in categories:
        vals = []
        for model in models:
            x = [r for r in rows if r["model"] == model and r["category"] == cat and r["score_pct"] != "MISSING"]
            if x:
                score = mean(float(r["score_pct"]) for r in x)
                text = f"{score:.1f}%"
                if len(x) < 3:
                    text += f" ({len(x)}/3)"
            else:
                text = "N/A"
            vals.append(text)
        f.write(f"{cat:30} {vals[0]:>10} {vals[1]:>12} {vals[2]:>12}\n")

    f.write("\nOVERALL METRICS\n")
    f.write("-" * 55 + "\n")

    for model in models:
        x = [r for r in rows if r["model"] == model and r["score_pct"] != "MISSING"]
        score = mean(float(r["score_pct"]) for r in x)
        latency = mean(float(r["latency_seconds"]) for r in x)
        tokens = mean(float(r["output_tokens"]) for r in x)

        f.write(
            f"{model}: Score={score:.1f}% | "
            f"Latency={latency:.2f}s | "
            f"Output tokens={tokens:.1f} | "
            f"Valid={len(x)}/21\n"
        )

    f.write("\nCATEGORY WINNERS\n")
    f.write("-" * 55 + "\n")

    for cat in categories:
        scores = {}
        for model in models:
            x = [r for r in rows if r["model"] == model and r["category"] == cat and r["score_pct"] != "MISSING"]
            if x:
                scores[model] = mean(float(r["score_pct"]) for r in x)

        winner = max(scores, key=scores.get)
        f.write(f"{cat}: {winner} ({scores[winner]:.1f}%)\n")

    f.write("\nKEY FINDINGS\n")
    f.write("-" * 55 + "\n")
    f.write("1. Code Llama achieved the highest overall score among valid responses.\n")
    f.write("2. Code Llama was strongest in Code Generation and RAG-based questions.\n")
    f.write("3. Phi-3 Mini showed more balanced performance across general project tasks.\n")
    f.write("4. StarCoder2 had the lowest average latency and output-token usage.\n")
    f.write("5. StarCoder2 had the lowest overall rubric score in this evaluation.\n")
    f.write("6. Code Llama Q4 timed out after 300 seconds and was therefore marked missing.\n")
    f.write("7. Scores are rubric-based project-task scores, not generic LLM accuracy.\n")

print("FINAL REPORT CREATED: FINAL_7_CATEGORY_REPORT.txt")
