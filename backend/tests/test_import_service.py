import pytest
from backend.app.services.student_import_service import StudentImportService
from backend.app.models.academic import Student, Mentor
from backend.app.models.user import User
from backend.app.models.performance import StudentSubjectPerformance
from backend.app.models.risk import RiskAssessment
from backend.app.models.intervention import StudentTask

def test_full_import_pipeline(test_db):
    report = StudentImportService.import_dataset(test_db, force_reload=True)
    assert report["total_detected"] == 60
    assert report["imported"] == 60
    assert report["rejected"] == 0
    assert len(report["validation_errors"]) == 0

    # Verify student count
    count = test_db.query(Student).count()
    assert count == 60

    # Verify sections distribution (20 per section)
    for sec in ["K3P25IL", "K3P25IM", "K3P25IN"]:
        sec_count = test_db.query(Student).filter_by(section=sec).count()
        assert sec_count == 20

    # Verify mentor workload (6 mentors, each exactly 10 mentees)
    mentors = test_db.query(Mentor).all()
    assert len(mentors) == 6
    for m in mentors:
        mentee_count = test_db.query(Student).filter_by(mentor_id=m.id).count()
        assert mentee_count == 10

def test_idempotence(test_db):
    # First run
    report1 = StudentImportService.import_dataset(test_db, force_reload=False)
    assert report1["imported"] == 60

    # Second run without force_reload should NOT import new rows
    report2 = StudentImportService.import_dataset(test_db, force_reload=False)
    assert report2["imported"] == 0
    assert report2["updated"] == 60
    assert report2["idempotent"] is True

    # Count must remain 60
    assert test_db.query(Student).count() == 60

def test_aarav_sharma_persona(test_db):
    StudentImportService.import_dataset(test_db, force_reload=True)
    aarav = test_db.query(Student).filter_by(registration_number="12511001").first()
    assert aarav is not None
    assert aarav.user.full_name == "Aarav Sharma"
    assert aarav.academic_status == "WATCH"
    assert aarav.section == "K3P25IL"

    # Verify risk assessment
    ra = test_db.query(RiskAssessment).filter_by(student_id=aarav.id).first()
    assert ra is not None
    assert ra.status == "WATCH"
    assert "MTH401 Assessment Drop" in ra.shap_json
    assert "R1" in ra.rules_fired

    # Verify tasks seeded for Aarav
    tasks = test_db.query(StudentTask).filter_by(student_id=aarav.id).all()
    assert len(tasks) >= 4
    task_titles = [t.title for t in tasks]
    assert any("Differential Calculus" in t for t in task_titles)
