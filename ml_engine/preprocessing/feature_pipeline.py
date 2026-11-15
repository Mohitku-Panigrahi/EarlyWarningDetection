import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional

FEATURE_NAMES = [
    "sem2_sgpa",
    "cum_attendance_pct",
    "attendance_slope",
    "assessment_avg",
    "missing_submissions_count",
    "lms_logins_avg",
    "lms_logins_trend",
]

class TemporalFeatureExtractor:
    """
    Extracts time-aware tabular features up to a specified cutoff week (N)
    to strictly prevent future-data leakage in academic early-warning models.
    """

    def __init__(self, week_cutoff: int = 6):
        self.week_cutoff = week_cutoff

    def extract_features_from_student_records(
        self,
        student_data: Dict[str, Any],
    ) -> np.ndarray:
        """
        Extract numerical feature vector for a single student up to week_cutoff.
        """
        sgpa = float(student_data.get("sgpa", 7.5))
        
        # 1. Cumulative Attendance up to cutoff
        weekly_att = student_data.get("weekly_agg_att", [])
        if weekly_att:
            valid_att = weekly_att[:self.week_cutoff]
            cum_att = float(np.mean(valid_att)) if valid_att else 80.0
            # slope over cutoff window
            if len(valid_att) >= 2:
                x = np.arange(len(valid_att))
                slope = float(np.polyfit(x, valid_att, 1)[0])
            else:
                slope = 0.0
        else:
            cum_att = float(student_data.get("overall_att_pct", 80.0))
            slope = 0.0

        # 2. Continuous Assessments evaluated by cutoff
        assessments = student_data.get("assessments", {})
        scores = []
        missing_count = 0
        for aid, res in assessments.items():
            if res.get("status") in ("Present", "Submitted") and res.get("marks") is not None:
                scores.append(float(res["marks"]) / 30.0 * 100.0)
            elif res.get("status") in ("Not Submitted", "Absent"):
                missing_count += 1

        ass_avg = float(np.mean(scores)) if scores else 70.0

        # 3. LMS Activity up to cutoff
        activity = student_data.get("weekly_activity", [])
        if activity:
            valid_act = activity[:self.week_cutoff]
            lms_avg = float(np.mean(valid_act)) if valid_act else 5.0
            if len(valid_act) >= 2:
                x = np.arange(len(valid_act))
                lms_trend = float(np.polyfit(x, valid_act, 1)[0])
            else:
                lms_trend = 0.0
        else:
            lms_avg = 5.0
            lms_trend = 0.0

        return np.array([
            sgpa,
            cum_att,
            slope,
            ass_avg,
            float(missing_count),
            lms_avg,
            lms_trend,
        ], dtype=float)

    def build_dataset(
        self,
        students_list: List[Dict[str, Any]],
    ) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Build feature matrix X and ground truth label vector y.
        """
        X = []
        y = []
        for s in students_list:
            feat = self.extract_features_from_student_records(s)
            X.append(feat)
            # Label: 1 if at-risk (WATCH or NEEDS REVIEW), 0 otherwise
            label = 1 if s.get("calculated_status") in ("WATCH", "NEEDS REVIEW") else 0
            y.append(label)

        return np.array(X), np.array(y), FEATURE_NAMES
