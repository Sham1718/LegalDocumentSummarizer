import os
from rouge_score import rouge_scorer
import statistics

GOLD_DIR = "../in_abs/subset_50/summary"
PRED_DIR = "../outputs/textrank/summaries"

scorer = rouge_scorer.RougeScorer(
    ['rouge1', 'rouge2', 'rougeL'],
    use_stemmer=True
)

rouge1_scores = []
rouge2_scores = []
rougeL_scores = []

files = os.listdir(GOLD_DIR)

for file in files:
    if not file.endswith(".txt"):
        continue

    gold_path = os.path.join(GOLD_DIR, file)
    pred_path = os.path.join(PRED_DIR, file)

    if not os.path.exists(pred_path):
        print(f"Missing prediction for {file}")
        continue

    with open(gold_path, "r", encoding="utf-8") as f:
        gold_text = f.read()

    with open(pred_path, "r", encoding="utf-8") as f:
        pred_text = f.read()

    scores = scorer.score(gold_text, pred_text)

    rouge1_scores.append(scores['rouge1'].fmeasure)
    rouge2_scores.append(scores['rouge2'].fmeasure)
    rougeL_scores.append(scores['rougeL'].fmeasure)

print("==== TextRank ROUGE Scores ====")
print("ROUGE-1 F1:", round(statistics.mean(rouge1_scores), 4))
print("ROUGE-2 F1:", round(statistics.mean(rouge2_scores), 4))
print("ROUGE-L F1:", round(statistics.mean(rougeL_scores), 4))
