import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database.session import get_db
from backend.app.services.student_import_service import StudentImportService

@pytest.fixture(scope="module")
def client(module_test_db):
    """Test client using the module-scoped populated test database."""
    # Seed test database once for the entire module
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


def test_health_endpoints(client):
    r1 = client.get("/api/v1/health")
    assert r1.status_code == 200
    assert r1.json()["status"] == "healthy"

    r2 = client.get("/api/v1/health/database")
    assert r2.status_code == 200
    assert r2.json()["status"] == "connected"

    r3 = client.get("/api/v1/system/info")
    assert r3.status_code == 200
    assert r3.json()["cohort"]["total_students"] == 60


def test_login_student(client):
    res = client.post("/api/v1/auth/login", json={"username": "12511001", "password": "demo123"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["role"] == "student"
    assert data["username"] == "12511001"
    assert data["full_name"] == "Aarav Sharma"


def test_login_mentor(client):
    res = client.post("/api/v1/auth/login", json={"username": "m08", "password": "mentor123"})
    assert res.status_code == 200
    data = res.json()
    assert data["role"] == "mentor"
    assert data["username"] == "m08"


def test_login_admin(client):
    res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    assert res.status_code == 200
    data = res.json()
    assert data["role"] == "admin"


def test_login_invalid_password(client):
    res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "wrongpassword"})
    assert res.status_code == 401
    assert "Incorrect" in res.json()["detail"]


def test_get_me_student(client):
    # Login as student
    l_res = client.post("/api/v1/auth/login", json={"username": "12511001", "password": "demo123"})
    token = l_res.json()["access_token"]

    # Call /me
    res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    me = res.json()
    assert me["username"] == "12511001"
    assert me["role"] == "student"
    assert me["profile"]["registration_number"] == "12511001"
    assert me["profile"]["academic_status"] == "WATCH"


def test_unauthenticated_request(client):
    res = client.get("/api/v1/auth/me")
    assert res.status_code == 401


def test_forged_token(client):
    res = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer forged.invalid.token"})
    assert res.status_code == 401


def test_profile_update(client):
    l_res = client.post("/api/v1/auth/login", json={"username": "12511001", "password": "demo123"})
    token = l_res.json()["access_token"]

    up_res = client.put(
        "/api/v1/auth/profile",
        headers={"Authorization": f"Bearer {token}"},
        json={"full_name": "Aarav Sharma (Updated)"},
    )
    assert up_res.status_code == 200
    assert up_res.json()["full_name"] == "Aarav Sharma (Updated)"


def test_change_password_workflow(client):
    # Use mentor m09 for password change test
    l_res = client.post("/api/v1/auth/login", json={"username": "m09", "password": "mentor123"})
    token = l_res.json()["access_token"]

    # Change password
    ch_res = client.post(
        "/api/v1/auth/change-password",
        headers={"Authorization": f"Bearer {token}"},
        json={"old_password": "mentor123", "new_password": "newMentorPassword123"},
    )
    assert ch_res.status_code == 200

    # Old password must fail
    fail_res = client.post("/api/v1/auth/login", json={"username": "m09", "password": "mentor123"})
    assert fail_res.status_code == 401

    # New password must succeed
    succ_res = client.post("/api/v1/auth/login", json={"username": "m09", "password": "newMentorPassword123"})
    assert succ_res.status_code == 200


def test_data_isolation_student_and_mentor(module_test_db):
    from backend.app.models.academic import Student
    from backend.app.api.deps import enforce_student_isolation, enforce_mentor_isolation
    from fastapi import HTTPException

    # Query Aarav (12511001, mentor m08) and another student (12511002, mentor m08 or m09)
    stu1 = module_test_db.query(Student).filter_by(registration_number="12511001").first()
    stu2 = module_test_db.query(Student).filter_by(registration_number="12511002").first()

    # Student 1 user accessing their own record -> OK
    assert enforce_student_isolation(stu1.user, stu1.id, module_test_db).id == stu1.id

    # Student 1 user attempting to access Student 2's record -> 403 Forbidden
    with pytest.raises(HTTPException) as exc_info:
        enforce_student_isolation(stu1.user, stu2.id, module_test_db)
    assert exc_info.value.status_code == 403

    # Mentor of stu1 accessing stu1 -> OK
    mentor1_user = stu1.mentor.user
    assert enforce_mentor_isolation(mentor1_user, stu1.id, module_test_db).id == stu1.id

    # Find another student belonging to a DIFFERENT mentor
    other_stu = None
    for s in module_test_db.query(Student).all():
        if s.mentor_id != stu1.mentor_id:
            other_stu = s
            break
    assert other_stu is not None

    # Mentor 1 attempting to access another mentor's mentee -> 403 Forbidden
    with pytest.raises(HTTPException) as m_exc:
        enforce_mentor_isolation(mentor1_user, other_stu.id, module_test_db)
    assert m_exc.value.status_code == 403
