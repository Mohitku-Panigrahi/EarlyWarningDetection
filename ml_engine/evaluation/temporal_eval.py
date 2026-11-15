from typing import List, Dict, Any
import numpy as np
from ml_engine.preprocessing.feature_pipeline import TemporalFeatureExtractor
from ml_engine.models.random_forest import CalibratedRandomForestEarlyWarning
from ml_engine.evaluation.metrics import evaluate_predictions

class TemporalEarlyWarningEvaluator:
    """
    Demonstrates model efficacy across time without future data leakage.
    Trains on data available up to weeks 2, 4, 6, and 8 only, demonstrating how
    detection recall strengthens as the semester progresses.
    """

    @staticmethod
    def evaluate_recall_trajectory(
        students_data: List[Dict[str, Any]],
        weeks: List[int] = [2, 4, 6, 8],
    ) -> List[Dict[str, Any]]:
        trajectory = []
        for w in weeks:
            extractor = TemporalFeatureExtractor(week_cutoff=w)
            X, y, feature_names = extractor.build_dataset(students_data)

            # Fit calibrated random forest on available temporal features
            model = CalibratedRandomForestEarlyWarning(n_estimators=100, max_depth=4)
            model.fit(X, y, feature_names)
            probs = model.predict_proba(X)

            eval_res = evaluate_predictions(y, probs, threshold=0.40)
            
            features_desc = (
                "Demographics + Initial Lecture Attendance" if w == 2 else (
                    "Attendance + Early LMS Clicks" if w == 4 else (
                        "Continuous Assessment 1 + Attendance Trend" if w == 6 else (
                            "Mid-Semester CA + Full Trajectory"
                        )
                    )
                )
            )

            trajectory.append({
                "week": w,
                "features_available": features_desc,
                "recall": eval_res["recall"],
                "precision": eval_res["precision"],
                "pr_auc": eval_res["pr_auc"],
                "f1": eval_res["f1"],
            })

        return trajectory
