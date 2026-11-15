import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database.session import get_db
from backend.app.models.system import AuditLog
from backend.app.services.student_import_service import StudentImportService

@pytest.fixture(scope="module")
def client(module_test_db):
    StudentImportService.import_dataset(module_test_db, force_reload=True)

    def override_get_db():
        try:
            yield module_test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_mentor_meeting_logging_and_cohort_isolation(client):
    """Verify mentor can log meetings for assigned student and is blocked for cross-cohort."""
    # Login as mentor m08 (mentor of student 1)
    res = client.post("/api/v1/auth/login", json={"username": "m08", "password": "mentor123"})
    assert res.status_code == 200
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Attempt cross-cohort meeting logging (student 2 is assigned to mentor 3)
    meeting_payload_cross = {
        "student_id": 2,
        "meeting_date": datetime.now(timezone.utc).isoformat(),
        "meeting_type": "In Person",
        "duration_minutes": 30,
        "discussion_summary": "Discussing mid-term recovery",
    }
    res_cross = client.post("/api/v1/mentor/meetings", json=meeting_payload_cross, headers=headers)
    assert res_cross.status_code == 403
    assert "outside your assigned mentorship cohort" in res_cross.json()["detail"]

    # 2. Record valid meeting for student 1 (in mentor 1's cohort)
    meeting_payload_valid = {
        "student_id": 1,
        "meeting_date": datetime.now(timezone.utc).isoformat(),
        "meeting_type": "In Person",
        "duration_minutes": 45,
        "discussion_summary": "In-depth review of Discrete Mathematics assessment deficits.",
        "academic_concerns": "MTH401 Quiz 1 score was 54%; student struggling with Recurrence Relations.",
        "agreed_actions": "Complete practice problem set 4.2 by Friday and attend tutorial session.",
        "next_followup_date": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
        "meeting_status": "completed",
    }
    res_valid = client.post("/api/v1/mentor/meetings", json=meeting_payload_valid, headers=headers)
    assert res_valid.status_code == 201
    m_data = res_valid.json()
    assert m_data["id"] is not None
    assert m_data["student_id"] == 1
    assert m_data["duration_minutes"] == 45
    assert m_data["followup_status"] == "Upcoming"
    meeting_id = m_data["id"]

    # 3. List mentor's meetings
    res_list = client.get("/api/v1/mentor/meetings", headers=headers)
    assert res_list.status_code == 200
    m_list = res_list.json()
    assert len(m_list) >= 1
    assert any(m["id"] == meeting_id for m in m_list)

    # 4. Update meeting agreed actions
    patch_payload = {
        "agreed_actions": "Updated action: Complete 15 differential equations problems.",
    }
    res_patch = client.patch(f"/api/v1/mentor/meetings/{meeting_id}", json=patch_payload, headers=headers)
    assert res_patch.status_code == 200
    assert "differential equations" in res_patch.json()["agreed_actions"]


def test_admin_governance_overview_and_rbac(client):
    """Verify Admin governance overview metrics, attention queue, and RBAC rejection of mentors/students."""
    # Login as student (s1) -> blocked from admin governance
    res_s = client.post("/api/v1/auth/login", json={"username": "12511001", "password": "student123"})
    if res_s.status_code == 200:
        s_headers = {"Authorization": f"Bearer {res_s.json()['access_token']}"}
        res_blocked = client.get("/api/v1/admin/governance/overview", headers=s_headers)
        assert res_blocked.status_code == 403

    # Login as mentor (m08) -> blocked from admin governance
    res_m = client.post("/api/v1/auth/login", json={"username": "m08", "password": "mentor123"})
    assert res_m.status_code == 200
    m_headers = {"Authorization": f"Bearer {res_m.json()['access_token']}"}
    res_m_blocked = client.get("/api/v1/admin/governance/overview", headers=m_headers)
    assert res_m_blocked.status_code == 403

    # Login as admin
    res_a = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    assert res_a.status_code == 200
    admin_token = res_a.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Governance Overview
    res_gov = client.get("/api/v1/admin/governance/overview", headers=admin_headers)
    assert res_gov.status_code == 200
    gov_data = res_gov.json()

    assert gov_data["total_active_mentors"] == 6
    assert gov_data["total_assigned_students"] == 60
    assert gov_data["students_with_active_support"] >= 1
    assert "attention_queue" in gov_data
    assert len(gov_data["attention_queue"]) > 0


