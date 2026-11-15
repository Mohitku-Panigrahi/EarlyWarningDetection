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


def test_shap_explainability_bug_fix(client):
    """Verify Phase 1: SHAP attributes have feature_name, observed_value, impact_label, and explanation."""
    # Login as mentor m08 (mentor of student 1 and 4 in test_db)
    res = client.post("/api/v1/auth/login", json={"username": "m08", "password": "mentor123"})
    assert res.status_code == 200
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Fetch risk details for Aarav Sharma (student 1)
    res = client.get("/api/v1/mentor/mentees/1/risk", headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert "shap_waterfall" in data
    assert len(data["shap_waterfall"]) > 0

    for item in data["shap_waterfall"]:
        # Verify NO undefined, null or empty strings
        assert item["feature_name"] is not None and len(item["feature_name"]) > 0
        assert item["observed_value"] is not None and len(item["observed_value"]) > 0
        assert item["impact_label"] in ("Increases predicted risk", "Reduces predicted risk")
        assert item["explanation"] is not None and len(item["explanation"]) > 0
        assert isinstance(item["contribution"], float)
        assert item["direction"] in ("positive_risk", "negative_risk")


def test_mentor_cohort_analytics_endpoint(client):
    """Verify Phase 2: Cohort analytics overview endpoint."""
    res = client.post("/api/v1/auth/login", json={"username": "m08", "password": "mentor123"})
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/mentor/analytics", headers=headers)
    assert res.status_code == 200
    data = res.json()

    # Verify status distribution
    sd = data["status_distribution"]
    assert "on_track" in sd and "watch" in sd and "needs_review" in sd
    assert sum(sd.values()) == 10

    # Verify averages
    assert 50.0 <= data["avg_cohort_attendance"] <= 100.0
    assert 40.0 <= data["avg_cohort_assessment"] <= 100.0

    # Trajectory distribution
    td = data["trajectory_distribution"]
    assert "improving" in td and "stable" in td and "declining" in td
    assert sum(td.values()) == 10

    # Subject averages
    assert len(data["subject_averages"]) > 0
    for sa in data["subject_averages"]:
        assert sa["subject_code"] is not None
        assert sa["benchmark"] == 75.0
        assert 0.0 <= sa["cohort_avg"] <= 100.0


def test_mentee_academic_trajectory_endpoint(client):
    """Verify Phase 2: Student trajectory, OLS classification, and cohort comparison."""
    res = client.post("/api/v1/auth/login", json={"username": "m08", "password": "mentor123"})
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/mentor/mentees/1/trajectory", headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["student_id"] == 1
    assert data["trend_classification"] in ("Improving", "Declining", "Stable", "Insufficient Data")
    assert "OLS linear regression" in data["method_documentation"]

    # Weekly points (W1-W8)
    weekly = data["weekly_trajectory"]
    assert len(weekly) == 8
    # W1-W6 observed, W7-W8 projected
    assert all(not p["is_projected"] for p in weekly if p["week_number"] <= 6)
    assert all(p["is_projected"] for p in weekly if p["week_number"] > 6)

    # Subject trajectories
    subjs = data["subject_trajectories"]
    assert len(subjs) > 0
    for st in subjs:
        assert st["benchmark"] == 75.0
        assert st["trend"] in ("Improving", "Declining", "Stable")

    # Cohort comparison
    comp = data["comparison"]
    assert comp["institutional_attendance_goal"] == 85.0
    assert "N=10" in comp["sample_size_label"]


def test_intelligent_task_recommendation_lifecycle(client):
    """Verify Phase 3: Recommendation generation, approval into task, and deduplication."""
    res = client.post("/api/v1/auth/login", json={"username": "m08", "password": "mentor123"})
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Fetch recommendations
    res = client.get("/api/v1/mentor/recommendations", headers=headers)
    assert res.status_code == 200
    recs = res.json()
    assert len(recs) > 0

    first_rec = recs[0]
    rec_id = first_rec["id"]
    student_id = first_rec["student_id"]
    course_code = first_rec["course_code"]
    assert first_rec["recommended_title"] is not None
    assert first_rec["evidence"] is not None
    assert first_rec["priority"] in ("High", "Medium", "Low")

    # 2. Mentor approves the recommendation
    res = client.post(f"/api/v1/mentor/recommendations/{rec_id}/approve", headers=headers, json={
        "title": "Customized: " + first_rec["recommended_title"],
        "priority": "High"
    })
    assert res.status_code == 201
    task = res.json()
    assert task["student_id"] == student_id
    assert task["course_code"] == course_code
    assert task["source"] == "mentor"
    assert "Customized: " in task["title"]

    # 3. Deduplication check: Same recommendation should no longer appear in active recommendations
    res = client.get("/api/v1/mentor/recommendations", headers=headers)
    new_recs = res.json()
    assert not any(r["id"] == rec_id for r in new_recs)
