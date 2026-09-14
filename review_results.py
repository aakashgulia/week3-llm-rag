import json

file = "codellama_7b-instruct_evaluation_results.json"

with open(file, "r") as f:
    results = json.load(f)

for item in results:
    print("\n" + "=" * 80)
    print(f"QUESTION {item['question_id']}")
    print("=" * 80)
    print("Question:")
    print(item["question"])
    print("\nReference Answer:")
    print(item["reference_answer"])
    print("\nCode Llama Answer:")
    print(item["answer"])

