import json,csv,re
from statistics import mean

files={"Phi-3 Mini":"phi3_mini_grounded_categorywise_results.json","StarCoder2":"starcoder2_3b_grounded_categorywise_results.json","Code Llama":"codellama_7b-instruct_grounded_categorywise_results.json"}

refs={x["id"]:x for x in json.load(open("evaluation_reference_categorywise.json"))}
rows=[]

def match(a,c):
    a=a.lower()
    terms={
    "mentions keda":["keda"],"mentions inference workers":["inference worker","worker"],
    "mentions redis queue length as scaling signal":["redis","queue length"],
    "separate api and inference responsibilities":["api","inference","separat"],
    "mentions independent scaling":["independent","scal"],
    "mentions queueing or handling busy workers":["queue","busy"],
    "mentions client/api":["client","api"],
    "mentions retrieval or inference service":["retrieval","inference"],
    "mentions ollama/code llama":["ollama","code llama"],
    "describes final response flow":["flow","response","result"],
    "retrieve.py":["retrieve.py"],"retrieve(query)":["retrieve(query)","retrieve (query)"],
    "app.py":["app.py"],"/ask-services":["/ask-services"]
    }
    t=terms.get(c.lower())
    if t:return all(x in a for x in t)
    w=[x for x in re.findall(r"[a-z0-9_./()-]+",c.lower()) if len(x)>2]
    return sum(x in a for x in w)>=max(1,len(w)//2)

for model,file in files.items():
    data={x["question_id"]:x for x in json.load(open(file))}
    for qid,ref in refs.items():
        r=data.get(qid)
        if not r:
            rows.append([model,qid,ref["category"],"MISSING","","","",""])
            continue
        score=100*sum(match(r["answer"],c) for c in ref["rubric"])/len(ref["rubric"])
        rows.append([model,qid,ref["category"],round(score,1),r.get("total_duration_seconds",r.get("wall_time_seconds","")),r.get("prompt_eval_count",""),r.get("eval_count",""),r.get("retrieval_similarity","")])

with open("categorywise_scored_results.csv","w",newline="") as f:
    w=csv.writer(f);w.writerow(["model","question_id","category","score_pct","latency_seconds","prompt_tokens","output_tokens","retrieval_similarity"]);w.writerows(rows)

cats=["Explanation","Code Retrieval","Dependency Understanding","Bug Analysis","Code Generation","Refactoring","RAG based Question"]
for model in files:
    print("\n"+model)
    for cat in cats:
        x=[r for r in rows if r[0]==model and r[2]==cat and r[3]!="MISSING"]
        print(f"{cat}: {mean(r[3] for r in x):.1f}% ({len(x)}/3)")
print("\nSaved: categorywise_scored_results.csv")
