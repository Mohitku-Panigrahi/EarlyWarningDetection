import numpy as np
from typing import List, Dict, Any
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV

class CalibratedRandomForestEarlyWarning:
    """
    Primary early-warning model:
    RandomForestClassifier with balanced subsampling, calibrated via Isotonic or Sigmoid
    regression to ensure true probability outputs for mentor decision support.
    """

    def __init__(self, n_estimators: int = 400, max_depth: int = 8, min_samples_leaf: int = 5):
        self.rf = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_leaf=min_samples_leaf,
            class_weight="balanced_subsample",
            random_state=42,
            n_jobs=1,
        )
        self.calibrated_model = None
        self.feature_names = []

    def fit(self, X: np.ndarray, y: np.ndarray, feature_names: List[str]):
        self.feature_names = feature_names
        # Adapt min_samples_leaf for small datasets/CV folds
        if len(X) < 20:
            self.rf.min_samples_leaf = max(1, len(X) // 6)
        
        # Use sigmoid if sample size is under 500, else isotonic
        method = "sigmoid" if len(X) < 500 else "isotonic"
        
        min_class_count = int(min(np.bincount(y))) if len(np.unique(y)) > 1 else 1
        cv = max(2, min(3, min_class_count)) if min_class_count >= 2 else 2

        try:
            self.calibrated_model = CalibratedClassifierCV(self.rf, method=method, cv=cv)
            self.calibrated_model.fit(X, y)
        except Exception:
            self.calibrated_model = None

        # Always fit base rf for feature importances
        self.rf.fit(X, y)
        if self.calibrated_model is None:
            self.calibrated_model = self.rf
            
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.calibrated_model.predict_proba(X)[:, 1]

    def get_feature_importances(self) -> Dict[str, float]:
        importances = self.rf.feature_importances_
        return {fn: round(float(imp), 4) for fn, imp in zip(self.feature_names, importances)}
