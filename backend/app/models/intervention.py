from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.database.session import Base

class Playbook(Base):
    """Intervention recommendation catalog."""
    __tablename__ = "playbook"

    id = Column(String(32), primary_key=True)  # e.g. PB01
    course_code = Column(String(32), nullable=False)
    trigger = Column(String(64), nullable=False)  # low_marks, low_attendance, etc.
    topic = Column(String(128), nullable=False)
    task_text = Column(Text, nullable=False)
    estimated_minutes = Column(Integer, default=30, nullable=False)

class Intervention(Base):
    """Interventions recommended by the planner or proposed by mentor."""
    __tablename__ = "interventions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), index=True, nullable=False)
    mentor_id = Column(Integer, ForeignKey("mentors.id"), index=True, nullable=False)
    playbook_id = Column(String(32), ForeignKey("playbook.id"), nullable=True)
    
    intervention_type = Column(String(64), nullable=False)  # Tutoring, Attendance Recovery, Counseling, Submission Extension
    recommendation = Column(Text, nullable=False)
    reason = Column(Text, nullable=False)
    priority = Column(String(32), default="Medium", nullable=False)  # High, Medium, Low
    status = Column(String(32), default="proposed", nullable=False)  # proposed, approved, rejected, in_progress, completed
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    student = relationship("Student", back_populates="interventions")
    mentor = relationship("Mentor", back_populates="interventions")
    decisions = relationship("MentorDecision", back_populates="intervention", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Intervention {self.id} for Student {self.student_id} ({self.status})>"

class MentorDecision(Base):
    """Audit trail of human mentor intervention reviews."""
    __tablename__ = "mentor_decisions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    intervention_id = Column(Integer, ForeignKey("interventions.id", ondelete="CASCADE"), index=True, nullable=False)
    mentor_id = Column(Integer, ForeignKey("mentors.id"), index=True, nullable=False)
    decision = Column(String(32), nullable=False)  # approved, rejected, modified, completed
    comments = Column(Text, nullable=True)
    decided_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    intervention = relationship("Intervention", back_populates="decisions")
    mentor = relationship("Mentor", back_populates="decisions")

class StudentTask(Base):
    """Personalized learning and recovery tasks displayed on the student dashboard."""
    __tablename__ = "student_tasks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), index=True, nullable=False)
    course_code = Column(String(32), nullable=True)
    source = Column(String(32), default="playbook", nullable=False)  # playbook, mentor, custom
    playbook_id = Column(String(32), nullable=True)
    title = Column(String(256), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(String(32), default="Medium", nullable=False)  # High, Medium, Low
    status = Column(String(32), default="pending", nullable=False)  # pending, completed
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    done_at = Column(DateTime, nullable=True)

    student = relationship("Student", back_populates="tasks")

class MentorMeeting(Base):
    """Formal record of mentoring sessions conducted between a faculty mentor and student."""
    __tablename__ = "mentor_meetings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    mentor_id = Column(Integer, ForeignKey("mentors.id", ondelete="CASCADE"), index=True, nullable=False)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), index=True, nullable=False)
    meeting_date = Column(DateTime, nullable=False)
    meeting_type = Column(String(32), default="In Person", nullable=False)  # In Person, Online, Phone
    duration_minutes = Column(Integer, default=30, nullable=False)
    discussion_summary = Column(Text, nullable=False)
    academic_concerns = Column(Text, nullable=True)
    agreed_actions = Column(Text, nullable=True)
    next_followup_date = Column(DateTime, nullable=True)
    meeting_status = Column(String(32), default="completed", nullable=False)  # completed, scheduled, cancelled
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    mentor = relationship("Mentor", back_populates="meetings")
    student = relationship("Student", back_populates="meetings")

    def __repr__(self):
        return f"<MentorMeeting {self.id}: Mentor {self.mentor_id} with Student {self.student_id}>"

