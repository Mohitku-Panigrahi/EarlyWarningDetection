import numpy as np
from typing import Dict, Any, List, Tuple
from sklearn.metrics import (
    recall_score,
    precision_score,
    f1_score,
    fbeta_score,
    average_precision_score,
    roc_auc_score,
    confusion_matrix,
    calibration_curve,
)

def evaluate_predictions(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    threshold: float = 0.40,
) -> Dict[str, Any]:
    """
    Calculate full evaluation metrics focused on Early-Warning Detection.
    Prioritizes Recall and PR-AUC over bare accuracy.
    """
    y_pred = (y_prob >= threshold).astype(int)

    rec = float(recall_score(y_true, y_pred, zero_division=0))
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))
    f2 = float(fbeta_score(y_true, y_pred, beta=2.0, zero_division=0))
    
    try:
        pr_auc = float(average_precision_score(y_true, y_prob))
    except Exception:
        pr_auc = 0.0

    try:
        roc_auc = float(roc_auc_score(y_true, y_prob))
    except Exception:
        roc_auc = 0.0

    cm = confusion_matrix(y_true, y_pred)
    if cm.shape == (2, 2):
        tn, fp, fn, tp = cm.ravel()
    else:
        tn, fp, fn, tp = int(cm[0, 0]), 0, 0, 0

    return {
        "threshold": threshold,
        "recall": round(rec, 4),
        "precision": round(prec, 4),
        "f1": round(f1, 4),
        "f2": round(f2, 4),
        "pr_auc": round(pr_auc, 4),
        "roc_auc": round(roc_auc, 4),
        "confusion_matrix": {
            "true_positive": int(tp),
            "false_positive": int(fp),
            "true_negative": int(tn),
            "false_negative": int(fn),
        },
    }

def compute_calibration(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    n_bins: int = 5,
) -> List[Dict[str, float]]:
    """
    Compute reliability diagram / calibration curve bins.
    """
    prob_true, prob_pred = calibration_curve(y_true, y_prob, n_bins=n_bins, strategy="uniform")
    curve = []
    for pt, pp in zip(prob_true, prob_pred):
        curve.append({
            "bin_predicted": round(float(pp), 4),
            "fraction_positives": round(float(pt), 4),
        })
    return curve

def tune_threshold_for_recall(
    y_val: np.ndarray,
    y_prob_val: np.ndarray,
    target_recall: float = 0.80,
) -> float:
    """
    Select optimal decision threshold on validation set to guarantee recall >= target_recall
    while minimizing false alarms.
    """
    candidate_thresholds = np.linspace(0.10, 0.70, 61)
    best_threshold = 0.40
    best_f2 = 0.0

    for t in candidate_thresholds:
        y_pred = (y_prob_val >= t).astype(int)
        rec = recall_score(y_val, y_pred, zero_division=0)
        if rec >= target_recall:
            f2 = fbeta_score(y_val, y_pred, beta=2.0, zero_division=0)
            if f2 > best_f2:
                best_f2 = f2
                best_threshold = float(t)

    return round(best_threshold, 2)
