import pytest
import numpy as np

from ml_engine.preprocessing.feature_pipeline import TemporalFeatureExtractor
from ml_engine.models.baselines import BaselineLogisticRegression, InterpretableDecisionTree
from ml_engine.models.random_forest import CalibratedRandomForestEarlyWarning
from ml_engine.models.challenger import HistGradientBoostingChallenger, StudentBehaviorSegmentation
from ml_engine.rules.rule_engine import EarlyWarningRuleEngine
from ml_engine.explainability.counterfactuals import CounterfactualSimulator, TransparentBayesianUpdater
from ml_engine.decision_support.pipeline import (
    AcademicMonitorComponent,
    AcademicRiskComponent,
    AcademicExplainerComponent,
    AcademicPlannerComponent,
)

def test_temporal_feature_extractor():
    sample_student = {
        "sgpa": 7.4,
        "weekly_agg_att": [88, 86, 84, 82, 85, 82, 84, 86],
        "assessments": {
            "A01": {"status": "Present", "marks": 24.0},
            "A02": {"status": "Present", "marks": 22.0},
            "A03": {"status": "Not Submitted", "marks": 0.0},
        },
        "weekly_activity": [8, 7, 6, 5, 6, 4],
        "calculated_status": "WATCH",
    }
    extractor = TemporalFeatureExtractor(week_cutoff=6)
    vec = extractor.extract_features_from_student_records(sample_student)
    assert len(vec) == 7
    assert vec[0] == 7.4  # SGPA
    assert 80.0 <= vec[1] <= 90.0  # Cumulative attendance
    assert vec[4] == 1.0  # 1 missing submission

def test_calibrated_random_forest():
    X = np.array([
        [8.5, 92.0, 0.1, 85.0, 0, 9.0, 0.1],
        [8.2, 88.0, 0.0, 80.0, 0, 8.0, 0.0],
        [7.0, 72.0, -0.2, 60.0, 2, 3.0, -0.2],
        [6.5, 65.0, -0.4, 52.0, 3, 2.0, -0.3],
        [8.8, 95.0, 0.1, 90.0, 0, 10.0, 0.1],
        [6.0, 58.0, -0.5, 45.0, 4, 1.0, -0.4],
    ])
    y = np.array([0, 0, 1, 1, 0, 1])
    feature_names = ["sgpa", "att", "att_slope", "marks", "missing", "lms", "lms_slope"]

    model = CalibratedRandomForestEarlyWarning(n_estimators=50, max_depth=3)
    model.fit(X, y, feature_names)

    probs = model.predict_proba(X)
    assert len(probs) == 6
    assert all(0.0 <= p <= 1.0 for p in probs)
    # High-risk student should have higher probability than top student
    assert probs[5] > probs[0]

    importances = model.get_feature_importances()
    assert len(importances) == 7

def test_baseline_and_challenger_models():
    X = np.random.randn(20, 5)
    y = np.array([0]*12 + [1]*8)
    fn = [f"f{i}" for i in range(5)]

    # 1. Logistic Regression
    lr = BaselineLogisticRegression()
    lr.fit(X, y, fn)
    assert len(lr.get_coefficients()) == 5

    # 2. Decision Tree
    dt = InterpretableDecisionTree(max_depth=3)
    dt.fit(X, y, fn)
    tree_text = dt.export_rules_text()
    assert "f0" in tree_text or "class" in tree_text

    # 3. HistGradientBoosting
    hgb = HistGradientBoostingChallenger()
    hgb.fit(X, y, fn)
    hgb_probs = hgb.predict_proba(X)
    assert len(hgb_probs) == 20

    # 4. KMeans
    km = StudentBehaviorSegmentation(n_clusters=3)
    clusters = km.fit_predict(X)
    assert len(clusters) == 20

def test_rule_engine_heuristics():
    engine = EarlyWarningRuleEngine()

    # Aarav profile: 82% attendance, 64% marks, 2 missing submissions
    rules = engine.evaluate(attendance_pct=82.0, recent_marks_pct=64.0, missing_submissions=2, marks_drop_pct=12.0)
    rule_ids = [r.rule_id for r in rules]
    assert "R2" in rule_ids  # Score dip
    assert "R3" in rule_ids  # Missing submissions

    # Struggling profile: 68% attendance (<75%)
    rules_struggling = engine.evaluate(attendance_pct=68.0, recent_marks_pct=55.0, missing_submissions=1)
    struggling_ids = [r.rule_id for r in rules_struggling]
    assert "R1" in struggling_ids  # Attendance below threshold
    assert "R4" in struggling_ids  # Multi-indicator

def test_counterfactual_and_bayesian():
    # Counterfactual
    cf = CounterfactualSimulator.simulate_recovery(current_prob=0.44, attendance_pct=82.0, missing_count=2)
    assert cf["projected_probability"] < 0.44
    assert len(cf["target_actions"]) >= 2

    # Bayesian
    bayesian = TransparentBayesianUpdater(base_prior=0.22)
    up1 = bayesian.update(has_low_attendance=True, has_low_marks=True, has_overdue_work=False)
    assert up1["posterior"] > 0.22

    up2 = bayesian.update(has_low_attendance=False, has_low_marks=False, has_overdue_work=False)
    assert up2["posterior"] < 0.22

def test_decision_support_pipeline():
    indicators = AcademicMonitorComponent.extract_indicators(attendance_pct=82.0, recent_marks_pct=64.0, missing_count=2)
    assert indicators["attendance_pct"] == 82.0

    risk_comp = AcademicRiskComponent(threshold=0.40)
    risk_res = risk_comp.score(indicators)
    assert risk_res["status"] == "WATCH"

    explainer = AcademicExplainerComponent()
    exp_res = explainer.explain(indicators, risk_res)
    assert len(exp_res["rules_fired"]) >= 1
    assert "projected_probability" in exp_res["counterfactual"]

    planner = AcademicPlannerComponent()
    plans = planner.plan(exp_res["rules_fired"], student_id=12511001)
    assert len(plans) >= 1
    assert plans[0]["requires_human_approval"] is True
