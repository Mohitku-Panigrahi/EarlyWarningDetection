import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database.session import get_db
from backend.app.services.student_import_service import StudentImportService
from backend.app.models.academic import Student

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


def test_student_dashboard_for_aarav(client):
    # 1. Login as Aarav Sharma
    res = client.post("/api/v1/auth/login", json={"username": "12511001", "password": "demo123"})
    assert res.status_code == 200
    token = res.json()["access_token"]

    # 2. Fetch dashboard
    dash_res = client.get("/api/v1/student/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert dash_res.status_code == 200
    data = dash_res.json()

    assert data["registration_number"] == "12511001"
    assert "Aarav" in data["name"]
    assert data["section"] == "K3P25IL"

    # KPI verification
    kpi = data["kpi"]
    assert kpi["academic_status"] == "WATCH"
    assert abs(kpi["attendance_percentage"] - 82.0) <= 0.5
    assert kpi["attendance_target"] == 85.0
    assert kpi["classes_to_safe"] >= 1
    assert abs(kpi["assignment_completion_pct"] - 76.0) <= 5.0

    # Weekly Trends (W1 to W8)
    trends = data["weekly_trends"]
    assert len(trends) == 8
    cur_point = next(p for p in trends if p["is_current"])
    assert cur_point["week_number"] == 6

    # Subject Performances
    subjs = data["subject_performances"]
    assert len(subjs) == 7
    mth = next(s for s in subjs if s["subject_code"] == "MTH401")
    assert mth is not None

    # Tasks
    tasks = data["tasks"]
    assert len(tasks) >= 4

    # Explanation factor cards
    exp = data["explanation"]
    assert exp["academic_status"] == "WATCH"
    assert len(exp["factors"]) >= 1
    assert len(exp["next_steps"]) == 3


def test_toggle_task(client):
    # Login as Aarav
    l_res = client.post("/api/v1/auth/login", json={"username": "12511001", "password": "demo123"})
    token = l_res.json()["access_token"]

    # Get tasks
    t_res = client.get("/api/v1/student/tasks", headers={"Authorization": f"Bearer {token}"})
    assert t_res.status_code == 200
    tasks = t_res.json()
    assert len(tasks) > 0
    target_task = tasks[0]

    # Toggle to completed
    patch_res = client.patch(
        f"/api/v1/student/tasks/{target_task['id']}",
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "completed"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "completed"

    # Toggle back to pending
    patch_res2 = client.patch(
        f"/api/v1/student/tasks/{target_task['id']}",
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "pending"},
    )
    assert patch_res2.status_code == 200
    assert patch_res2.json()["status"] == "pending"


def test_create_custom_task(client):
    l_res = client.post("/api/v1/auth/login", json={"username": "12511001", "password": "demo123"})
    token = l_res.json()["access_token"]

    create_res = client.post(
        "/api/v1/student/tasks",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "Prepare Chapter 4 Formula Sheet", "course_code": "MTH401", "priority": "Medium"},
    )
    assert create_res.status_code == 201
    created = create_res.json()
    assert created["title"] == "Prepare Chapter 4 Formula Sheet"
    assert created["status"] == "pending"


def test_mentor_access_and_isolation(client, module_test_db):
    # Login as mentor m08
    m_res = client.post("/api/v1/auth/login", json={"username": "m08", "password": "mentor123"})
    m_token = m_res.json()["access_token"]

    # Aarav is assigned to m08 -> access allowed
    aarav = module_test_db.query(Student).filter_by(registration_number="12511001").first()
    res1 = client.get(f"/api/v1/student/dashboard?student_id={aarav.id}", headers={"Authorization": f"Bearer {m_token}"})
    assert res1.status_code == 200
    assert res1.json()["student_id"] == aarav.id

    # Find a student not assigned to m08
    other = module_test_db.query(Student).filter(Student.mentor_id != aarav.mentor_id).first()
    assert other is not None

    # Accessing other student -> 403 Forbidden
    res2 = client.get(f"/api/v1/student/dashboard?student_id={other.id}", headers={"Authorization": f"Bearer {m_token}"})
    assert res2.status_code == 403
