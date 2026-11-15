from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.app.database.session import Base

class RiskAssessment(Base):
    """Early-warning risk score, status classification, SHAP feature attributions, and rules."""
    __tablename__ = "risk_assessments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), index=True, nullable=False)
    model_version = Column(String(64), default="v2.4-lpu-demo", nullable=False)
    prediction = Column(Integer, default=0, nullable=False)  # 0: Low/Normal, 1: At-Risk
    probability = Column(Float, nullable=False)  # Calibrated probability [0.0, 1.0]
    decision_threshold = Column(Float, default=0.40, nullable=False)
    status = Column(String(32), nullable=False)  # ON TRACK, WATCH, NEEDS REVIEW
    assessment_week = Column(Integer, default=6, nullable=False)
    
    # Explainable AI JSON stores
    explanation_summary = Column(Text, nullable=True)
    shap_json = Column(Text, nullable=True)  # JSON: feature attributions
    rules_fired = Column(Text, nullable=True)  # JSON or comma-separated rule codes (R1, R2, etc.)
    counterfactual_json = Column(Text, nullable=True)  # JSON: what-if scenarios
    bayesian_json = Column(Text, nullable=True)  # JSON: prior, likelihood, posterior
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        UniqueConstraint("student_id", "assessment_week", "model_version", name="uq_student_week_risk"),
    )

    student = relationship("Student", back_populates="risk_assessments")

class ModelRegistry(Base):
    """Registry of trained models, validation metrics, and governance states."""
    __tablename__ = "model_registry"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    model_name = Column(String(64), nullable=False)  # e.g. RandomForestEarlyWarning
    model_version = Column(String(32), unique=True, index=True, nullable=False)  # e.g. v2.4-lpu
    dataset_version = Column(String(64), nullable=False)  # e.g. synthetic-lpu-v1 / oulad-v1
    metrics_json = Column(Text, nullable=False)  # JSON: recall, precision, f1, f2, pr_auc
    threshold = Column(Float, default=0.40, nullable=False)
    status = Column(String(32), default="active", nullable=False)  # active, challenger, deprecated
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
