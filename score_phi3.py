import csv

scores = [
    (1, 1),
    (2, 0),
    (3, 0),
    (4, 2),
    (5, 0),
    (6, 1),
    (7, 2),
    (8, 1),
    (9, 0),
    (10, 1),
    (11, 0),
    (12, 1),
    (13, 0),
    (14, 1),
    (15, 1),
    (16, 1),
    (17, 0),
    (18, 2),
    (19, 1),
    (20, 1)
]

input_file = "quality_scoring.csv"

with open(input_file, "r", newline="") as f:
    rows = list(csv.DictReader(f))

for row in rows:
    if row["model"] == "Phi-3 Mini":
        qid = int(row["question_id"])
        for question_id, score in scores:
            if qid == question_id:
                row["correctness_score"] = score
                break

with open(input_file, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

total = sum(score for _, score in scores)
accuracy = total / 40 * 100

print(f"Phi-3 Mini score: {total}/40")
print(f"Phi-3 Mini accuracy: {accuracy:.1f}%")
