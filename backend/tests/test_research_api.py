import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_get_search_graph(client):
    res = client.get("/api/v1/research/search/graph")
    assert res.status_code == 200
    data = res.json()
    assert "states" in data
    assert "transitions" in data
    assert len(data["states"]) == 8

def test_execute_search_algorithm_bfs(client):
    res = client.post("/api/v1/research/search/execute", json={
        "algorithm": "BFS",
        "start_state": "INITIAL_REVIEW",
        "goal_state": "PLAN_COMPLETED",
    })
    assert res.status_code == 200
    data = res.json()
    assert data["completion_status"] == "SUCCESS"
    assert data["path"][0] == "INITIAL_REVIEW"
    assert data["path"][-1] == "PLAN_COMPLETED"

def test_execute_search_algorithm_a_star(client):
    res = client.post("/api/v1/research/search/execute", json={
        "algorithm": "A*",
        "start_state": "INITIAL_REVIEW",
        "goal_state": "PLAN_COMPLETED",
    })
    assert res.status_code == 200
    data = res.json()
    assert data["completion_status"] == "SUCCESS"
    assert data["path_cost"] > 0
    assert "node_evaluations" in data

def test_search_comparison(client):
    res = client.get("/api/v1/research/search/comparison")
    assert res.status_code == 200
    data = res.json()
    assert len(data["comparison"]) == 5

def test_knowledge_evaluate(client):
    res = client.post("/api/v1/research/knowledge/evaluate", json={
        "student_id": "12511001",
        "name": "Aarav Sharma",
        "attendance_pct": 68.0,
        "marks_drop_pct": 14.0,
        "missing_count": 3,
        "recent_trend": "declining",
    })
    assert res.status_code == 200
    data = res.json()
    assert data["predicates"]["LowAttendance"] is True
    assert data["predicates"]["NeedsMentorReview"] is True
    assert data["active_rules_count"] >= 3

def test_truth_table(client):
    res = client.get("/api/v1/research/knowledge/truth-table")
    assert res.status_code == 200
    data = res.json()
    assert data["total_rows"] == 16
    assert data["is_satisfiable"] is True

def test_bayesian_update(client):
    res = client.post("/api/v1/research/bayesian/update", json={
        "has_low_attendance": True,
        "has_low_marks": True,
        "has_overdue_work": False,
        "prior": 0.22,
    })
    assert res.status_code == 200
    data = res.json()
    assert data["posterior"] > 0.22
    assert data["is_normalized"] is True

def test_model_comparison(client):
    res = client.get("/api/v1/research/models/comparison")
    assert res.status_code == 200
    data = res.json()
    assert len(data["models"]) == 4
    assert "k_means_segmentation" in data
