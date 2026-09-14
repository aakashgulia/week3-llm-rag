import json
import statistics

files = {
    "Code Llama": "codellama_7b-instruct_evaluation_results.json",
    "StarCoder2": "starcoder2_3b_evaluation_results.json",
    "Phi-3 Mini": "phi3_mini_evaluation_results.json",
}

for name, filename in files.items():
    with open(filename, "r") as f:
        results = json.load(f)

    total = statistics.mean(
        r["total_duration_seconds"] for r in results
    )

    load = statistics.mean(
        r["load_duration_seconds"] for r in results
    )

    output_tokens = statistics.mean(
        r["eval_count"] for r in results
    )

    generation = statistics.mean(
        r["eval_duration_seconds"] for r in results
    )

    prompt_tokens = statistics.mean(
        r["prompt_eval_count"] for r in results
    )

    print(f"\n{name}")
    print(f"  Average total time:       {total:.2f} seconds")
    print(f"  Average model load time:  {load:.2f} seconds")
    print(f"  Average prompt tokens:    {prompt_tokens:.1f}")
    print(f"  Average output tokens:    {output_tokens:.1f}")
    print(f"  Average generation time:  {generation:.2f} seconds")
