from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.database.session import Base

class Section(Base):
    __tablename__ = "sections"

    id = Column(Integer, primary_key=True, autoincrement=True)
    section_code = Column(String(32), unique=True, index=True, nullable=False)
    department = Column(String(64), default="Computer Science & Engineering")

    students = relationship("Student", back_populates="section_rel")

class Mentor(Base):
    __tablename__ = "mentors"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    faculty_code = Column(String(32), unique=True, index=True, nullable=False)  # e.g. F08
    department = Column(String(64), default="Computer Science & Engineering", nullable=False)
    designation = Column(String(64), default="Assistant Professor", nullable=False)
    workload_cap = Column(Integer, default=10, nullable=False)

    # Relationships
    user = relationship("User", back_populates="mentor_profile")
    students = relationship("Student", back_populates="mentor", foreign_keys="Student.mentor_id")
    interventions = relationship("Intervention", back_populates="mentor")
    decisions = relationship("MentorDecision", back_populates="mentor")
    meetings = relationship("MentorMeeting", back_populates="mentor", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Mentor {self.faculty_code}>"

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    registration_number = Column(String(32), unique=True, index=True, nullable=False)  # e.g. 12511001
    department = Column(String(64), default="Computer Science & Engineering", nullable=False)
    programme = Column(String(64), default="B.Tech Computer Science & Engineering", nullable=False)
    semester = Column(Integer, default=4, nullable=False)
    section = Column(String(32), ForeignKey("sections.section_code"), index=True, nullable=False)
    admission_year = Column(Integer, default=2024, nullable=False)
    mentor_id = Column(Integer, ForeignKey("mentors.id"), index=True, nullable=True)
    academic_status = Column(String(32), default="ON TRACK", nullable=False)  # ON TRACK, WATCH, NEEDS REVIEW
    
    # LPU Synthetic demographic and fairness attributes
    sem2_sgpa = Column(Float, nullable=True)
    cgpa_band = Column(String(16), nullable=True)  # <6, 6-8, 8+
    admission_route = Column(String(32), nullable=True)  # LPUNEST, JEE Main, State CET, Board Merit
    schooling_board = Column(String(32), nullable=True)  # CBSE, State Board, ICSE
    medium_of_instruction = Column(String(32), nullable=True)  # English, Hindi, Regional
    home_region = Column(String(32), nullable=True)  # North, East, South, West, Northeast

    # Relationships
    user = relationship("User", back_populates="student_profile")
    mentor = relationship("Mentor", back_populates="students", foreign_keys=[mentor_id])
    section_rel = relationship("Section", back_populates="students")
    
    subject_performances = relationship("StudentSubjectPerformance", back_populates="student", cascade="all, delete-orphan")
    academic_records = relationship("AcademicRecord", back_populates="student", cascade="all, delete-orphan")
    weekly_metrics = relationship("WeeklyAcademicMetric", back_populates="student", cascade="all, delete-orphan")
    weekly_attendance = relationship("WeeklyAttendance", back_populates="student", cascade="all, delete-orphan")
    weekly_activity = relationship("WeeklyActivity", back_populates="student", cascade="all, delete-orphan")
    assessments = relationship("StudentAssessment", back_populates="student", cascade="all, delete-orphan")
    risk_assessments = relationship("RiskAssessment", back_populates="student", cascade="all, delete-orphan")
    interventions = relationship("Intervention", back_populates="student", cascade="all, delete-orphan")
    tasks = relationship("StudentTask", back_populates="student", cascade="all, delete-orphan")
    meetings = relationship("MentorMeeting", back_populates="student", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Student {self.registration_number}>"

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    subject_code = Column(String(32), unique=True, index=True, nullable=False)  # e.g. CSE276
    subject_name = Column(String(128), nullable=False)
    semester = Column(Integer, default=4, nullable=False)
    credits = Column(Integer, default=3, nullable=False)
    total_lectures = Column(Integer, default=33, nullable=False)
    teacher_id = Column(String(32), nullable=True)  # E.g. F01-F07

    # Relationships
    performances = relationship("StudentSubjectPerformance", back_populates="subject", cascade="all, delete-orphan")
    assessments = relationship("Assessment", back_populates="subject", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Subject {self.subject_code}: {self.subject_name}>"
