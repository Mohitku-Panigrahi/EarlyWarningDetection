from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier, export_text
from typing import Dict, Any, List
import numpy as np

class BaselineLogisticRegression:
    """Interpretable linear baseline with class-weight balancing."""

    def __init__(self):
        self.model = LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42)
        self.feature_names = []

    def fit(self, X: np.ndarray, y: np.ndarray, feature_names: List[str]):
        self.feature_names = feature_names
        self.model.fit(X, y)
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(X)[:, 1]

    def get_coefficients(self) -> Dict[str, float]:
        coefs = self.model.coef_[0]
        return {fn: round(float(c), 4) for fn, c in zip(self.feature_names, coefs)}

class InterpretableDecisionTree:
    """Interpretable shallow decision tree (depth 3 to 4) mirroring rule splits."""

    def __init__(self, max_depth: int = 4):
        self.model = DecisionTreeClassifier(max_depth=max_depth, class_weight="balanced", random_state=42)
        self.feature_names = []

    def fit(self, X: np.ndarray, y: np.ndarray, feature_names: List[str]):
        self.feature_names = feature_names
        self.model.fit(X, y)
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(X)[:, 1]

    def export_rules_text(self) -> str:
        return export_text(self.model, feature_names=self.feature_names)
