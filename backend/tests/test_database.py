import pytest
from sqlalchemy.exc import IntegrityError
from backend.app.models.user import User
from backend.app.models.academic import Section, Mentor, Student, Subject
from backend.app.models.performance import StudentSubjectPerformance
from backend.app.core.security import get_password_hash, verify_password

def test_user_creation_and_password_hashing(test_db):
    pw = "SecretPass123"
    hashed = get_password_hash(pw)
    assert hashed.startswith("pbkdf2_sha256$")
    assert verify_password(pw, hashed) is True
    assert verify_password("wrong", hashed) is False

    user = User(
        username="testuser",
        email="test@lpu.in",
        full_name="Test Student",
        password_hash=hashed,
        role="student",
    )
    test_db.add(user)
    test_db.commit()

    queried = test_db.query(User).filter_by(username="testuser").first()
    assert queried is not None
    assert queried.role == "student"
    assert verify_password(pw, queried.password_hash) is True

def test_user_unique_constraint(test_db):
    u1 = User(username="dupe", email="dupe1@lpu.in", full_name="User 1", password_hash="h1", role="student")
    u2 = User(username="dupe", email="dupe2@lpu.in", full_name="User 2", password_hash="h2", role="student")
    test_db.add(u1)
    test_db.commit()

    test_db.add(u2)
    with pytest.raises(IntegrityError):
        test_db.commit()
    test_db.rollback()

def test_student_and_performance_relations(test_db):
    user = User(username="stu01", email="stu01@lpu.in", full_name="Student One", password_hash="h", role="student")
    test_db.add(user)
    sec = Section(section_code="K3P25IL")
    test_db.add(sec)
    subj = Subject(subject_code="CSE276", subject_name="AI Foundations", total_lectures=33)
    test_db.add(subj)
    test_db.commit()

    student = Student(
        user_id=user.id,
        registration_number="12511001",
        section="K3P25IL",
        academic_status="ON TRACK",
        sem2_sgpa=8.2,
    )
    test_db.add(student)
    test_db.commit()

    perf = StudentSubjectPerformance(
        student_id=student.id,
        subject_id=subj.id,
        delivered=33,
        attended=28,
        duty_leave=2,
        attendance_percentage=91.0,
        internal_marks=26.5,
        assignment_completion=100.0,
    )
    test_db.add(perf)
    test_db.commit()

    saved_student = test_db.query(Student).filter_by(registration_number="12511001").first()
    assert len(saved_student.subject_performances) == 1
    assert saved_student.subject_performances[0].subject.subject_code == "CSE276"
    assert saved_student.subject_performances[0].attendance_percentage == 91.0
