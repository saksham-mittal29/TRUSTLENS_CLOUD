import json
import csv
import sys
from pathlib import Path
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support, accuracy_score

BASE_DIR = Path(__file__).resolve().parent

CACHE_FILE = BASE_DIR / "evidence_cache.json"
DATASET_FILE = BASE_DIR / "dataset.csv"
TRUSTLENS_RESULTS_FILE = BASE_DIR / "results.csv"

BERT_RESULTS_FILE = BASE_DIR / "bert_evaluation_results.csv"
BERT_SUMMARY_FILE = BASE_DIR / "bert_evaluation_summary.json"

MODEL_NAME = "textattack/bert-base-uncased-MNLI"

# Standard label mapping for 3-class NLI
# textattack/bert-base-uncased-MNLI:
# 0 -> CONTRADICTION
# 1 -> ENTAILMENT
# 2 -> NEUTRAL
INDEX_TO_LABEL = {
    0: "CONTRADICTED",
    1: "SUPPORTED",
    2: "NOT ENOUGH EVIDENCE"
}

LABEL_ORDER = ["SUPPORTED", "CONTRADICTED", "NOT ENOUGH EVIDENCE"]

# Normalization mapping for dataset labels to standard 3 classes
GROUND_TRUTH_MAP = {
    "SUPPORTED": "SUPPORTED",
    "SUPPORTS": "SUPPORTED",
    "CONTRADICTED": "CONTRADICTED",
    "REFUTES": "CONTRADICTED",
    "UNCERTAIN": "NOT ENOUGH EVIDENCE",
    "NOT ENOUGH INFO": "NOT ENOUGH EVIDENCE",
    "NOT ENOUGH EVIDENCE": "NOT ENOUGH EVIDENCE"
}


def normalize_label(label: str) -> str:
    cleaned = str(label).strip().upper()
    return GROUND_TRUTH_MAP.get(cleaned, cleaned)


def format_evidence_premise(evidence_list: list) -> str:
    """
    Format retrieved evidence snippets into a cohesive premise.
    """
    if not evidence_list:
        return "No evidence available."
    
    parts = []
    for item in evidence_list:
        title = item.get("title", "").strip()
        snippet = item.get("snippet", "").strip()
        if snippet:
            if title:
                parts.append(f"{title}: {snippet}")
            else:
                parts.append(snippet)
    
    return " ".join(parts) if parts else "No evidence available."


def calculate_brier_score(y_true: list, y_probs: np.ndarray, labels: list) -> float:
    """
    Calculate multi-class Brier score: (1/N) * sum_i sum_k (p_ik - y_ik)^2
    """
    n_samples = len(y_true)
    if n_samples == 0:
        return 0.0
    
    label_to_idx = {lbl: idx for idx, lbl in enumerate(labels)}
    y_one_hot = np.zeros((n_samples, len(labels)))
    for i, label in enumerate(y_true):
        if label in label_to_idx:
            y_one_hot[i, label_to_idx[label]] = 1.0
            
    brier = np.mean(np.sum((y_probs - y_one_hot) ** 2, axis=1))
    return float(brier)


def calculate_ece(y_true: list, y_pred: list, confidences: list, n_bins: int = 10) -> float:
    """
    Calculate Expected Calibration Error (ECE).
    confidences: array of max predicted probabilities (0 to 1)
    """
    n_samples = len(y_true)
    if n_samples == 0:
        return 0.0
    
    correctness = [1 if y_t == y_p else 0 for y_t, y_p in zip(y_true, y_pred)]
    
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    
    for i in range(n_bins):
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]
        
        # Determine items in this confidence bin
        in_bin = [
            j for j, conf in enumerate(confidences)
            if (conf > bin_lower and conf <= bin_upper) or (i == 0 and conf == bin_lower)
        ]
        
        bin_size = len(in_bin)
        if bin_size > 0:
            bin_acc = sum(correctness[j] for j in in_bin) / bin_size
            bin_conf = sum(confidences[j] for j in in_bin) / bin_size
            ece += (bin_size / n_samples) * abs(bin_acc - bin_conf)
            
    return float(ece)


