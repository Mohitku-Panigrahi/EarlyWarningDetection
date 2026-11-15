import os
from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.app.core.config import settings
from backend.app.database.session import get_db, engine, Base
import backend.app.models
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.student import router as student_router
from backend.app.api.v1.mentor import router as mentor_router
from backend.app.api.v1.interventions import router as intervention_router
from backend.app.api.v1.admin import router as admin_router
from backend.app.api.v1.admin_governance import router as admin_governance_router
from backend.app.api.v1.research import router as research_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Explainable Academic Early-Warning and Intervention Decision System API for Lovely Professional University.",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# Enable CORS for local Vite frontend and Stitch components
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(student_router, prefix=settings.API_V1_STR)
app.include_router(mentor_router, prefix=settings.API_V1_STR)
app.include_router(intervention_router, prefix=settings.API_V1_STR)
app.include_router(admin_router, prefix=settings.API_V1_STR)
app.include_router(admin_governance_router, prefix=settings.API_V1_STR)
app.include_router(research_router, prefix=settings.API_V1_STR)

# ----------------- FRONTEND STATIC & DASHBOARD ROUTES -----------------
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "frontend")

if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/", include_in_schema=False)
def root_redirect():
    """Redirect root to the multi-role login portal."""
    return RedirectResponse(url="/login")

@app.get("/login", include_in_schema=False)
def serve_login():
    """Serve the Eduvance Multi-Role Login Portal."""
    login_path = os.path.join(FRONTEND_DIR, "login.html")
    if os.path.exists(login_path):
        return FileResponse(login_path)
    return {"message": "Eduvance Multi-Role Login Portal"}

@app.get("/student", include_in_schema=False)
def serve_student():
    """Serve the Student Academic Dashboard."""
    student_path = os.path.join(FRONTEND_DIR, "student.html")
    if os.path.exists(student_path):
        return FileResponse(student_path)
    return {"message": "Student Academic Dashboard"}

@app.get("/mentor", include_in_schema=False)
def serve_mentor():
    """Serve the Mentor Decision & Intervention Dashboard."""
    mentor_path = os.path.join(FRONTEND_DIR, "mentor.html")
    if os.path.exists(mentor_path):
        return FileResponse(mentor_path)
    return {"message": "Mentor Decision & Intervention Dashboard"}

@app.get("/admin", include_in_schema=False)
def serve_admin():
    """Serve the Institutional Administration Dashboard."""
    admin_path = os.path.join(FRONTEND_DIR, "admin.html")
    if os.path.exists(admin_path):
        return FileResponse(admin_path)
    return {"message": "Institutional Administration Dashboard"}

@app.get("/lab", include_in_schema=False)
def serve_lab():
    """Serve the Research and Algorithm Lab."""
    lab_path = os.path.join(FRONTEND_DIR, "lab.html")
    if os.path.exists(lab_path):
        return FileResponse(lab_path)
    return {"message": "Research and Algorithm Lab"}

# ----------------- SYSTEM & HEALTH ENDPOINTS -----------------

@app.get(f"{settings.API_V1_STR}/health", tags=["Health"])
def health_check():
    """Basic service liveness probe."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

@app.get(f"{settings.API_V1_STR}/health/database", tags=["Health"])
def database_health_check(db: Session = Depends(get_db)):
    """Database connectivity and readiness probe."""
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "connected",
            "database": "SQLite (lpu_risk_system.db)",
            "readiness": "ready",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connectivity failed: {str(e)}",
        )

@app.get(f"{settings.API_V1_STR}/system/info", tags=["Health"])
def system_info(db: Session = Depends(get_db)):
    """System information, active dataset status, and model metadata."""
    from backend.app.models.academic import Student, Mentor
    from backend.app.models.risk import ModelRegistry
    from backend.app.models.system import SystemSetting

    total_students = db.query(Student).count()
    total_mentors = db.query(Mentor).count()
    active_model = db.query(ModelRegistry).filter_by(status="active").first()
    settings_rows = db.query(SystemSetting).all()

    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "academic_session": "2024-2025 Regular (Semester 4 - Spring)",
        "cohort": {
            "total_students": total_students,
            "total_mentors": total_mentors,
            "sections": ["K3P25IL", "K3P25IM", "K3P25IN"],
        },
        "model_engine": {
            "version": active_model.model_version if active_model else "v2.4-lpu-demo",
            "status": "Calibrated & Active",
            "decision_threshold": active_model.threshold if active_model else 0.40,
        },
        "system_settings": {s.setting_key: s.setting_value for s in settings_rows},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
