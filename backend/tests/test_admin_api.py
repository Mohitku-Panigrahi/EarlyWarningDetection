import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database.session import get_db
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


def test_admin_dashboard(client):
    # 1. Login as admin
    res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    assert res.status_code == 200
    token = res.json()["access_token"]

    # 2. Get dashboard
    dash_res = client.get("/api/v1/admin/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert dash_res.status_code == 200
    data = dash_res.json()

    assert data["kpi"]["total_monitored_students"] == 60
    assert len(data["section_distributions"]) == 3
    assert len(data["section_subject_heatmap"]) == 21  # 3 sections * 7 courses
    assert len(data["priority_signals"]) == 4


def test_admin_students_list_and_filters(client):
    res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    token = res.json()["access_token"]

    # Search by name
    s_res = client.get("/api/v1/admin/students?search=Aarav", headers={"Authorization": f"Bearer {token}"})
    assert s_res.status_code == 200
    s_data = s_res.json()
    assert s_data["total"] >= 1
    assert any("Aarav" in s["name"] for s in s_data["students"])

    # Filter by section
    sec_res = client.get("/api/v1/admin/students?section=K3P25IL", headers={"Authorization": f"Bearer {token}"})
    assert sec_res.status_code == 200
    assert sec_res.json()["total"] == 20

    # Filter by status
    stat_res = client.get("/api/v1/admin/students?status_filter=WATCH", headers={"Authorization": f"Bearer {token}"})
    assert stat_res.status_code == 200
    for s in stat_res.json()["students"]:
        assert s["academic_status"] == "WATCH"


def test_admin_mentor_analytics(client):
    res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    token = res.json()["access_token"]

    m_res = client.get("/api/v1/admin/mentor-analytics", headers={"Authorization": f"Bearer {token}"})
    assert m_res.status_code == 200
    mentors = m_res.json()
    assert len(mentors) == 6
    for m in mentors:
        assert m["assigned_mentees"] == 10


def test_admin_intervention_analytics(client):
    res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    token = res.json()["access_token"]

    inv_res = client.get("/api/v1/admin/intervention-analytics", headers={"Authorization": f"Bearer {token}"})
    assert inv_res.status_code == 200
    data = inv_res.json()
    assert data["total_interventions"] >= 1
    assert "by_type" in data


def test_admin_model_health(client):
    res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    token = res.json()["access_token"]

    mh_res = client.get("/api/v1/admin/model-health", headers={"Authorization": f"Bearer {token}"})
    assert mh_res.status_code == 200
    data = mh_res.json()
    assert data["threshold"] == 0.40
    assert data["metrics"]["recall"] >= 0.80
    assert len(data["calibration_curve"]) == 5
    assert len(data["recall_by_week"]) == 4


def test_admin_fairness_report(client):
    res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    token = res.json()["access_token"]

    fair_res = client.get("/api/v1/admin/fairness", headers={"Authorization": f"Bearer {token}"})
    assert fair_res.status_code == 200
    data = fair_res.json()
    assert len(data["admission_route"]) >= 2
    assert len(data["schooling_board"]) >= 2
    assert len(data["medium_of_instruction"]) >= 2
    assert len(data["home_region"]) >= 2


def test_admin_audit_logs(client):
    res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    token = res.json()["access_token"]

    log_res = client.get("/api/v1/admin/audit-logs", headers={"Authorization": f"Bearer {token}"})
    assert log_res.status_code == 200
    assert log_res.json()["total"] >= 1


def test_admin_system_settings_workflow(client):
    res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    token = res.json()["access_token"]

    # 1. Get settings
    get_res = client.get("/api/v1/admin/system-settings", headers={"Authorization": f"Bearer {token}"})
    assert get_res.status_code == 200
    assert len(get_res.json()) >= 5

    # 2. Update threshold setting
    put_res = client.put(
        "/api/v1/admin/system-settings",
        headers={"Authorization": f"Bearer {token}"},
        json={"settings": {"risk_decision_threshold": "0.42"}},
    )
    assert put_res.status_code == 200
    updated = next(s for s in put_res.json() if s["key"] == "risk_decision_threshold")
    assert updated["value"] == "0.42"


def test_non_admin_forbidden_on_admin_routes(client):
    # Mentor attempt -> 403 Forbidden
    m_res = client.post("/api/v1/auth/login", json={"username": "m08", "password": "mentor123"})
    m_token = m_res.json()["access_token"]
    res1 = client.get("/api/v1/admin/dashboard", headers={"Authorization": f"Bearer {m_token}"})
    assert res1.status_code == 403

    # Student attempt -> 403 Forbidden
    s_res = client.post("/api/v1/auth/login", json={"username": "12511001", "password": "demo123"})
    s_token = s_res.json()["access_token"]
    res2 = client.get("/api/v1/admin/dashboard", headers={"Authorization": f"Bearer {s_token}"})
    assert res2.status_code == 403
