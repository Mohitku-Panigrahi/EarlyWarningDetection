from datetime import date, datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, UniqueConstraint, Text
from sqlalchemy.orm import relationship
from backend.app.database.session import Base

class Assessment(Base):
    """Assessment component created by faculty."""
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    assessment_code = Column(String(32), unique=True, index=True, nullable=False)  # e.g. A01
    course_code = Column(String(32), ForeignKey("subjects.subject_code"), index=True, nullable=False)
    type = Column(String(64), nullable=False)  # Test, Assignment, Project, etc.
    title = Column(String(128), nullable=False)
    mode = Column(String(32), default="manual", nullable=False)  # manual, online
    assigned_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)
    max_marks = Column(Float, default=30.0, nullable=False)
    faculty_id = Column(String(32), nullable=True)

    subject = relationship("Subject", back_populates="assessments")
    student_assessments = relationship("StudentAssessment", back_populates="assessment", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Assessment {self.assessment_code}: {self.title}>"

class StudentAssessment(Base):
    """Individual student assessment result, status, and teacher comments."""
    __tablename__ = "student_assessments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), index=True, nullable=False)
    assessment_id = Column(Integer, ForeignKey("assessments.id", ondelete="CASCADE"), index=True, nullable=False)
    marks = Column(Float, nullable=True)  # Null if pending
    status = Column(String(32), nullable=False)  # Present, Submitted, Not Submitted, Absent, Pending
    teacher_comment = Column(Text, default="", nullable=True)
    evaluated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        UniqueConstraint("student_id", "assessment_id", name="uq_student_assessment"),
    )

    student = relationship("Student", back_populates="assessments")
    assessment = relationship("Assessment", back_populates="student_assessments")
