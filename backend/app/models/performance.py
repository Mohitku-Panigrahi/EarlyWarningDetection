from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.app.database.session import Base

class StudentSubjectPerformance(Base):
    """Subject-wise aggregated performance for continuous evaluation."""
    __tablename__ = "student_subject_performance"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), index=True, nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), index=True, nullable=False)
    
    # Attendance summary
    delivered = Column(Integer, default=0, nullable=False)
    attended = Column(Integer, default=0, nullable=False)
    duty_leave = Column(Integer, default=0, nullable=False)
    first_week_bonus = Column(Integer, default=0, nullable=False)
    attendance_percentage = Column(Float, default=0.0, nullable=False)
    
    # Internal marks & assignments
    internal_marks = Column(Float, default=0.0, nullable=False)
    maximum_internal_marks = Column(Float, default=30.0, nullable=False)
    assignment_completion = Column(Float, default=100.0, nullable=False)
    assessment_date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        UniqueConstraint("student_id", "subject_id", name="uq_student_subject"),
    )

    student = relationship("Student", back_populates="subject_performances")
    subject = relationship("Subject", back_populates="performances")

class AcademicRecord(Base):
    """Semester-level summary records (historical & current)."""
    __tablename__ = "academic_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), index=True, nullable=False)
    semester = Column(Integer, nullable=False)
    cgpa = Column(Float, nullable=False)
    semester_average = Column(Float, nullable=False)
    attendance_average = Column(Float, nullable=False)
    recorded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    student = relationship("Student", back_populates="academic_records")

class WeeklyAcademicMetric(Base):
    """Weekly aggregated multi-factor indicators for trend analytics."""
    __tablename__ = "weekly_academic_metrics"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), index=True, nullable=False)
    week_number = Column(Integer, nullable=False, index=True)
    attendance_percentage = Column(Float, nullable=False)
    assessment_score = Column(Float, nullable=False)
    assignment_completion = Column(Float, nullable=False)
    engagement_metric = Column(Float, default=0.0, nullable=False)  # LMS logins
    recorded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        UniqueConstraint("student_id", "week_number", name="uq_student_week_metric"),
    )

    student = relationship("Student", back_populates="weekly_metrics")

class WeeklyAttendance(Base):
    """Weekly lecture attendance per course."""
    __tablename__ = "weekly_attendance"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), index=True, nullable=False)
    course_code = Column(String(32), index=True, nullable=False)
    week_number = Column(Integer, nullable=False, index=True)
    delivered = Column(Integer, nullable=False)
    attended = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("student_id", "course_code", "week_number", name="uq_student_course_week_att"),
    )

    student = relationship("Student", back_populates="weekly_attendance")

class WeeklyActivity(Base):
    """Weekly LMS digital engagement activity."""
    __tablename__ = "weekly_activity"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), index=True, nullable=False)
    week_number = Column(Integer, nullable=False, index=True)
    lms_logins_7d = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint("student_id", "week_number", name="uq_student_week_act"),
    )

    student = relationship("Student", back_populates="weekly_activity")
