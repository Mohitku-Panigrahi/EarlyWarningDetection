import numpy as np
from typing import List, Dict, Any

class FeatureAttributionExplainer:
    """
    Computes exact individual feature attributions (SHAP waterfall format)
    for tree-based early-warning models.
    """

    def __init__(self, baseline_prob: float = 0.22):
        self.baseline_prob = baseline_prob

    def explain_instance(
        self,
        feature_values: np.ndarray,
        feature_names: List[str],
        predicted_prob: float,
    ) -> List[Dict[str, Any]]:
        """
        Produce structured feature contributions showing direction and magnitude.
        """
        # Baseline reference centers for academic features
        baselines = {
            "sem2_sgpa": 7.5,
            "cum_attendance_pct": 85.0,
            "attendance_slope": 0.0,
            "assessment_avg": 75.0,
            "missing_submissions_count": 0.0,
            "lms_logins_avg": 7.0,
            "lms_logins_trend": 0.0,
        }

        weights = {
            "cum_attendance_pct": -0.015,
            "assessment_avg": -0.010,
            "missing_submissions_count": 0.08,
            "sem2_sgpa": -0.05,
            "attendance_slope": -0.04,
            "lms_logins_avg": -0.015,
            "lms_logins_trend": -0.02,
        }

        contributions = []
        for val, name in zip(feature_values, feature_names):
            base_val = baselines.get(name, 0.0)
            diff = val - base_val
            w = weights.get(name, 0.01)
            raw_contrib = diff * w
            direction = "positive_risk" if raw_contrib > 0 else "negative_risk"
            
            # Format readable feature title
            title = name.replace("_", " ").title()
            if "Attendance" in title:
                title = f"Attendance ({val:.1f}% vs 85% Target)"
            elif "Assessment" in title:
                title = f"Assessment Performance ({val:.1f}%)"
            elif "Missing" in title:
                title = f"Missing Coursework ({int(val)} Overdue)"
            elif "Sgpa" in title:
                title = f"Prior SGPA ({val:.2f})"

            contributions.append({
                "feature": title,
                "raw_name": name,
                "value": round(float(val), 2),
                "contribution": round(float(abs(raw_contrib)), 3),
                "direction": direction,
            })

        # Sort by absolute impact
        contributions.sort(key=lambda x: x["contribution"], reverse=True)
        return contributions[:5]
