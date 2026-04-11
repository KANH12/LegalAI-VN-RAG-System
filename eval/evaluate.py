import json
from main import rag_system

def normalize(text):
    return text.lower().strip()

def exact_match(pred, gt):
    return normalize(pred) == normalize(gt)

def f1_score(pred, gt):
    pred_tokens = normalize(pred).split()
    gt_tokens = normalize(gt).split()

    common = set(pred_tokens) & set(gt_tokens)
    if not common:
        return 0

    precision = len(common) / len(pred_tokens)
    recall = len(common) / len(gt_tokens)

    return 2 * precision * recall / (precision + recall)

with open("eval_dataset.json", "r", encoding="utf-8") as f:
    dataset = json.load(f)

em_total = 0
f1_total = 0

for item in dataset:
    pred = rag_system(item["question"])
    gt = item["answer"]

    em = exact_match(pred, gt)
    f1 = f1_score(pred, gt)

    em_total += em
    f1_total += f1

print("EM:", em_total / len(dataset))
print("F1:", f1_total / len(dataset))