def compute_metrics(y_true: list, y_pred: list, y_probs: np.ndarray, labels: list) -> dict:
    """
    Compute comprehensive metrics for classification and calibration.
    """
    acc = accuracy_score(y_true, y_pred)
    
    prec_macro, rec_macro, f1_macro, _ = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, average="macro", zero_division=0
    )
    
    prec_per_class, rec_per_class, f1_per_class, support_per_class = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, average=None, zero_division=0
    )
    
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    
    brier = calculate_brier_score(y_true, y_probs, labels)
    
    max_confs = np.max(y_probs, axis=1)
    ece = calculate_ece(y_true, y_pred, max_confs)
    
    per_class_metrics = {}
    for idx, lbl in enumerate(labels):
        per_class_metrics[lbl] = {
            "precision": round(float(prec_per_class[idx]), 4),
            "recall": round(float(rec_per_class[idx]), 4),
            "f1_score": round(float(f1_per_class[idx]), 4),
            "support": int(support_per_class[idx])
        }
        
    return {
        "accuracy": round(float(acc), 4),
        "macro_precision": round(float(prec_macro), 4),
        "macro_recall": round(float(rec_macro), 4),
        "macro_f1": round(float(f1_macro), 4),
        "brier_score": round(float(brier), 4),
        "ece": round(float(ece), 4),
        "per_class": per_class_metrics,
        "confusion_matrix": cm.tolist(),
        "total_samples": len(y_true)
    }