def test_admin_mentor_workload_and_distribution(client):
    """Verify mentor workload capacity and student support distribution endpoints."""
    res_a = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    admin_headers = {"Authorization": f"Bearer {res_a.json()['access_token']}"}

    # Workload
    res_w = client.get("/api/v1/admin/governance/mentor-workload", headers=admin_headers)
    assert res_w.status_code == 200
    w_data = res_w.json()
    assert len(w_data) == 6
    for item in w_data:
        assert item["assigned_students"] == 10
        assert item["max_quota"] == 10
        assert item["allocated_percentage"] == 100.0

    # Student Distribution (On Track / Watch / Needs Review)
    res_d = client.get("/api/v1/admin/governance/student-distribution", headers=admin_headers)
    assert res_d.status_code == 200
    d_data = res_d.json()
    assert len(d_data) == 6
    for item in d_data:
        assert item["total_students"] == 10
        assert (item["on_track_count"] + item["watch_count"] + item["needs_review_count"]) == 10


def test_admin_mentor_directory_and_profiles(client):
    """Verify mentor directory and 4-group governance profile."""
    res_a = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    admin_headers = {"Authorization": f"Bearer {res_a.json()['access_token']}"}

    # Directory
    res_dir = client.get("/api/v1/admin/governance/mentors", headers=admin_headers)
    assert res_dir.status_code == 200
    dir_data = res_dir.json()
    assert len(dir_data) == 6
    m1 = dir_data[0]
    assert m1["assigned_students"] == 10
    assert m1["faculty_code"] is not None

    # Individual Profile for Mentor 1
    res_prof = client.get("/api/v1/admin/governance/mentors/1", headers=admin_headers)
    assert res_prof.status_code == 200
    prof = res_prof.json()

    assert prof["mentor_id"] == 1
    assert prof["total_assigned_students"] == 10
    assert 50.0 <= prof["avg_attendance_pct"] <= 100.0
    assert 40.0 <= prof["avg_assessment_pct"] <= 100.0
    assert "cohort_status_distribution" in prof
    assert "meeting_frequency_weekly" in prof


def test_admin_student_mentor_relationships_and_drawer(client):
    """Verify student-mentor relationship table and deep student governance profile drawer."""
    res_a = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    admin_headers = {"Authorization": f"Bearer {res_a.json()['access_token']}"}

    # Relationships matrix
    res_rel = client.get("/api/v1/admin/governance/relationships?page=1&page_size=10", headers=admin_headers)
    assert res_rel.status_code == 200
    rel_data = res_rel.json()
    assert rel_data["total"] == 60
    assert len(rel_data["relationships"]) == 10

    first_rel = rel_data["relationships"][0]
    assert first_rel["student_name"] is not None
    assert first_rel["registration_number"] is not None
    assert first_rel["mentor_name"] is not None
    assert first_rel["academic_status"] in ("ON TRACK", "WATCH", "NEEDS REVIEW")

    # Student Governance Drawer (Student 1)
    res_stu = client.get("/api/v1/admin/governance/students/1/governance", headers=admin_headers)
    assert res_stu.status_code == 200
    stu_data = res_stu.json()
    assert stu_data["student_id"] == 1
    assert "observed_trajectory" in stu_data
    assert "projected_trajectory" in stu_data
    assert "weak_subjects" in stu_data
    assert "meetings" in stu_data


def test_admin_meeting_monitoring_and_followups(client):
    """Verify meeting analytics, meeting listings, and follow-up queue."""
    res_a = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    admin_headers = {"Authorization": f"Bearer {res_a.json()['access_token']}"}

    # Analytics
    res_an = client.get("/api/v1/admin/governance/meetings/analytics", headers=admin_headers)
    assert res_an.status_code == 200
    an_data = res_an.json()
    assert an_data["total_meetings"] >= 1
    assert "meetings_by_mentor" in an_data
    assert "meetings_by_modality" in an_data

    # Meeting list
    res_list = client.get("/api/v1/admin/governance/meetings", headers=admin_headers)
    assert res_list.status_code == 200
    assert res_list.json()["total"] >= 1

    # Follow-up queue
    res_fol = client.get("/api/v1/admin/governance/followups", headers=admin_headers)
    assert res_fol.status_code == 200
    fol_data = res_fol.json()
    assert len(fol_data) >= 1
    assert fol_data[0]["status"] in ("Upcoming", "Overdue")


def test_admin_intervention_oversight_and_review_action(client):
    """Verify administrative intervention oversight and review note action with audit logging."""
    res_a = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    admin_headers = {"Authorization": f"Bearer {res_a.json()['access_token']}"}

    # Interventions list
    res_inv = client.get("/api/v1/admin/governance/interventions", headers=admin_headers)
    assert res_inv.status_code == 200
    inv_data = res_inv.json()
    assert len(inv_data) > 0

    first_inv = inv_data[0]
    inv_id = first_inv["id"]

    # Administrative Review Action
    review_payload = {
        "action": "add_administrative_note",
        "note": "Dean's office noted: Intervention aligns with MTH401 continuous assessment score dip.",
    }
    res_rev = client.post(f"/api/v1/admin/governance/interventions/{inv_id}/review", json=review_payload, headers=admin_headers)
    assert res_rev.status_code == 200
    assert res_rev.json()["status"] == "success"
