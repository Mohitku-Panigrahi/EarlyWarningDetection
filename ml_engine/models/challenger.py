import numpy as np
from typing import List, Dict, Any
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.cluster import KMeans

class HistGradientBoostingChallenger:
    """Gradient boosting challenger model for tabular performance benchmarking."""

    def __init__(self, max_iter: int = 100, max_depth: int = 4):
        self.model = HistGradientBoostingClassifier(
            max_iter=max_iter,
            max_depth=max_depth,
            class_weight="balanced",
            random_state=42,
        )
        self.feature_names = []

    def fit(self, X: np.ndarray, y: np.ndarray, feature_names: List[str]):
        self.feature_names = feature_names
        self.model.fit(X, y)
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.model.predict_proba(X)[:, 1]

class StudentBehaviorSegmentation:
    """
    Unsupervised K-Means clustering for student persona segmentation.
    NOTE: Used for pedagogical exploratory grouping, NOT for early-warning risk scoring.
    """

    def __init__(self, n_clusters: int = 4):
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init="auto")

    def fit_predict(self, X: np.ndarray) -> np.ndarray:
        return self.kmeans.fit_predict(X)