def evaluate_bert(model_path: str = None):
    chosen_model = model_path if model_path else MODEL_NAME
    print("=" * 70)
    print("TRUSTLENS VERIFICATION EVALUATION: BERT-BASED NLI vs CURRENT SYSTEM")
    print("=" * 70)
    
    # 1. Load Data
    if not CACHE_FILE.exists():
        raise FileNotFoundError(f"Evidence cache not found: {CACHE_FILE}")
        
    with CACHE_FILE.open("r", encoding="utf-8") as f:
        cache = json.load(f)
        
    print(f"Loaded {len(cache)} claims from {CACHE_FILE.name}")
    
    # 2. Load Pretrained BERT NLI Model
    print(f"Loading BERT NLI model from: {chosen_model}...")
    tokenizer = AutoTokenizer.from_pretrained(chosen_model)
    model = AutoModelForSequenceClassification.from_pretrained(chosen_model)
    model.eval()
    
    # Check GPU availability (Apple Silicon MPS / CUDA / CPU)
    if torch.backends.mps.is_available():
        device = torch.device("mps")
        print("Using Apple Silicon MPS acceleration.")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
        print("Using CUDA acceleration.")
    else:
        device = torch.device("cpu")
        print("Using CPU device.")
        
    model.to(device)
    
    # 3. Run Inference on All Benchmark Items
    bert_predictions_data = []
    y_true_all = []
    y_pred_all = []
    y_probs_all = []
    
    print("\nRunning BERT NLI verification on test benchmark...")
    for idx, item in enumerate(cache, start=1):
        claim_id = item.get("id", str(idx))
        claim = item.get("claim", "").strip()
        gt_raw = item.get("ground_truth", "")
        ground_truth = normalize_label(gt_raw)
        evidence = item.get("evidence", [])
        
        premise = format_evidence_premise(evidence)
        hypothesis = claim
        
        # Tokenize (Premise, Hypothesis)
        inputs = tokenizer(
            premise,
            hypothesis,
            return_tensors="pt",
            truncation=True,
            max_length=512
        ).to(device)
        
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=-1)[0].cpu().numpy()
            
        pred_idx = int(np.argmax(probs))
        bert_pred_label = INDEX_TO_LABEL[pred_idx]
        
        # Probabilities aligned to LABEL_ORDER: ["SUPPORTED", "CONTRADICTED", "NOT ENOUGH EVIDENCE"]
        # In INDEX_TO_LABEL: 0=CONTRADICTED, 1=SUPPORTED, 2=NOT ENOUGH EVIDENCE
        p_contra = float(probs[0])
        p_supp = float(probs[1])
        p_neu = float(probs[2])
        
        prob_vector_ordered = [p_supp, p_contra, p_neu]
        confidence = float(np.max(probs))
        
        y_true_all.append(ground_truth)
        y_pred_all.append(bert_pred_label)
        y_probs_all.append(prob_vector_ordered)
        
        bert_predictions_data.append({
            "id": claim_id,
            "claim": claim,
            "evidence_used": premise[:200] + ("..." if len(premise) > 200 else ""),
            "ground_truth": ground_truth,
            "bert_prediction": bert_pred_label,
            "prob_supported": round(p_supp, 4),
            "prob_contradicted": round(p_contra, 4),
            "prob_not_enough_evidence": round(p_neu, 4),
            "bert_confidence": round(confidence * 100, 2)
        })
        
        print(f"[{idx:02d}/{len(cache)}] Claim: {claim[:45]:<45} | GT: {ground_truth:<20} | BERT: {bert_pred_label:<20} (Conf: {confidence*100:5.1f}%)")
        
    y_probs_all = np.array(y_probs_all)
    
    # 4. Save results to CSV
    with BERT_RESULTS_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "id",
                "claim",
                "evidence_used",
                "ground_truth",
                "bert_prediction",
                "prob_supported",
                "prob_contradicted",
                "prob_not_enough_evidence",
                "bert_confidence"
            ]
        )
        writer.writeheader()
        writer.writerows(bert_predictions_data)
        
    print(f"\nSaved detailed prediction results to: {BERT_RESULTS_FILE}")
    
    # 5. Compute Full BERT Metrics
    bert_full_metrics = compute_metrics(y_true_all, y_pred_all, y_probs_all, LABEL_ORDER)
    
    # 6. Compare with Current TrustLens Results (Matched Subsets)
    matched_comparison = None
    trustlens_matched_metrics = None
    bert_matched_metrics = None
    
    if TRUSTLENS_RESULTS_FILE.exists():
        with TRUSTLENS_RESULTS_FILE.open("r", encoding="utf-8") as f:
            tl_rows = list(csv.DictReader(f))
            
        # Filter non-error rows
        valid_tl = [r for r in tl_rows if r.get("prediction") and r.get("prediction") != "ERROR" and not r.get("error")]
        
        if valid_tl:
            matched_tl_true = []
            matched_tl_pred = []
            matched_tl_probs = []
            
            matched_bert_true = []
            matched_bert_pred = []
            matched_bert_probs = []
            
            # Map cached BERT predictions by id
            bert_by_id = {str(item["id"]): item for item in bert_predictions_data}
            
            for row in valid_tl:
                cid = str(row["id"])
                gt = normalize_label(row["ground_truth"])
                pred = normalize_label(row["prediction"])
                conf_pct = float(row.get("confidence", 50))
                p_pred = max(0.01, min(0.99, conf_pct / 100.0))
                p_rem = (1.0 - p_pred) / 2.0
                
                # Construct pseudo-probability vector for TrustLens [SUPPORTED, CONTRADICTED, NOT ENOUGH EVIDENCE]
                tl_prob_vec = [p_rem, p_rem, p_rem]
                if pred in LABEL_ORDER:
                    tl_prob_vec[LABEL_ORDER.index(pred)] = p_pred
                else:
                    tl_prob_vec = [1/3, 1/3, 1/3]
                    
                matched_tl_true.append(gt)
                matched_tl_pred.append(pred)
                matched_tl_probs.append(tl_prob_vec)
                
                if cid in bert_by_id:
                    b_item = bert_by_id[cid]
                    matched_bert_true.append(b_item["ground_truth"])
                    matched_bert_pred.append(b_item["bert_prediction"])
                    matched_bert_probs.append([
                        b_item["prob_supported"],
                        b_item["prob_contradicted"],
                        b_item["prob_not_enough_evidence"]
                    ])
                    
            if len(matched_tl_true) > 0 and len(matched_bert_true) == len(matched_tl_true):
                trustlens_matched_metrics = compute_metrics(
                    matched_tl_true, matched_tl_pred, np.array(matched_tl_probs), LABEL_ORDER
                )
                bert_matched_metrics = compute_metrics(
                    matched_bert_true, matched_bert_pred, np.array(matched_bert_probs), LABEL_ORDER
                )
                
                matched_comparison = {
                    "matched_sample_count": len(matched_tl_true),
                    "current_trustlens": trustlens_matched_metrics,
                    "bert_nli": bert_matched_metrics
                }
                
    # 7. Generate Summary JSON
    summary_data = {
        "model_name": MODEL_NAME,
        "classes": LABEL_ORDER,
        "total_evaluated_claims": len(cache),
        "bert_full_benchmark_metrics": bert_full_metrics,
        "matched_comparison": matched_comparison
    }
    
    with BERT_SUMMARY_FILE.open("w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)
        
    print(f"Saved evaluation summary to: {BERT_SUMMARY_FILE}")
    
    # 8. Print Results and Comparison Table
    print("\n" + "=" * 70)
    print("FINAL EVALUATION REPORT: BERT NLI VERIFIER")
    print("=" * 70)
    print(f"Model: {MODEL_NAME}")
    print(f"Benchmark Test Size: {bert_full_metrics['total_samples']} claims")
    print(f"Accuracy:        {bert_full_metrics['accuracy'] * 100:.2f}%")
    print(f"Macro-Precision: {bert_full_metrics['macro_precision']:.4f}")
    print(f"Macro-Recall:    {bert_full_metrics['macro_recall']:.4f}")
    print(f"Macro-F1:        {bert_full_metrics['macro_f1']:.4f}")
    print(f"Brier Score:     {bert_full_metrics['brier_score']:.4f}  (Lower is better)")
    print(f"ECE (Calib Err): {bert_full_metrics['ece']:.4f}  (Lower is better)")
    
    print("\n" + "-" * 70)
    print("PER-CLASS METRICS (BERT NLI):")
    print("-" * 70)
    print(f"{'Class':<22} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10} | {'Support':<8}")
    print("-" * 70)
    for lbl in LABEL_ORDER:
        pcm = bert_full_metrics["per_class"][lbl]
        print(f"{lbl:<22} | {pcm['precision']:<10.4f} | {pcm['recall']:<10.4f} | {pcm['f1_score']:<10.4f} | {pcm['support']:<8}")
        
    print("\n" + "-" * 70)
    print("CONFUSION MATRIX (BERT NLI):")
    print("Rows = Ground Truth | Columns = Predicted")
    print("-" * 70)
    print(f"{'':<24} | {'Pred: SUPP':<12} | {'Pred: CONTRA':<12} | {'Pred: NOT ENOUGH'}")
    cm = bert_full_metrics["confusion_matrix"]
    print(f"{'True: SUPPORTED':<24} | {cm[0][0]:<12} | {cm[0][1]:<12} | {cm[0][2]}")
    print(f"{'True: CONTRADICTED':<24} | {cm[1][0]:<12} | {cm[1][1]:<12} | {cm[1][2]}")
    print(f"{'True: NOT ENOUGH EVIDENCE':<24} | {cm[2][0]:<12} | {cm[2][1]:<12} | {cm[2][2]}")
    
    if matched_comparison:
        print("\n" + "=" * 70)
        print(f"HEAD-TO-HEAD COMPARISON (On {matched_comparison['matched_sample_count']} Matched Examples Evaluated by Both)")
        print("=" * 70)
        tl_m = matched_comparison["current_trustlens"]
        b_m = matched_comparison["bert_nli"]
        print(f"{'Metric':<25} | {'Current TrustLens (Gemini)':<28} | {'BERT NLI':<15}")
        print("-" * 70)
        print(f"{'Accuracy':<25} | {tl_m['accuracy']*100:>26.2f}% | {b_m['accuracy']*100:>13.2f}%")
        print(f"{'Macro-F1':<25} | {tl_m['macro_f1']:>28.4f} | {b_m['macro_f1']:>15.4f}")
        print(f"{'Precision (Macro)':<25} | {tl_m['macro_precision']:>28.4f} | {b_m['macro_precision']:>15.4f}")
        print(f"{'Recall (Macro)':<25} | {tl_m['macro_recall']:>28.4f} | {b_m['macro_recall']:>15.4f}")
        print(f"{'Brier Score':<25} | {tl_m['brier_score']:>28.4f} | {b_m['brier_score']:>15.4f}")
        print(f"{'ECE (Calibration)':<25} | {tl_m['ece']:>28.4f} | {b_m['ece']:>15.4f}")
        print("=" * 70)
        
    print("\nEvaluation complete.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Evaluate BERT NLI on TrustLens dataset")
    parser.add_argument(
        "--model-path",
        type=str,
        default=None,
        help="Path or HuggingFace ID of the model to evaluate (default: textattack/bert-base-uncased-MNLI)"
    )
    args = parser.parse_args()
    
    # Auto-detect locally fine-tuned model if no path is passed and local model exists
    default_local = BASE_DIR / "models" / "bert-fever-finetuned"
    if args.model_path is None and default_local.exists():
        print(f"Auto-detected fine-tuned local model at: {default_local}")
        evaluate_bert(str(default_local))
    else:
        evaluate_bert(args.model_path)
