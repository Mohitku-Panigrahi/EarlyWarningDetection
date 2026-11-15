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

def test_full_task_lifecycle_and_security(client: TestClient):
    # Login Mentor Dr. Manoj Saini (m08, mentor of Arjun Gupta student_id=4)
    res_m = client.post("/api/v1/auth/login", json={"username": "m08", "password": "mentor123"})
    assert res_m.status_code == 200
    m_token = res_m.json()["access_token"]
    m_headers = {"Authorization": f"Bearer {m_token}"}

    # Login Student Arjun Gupta (12511004)
    res_s = client.post("/api/v1/auth/login", json={"username": "12511004", "password": "demo123"})
    assert res_s.status_code == 200
    s_token = res_s.json()["access_token"]
    s_headers = {"Authorization": f"Bearer {s_token}"}

    # 1. Student creates personal task
    res = client.post("/api/v1/student/tasks", headers=s_headers, json={
        "title": "Practice Graph Traversal (BFS & DFS)",
        "description": "Solve 10 problems on adjacency list implementation",
        "course_code": "CSE205",
        "priority": "High"
    })
    assert res.status_code == 201
    p_task = res.json()
    assert p_task["source"] == "student"

    # 2. Mentor assigns academic task to mentee (student_id=4)
    res = client.post("/api/v1/mentor/tasks", headers=m_headers, json={
        "student_id": 4,
        "course_code": "MTH401",
        "title": "Complete Discrete Mathematics Unit 3 Practice",
        "description": "Complete problem set from Unit 3 and review before Friday session.",
        "priority": "High"
    })
    assert res.status_code == 201
    m_task = res.json()
    assert m_task["source"] == "mentor"
    assert m_task["course_code"] == "MTH401"

    # 3. Student views mentor-assigned tasks
    res = client.get("/api/v1/student/tasks?filter_type=mentor_assigned", headers=s_headers)
    assert res.status_code == 200
    assigned_tasks = res.json()
    assert any(t["id"] == m_task["id"] for t in assigned_tasks)

    # 4. Student updates status to in_progress
    res = client.patch(f"/api/v1/student/tasks/{m_task['id']}", headers=s_headers, json={
        "status": "in_progress"
    })
    assert res.status_code == 200
    assert res.json()["status"] == "in_progress"

    # 5. Mentor observes updated status
    res = client.get("/api/v1/mentor/tasks?student_id=4", headers=m_headers)
    assert res.status_code == 200
    m_tasks = res.json()
    assert any(t["id"] == m_task["id"] and t["status"] == "in_progress" for t in m_tasks)

    # 6. Security: Student cannot modify mentor task instructions
    res = client.patch(f"/api/v1/student/tasks/{m_task['id']}", headers=s_headers, json={
        "title": "Tampered Title"
    })
    assert res.status_code == 403

    # 7. Security: Student cannot delete mentor-assigned task
    res = client.delete(f"/api/v1/student/tasks/{m_task['id']}", headers=s_headers)
    assert res.status_code == 403

    # 8. Student can delete own personal task
    res = client.delete(f"/api/v1/student/tasks/{p_task['id']}", headers=s_headers)
    assert res.status_code == 200

    # 9. Security: Mentor cannot assign tasks to students outside their cohort
    res = client.post("/api/v1/mentor/tasks", headers=m_headers, json={
        "student_id": 2,  # Belongs to mentor_id=3, not m08 (mentor_id=1)
        "title": "Cross-Cohort Assignment",
        "priority": "High"
    })
    assert res.status_code == 403
