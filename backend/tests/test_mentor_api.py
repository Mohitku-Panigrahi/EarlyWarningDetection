import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database.session import get_db
from backend.app.services.student_import_service import StudentImportService
from backend.app.models.academic import Student
from backend.app.models.intervention import Intervention, StudentTask

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


def test_mentor_dashboard_kpis_and_cohort(client):
    # 1. Login as mentor m08
    m_res = client.post("/api/v1/auth/login", json={"username": "m08", "password": "mentor123"})
    assert m_res.status_code == 200
    token = m_res.json()["access_token"]

    # 2. Get mentor dashboard
    dash_res = client.get("/api/v1/mentor/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert dash_res.status_code == 200
    data = dash_res.json()

    assert data["faculty_code"] == "F08"
    assert "Manoj Saini" in data["mentor_name"]

    # KPI verification: exactly 10 mentees
    kpi = data["kpi"]
    assert kpi["total_mentees"] == 10
    assert (kpi["on_track_count"] + kpi["watch_count"] + kpi["review_count"]) == 10

    # Priority Action Queue
    assert len(data["priority_queue"]) >= 1

    # Mentee Roster: 10 items
    assert len(data["mentees"]) == 10


def test_explainability_drawer_payload(client, module_test_db):
    m_res = client.post("/api/v1/auth/login", json={"username": "m08", "password": "mentor123"})
    token = m_res.json()["access_token"]

    aarav = module_test_db.query(Student).filter_by(registration_number="12511001").first()
    risk_res = client.get(f"/api/v1/mentor/mentees/{aarav.id}/risk", headers={"Authorization": f"Bearer {token}"})
    assert risk_res.status_code == 200
    risk_data = risk_res.json()

    assert risk_data["registration_number"] == "12511001"
    assert risk_data["academic_status"] == "WATCH"

    # SHAP Waterfall
    shap = risk_data["shap_waterfall"]
    assert len(shap) >= 3
    features = [s["feature"] for s in shap]
    assert any("MTH401" in f for f in features)

    # Rule Trace
    rules = risk_data["rules_fired"]
    assert len(rules) >= 1
    assert any(r["rule_id"] == "R1" for r in rules)

    # Counterfactual
    cf = risk_data["counterfactual"]
    assert "attendance" in cf["scenario"].lower()
    assert len(cf["target_actions"]) >= 1

    # Bayesian Reasoning
    bayes = risk_data["bayesian"]
    assert bayes["prior"] == 0.22
    assert bayes["posterior"] > bayes["prior"]


def test_mentor_workload_telemetry(client):
    m_res = client.post("/api/v1/auth/login", json={"username": "m08", "password": "mentor123"})
    token = m_res.json()["access_token"]

    workload_res = client.get("/api/v1/mentor/workload", headers={"Authorization": f"Bearer {token}"})
    assert workload_res.status_code == 200
    w_data = workload_res.json()
    assert w_data["faculty_code"] == "F08"
    assert w_data["current_mentees"] == 10
    assert w_data["workload_cap"] == 10
    assert w_data["utilization_pct"] == 100.0


def test_human_in_the_loop_intervention_workflow(client, module_test_db):
    m_res = client.post("/api/v1/auth/login", json={"username": "m08", "password": "mentor123"})
    token = m_res.json()["access_token"]

    aarav = module_test_db.query(Student).filter_by(registration_number="12511001").first()

    # 1. Propose intervention
    create_res = client.post(
        "/api/v1/interventions",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "student_id": aarav.id,
            "intervention_type": "Subject Tutoring & Practice",
            "recommendation": "Weekly 30-min Discrete Math tutoring sessions",
            "reason": "Calculus marks drop (-18%) detected in Continuous Assessment",
            "priority": "High",
            "playbook_id": "PB01",
        },
    )
    assert create_res.status_code == 201
    interv_id = create_res.json()["id"]
    assert create_res.json()["status"] == "proposed"

    # 2. Approve intervention (Mentor Human-in-the-Loop decision)
    appr_res = client.post(
        f"/api/v1/interventions/{interv_id}/approve",
        headers={"Authorization": f"Bearer {token}"},
        json={"comments": "Approved after reviewing SHAP waterfall and meeting with student."},
    )
    assert appr_res.status_code == 200
    assert appr_res.json()["status"] == "approved"
    assert len(appr_res.json()["decisions"]) == 1

    # 3. Verify task spawned on student dashboard
    student_tasks = module_test_db.query(StudentTask).filter_by(student_id=aarav.id).all()
    assert any("Discrete Math" in t.title or "Tutoring" in t.title for t in student_tasks)

    # 4. Complete intervention
    comp_res = client.post(
        f"/api/v1/interventions/{interv_id}/complete",
        headers={"Authorization": f"Bearer {token}"},
        json={"comments": "Student attended 2 sessions; marks improved."},
    )
    assert comp_res.status_code == 200
    assert comp_res.json()["status"] == "completed"
    assert len(comp_res.json()["decisions"]) == 2


def test_rejection_workflow(client, module_test_db):
    m_res = client.post("/api/v1/auth/login", json={"username": "m08", "password": "mentor123"})
    token = m_res.json()["access_token"]
    aarav = module_test_db.query(Student).filter_by(registration_number="12511001").first()

    # Propose
    create_res = client.post(
        "/api/v1/interventions",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "student_id": aarav.id,
            "intervention_type": "Schedule Revision",
            "recommendation": "Shift lecture timing",
            "reason": "Minor attendance variance",
            "priority": "Low",
        },
    )
    assert create_res.status_code == 201
    interv_id = create_res.json()["id"]

    # Reject
    rej_res = client.post(
        f"/api/v1/interventions/{interv_id}/reject",
        headers={"Authorization": f"Bearer {token}"},
        json={"comments": "Not viable due to department laboratory conflicts."},
    )
    assert rej_res.status_code == 200
    assert rej_res.json()["status"] == "rejected"
    assert len(rej_res.json()["decisions"]) == 1


def test_student_cannot_access_mentor_endpoints(client):
    stu_res = client.post("/api/v1/auth/login", json={"username": "12511001", "password": "demo123"})
    s_token = stu_res.json()["access_token"]

    res = client.get("/api/v1/mentor/dashboard", headers={"Authorization": f"Bearer {s_token}"})
    assert res.status_code == 403
