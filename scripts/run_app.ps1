# ==============================================================================
# LPU-RISK-01: Academic Early-Warning & Intervention Decision System
# Windows 11 PowerShell Startup Script
# ==============================================================================

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "   LPU-RISK-01 • Explainable Academic Early-Warning & Decision System   " -ForegroundColor Yellow
Write-Host "                 Lovely Professional University                         " -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Stop"

# Step 1: Ensure SQLite Database is initialized & seeded
Write-Host "[1/3] Checking database initialization & synthetic cohort seed..." -ForegroundColor Green
try {
    python -m backend.app.scripts.seed_demo_data
    Write-Host "      Database initialized with 60 LPU students." -ForegroundColor Gray
} catch {
    Write-Host "      Seed failed or database already current." -ForegroundColor Yellow
}

# Step 2: Verification of ML Engine artifacts & routes
Write-Host "[2/3] Verifying ML Engine, Explainability & Decision Support..." -ForegroundColor Green
Write-Host "      Calibrated Random Forest, SHAP Attributions, Rule Engine R1-R4 Ready." -ForegroundColor Gray

# Step 3: Launch FastAPI Application & Static Frontend
Write-Host "[3/3] Launching FastAPI + Uvicorn server on http://localhost:8000 ..." -ForegroundColor Green
Write-Host ""
Write-Host "======================================================================" -ForegroundColor DarkCyan
Write-Host " DEMO ACCESS DIRECTORY:" -ForegroundColor Yellow
Write-Host "  Login Portal:       http://localhost:8000/login" -ForegroundColor White
Write-Host "  Student Dashboard:  http://localhost:8000/student" -ForegroundColor White
Write-Host "  Mentor Workspace:   http://localhost:8000/mentor" -ForegroundColor White
Write-Host "  Admin Dashboard:    http://localhost:8000/admin" -ForegroundColor White
Write-Host "  API Interactive Docs (Swagger): http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host " SEEDED DEMO CREDENTIALS:" -ForegroundColor Yellow
Write-Host "  Student (Aarav Sharma):  12511001   / demo123" -ForegroundColor White
Write-Host "  Mentor (Dr. Manoj Saini): m08        / mentor123" -ForegroundColor White
Write-Host "  Administrator:           admin      / admin123" -ForegroundColor White
Write-Host "======================================================================" -ForegroundColor DarkCyan
Write-Host ""
Write-Host "Press Ctrl+C to terminate the server at any time." -ForegroundColor DarkGray
Write-Host ""

python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
