@echo off
title LPU-RISK-01 Academic Early-Warning System
color 0B
cls

echo ======================================================================
echo    LPU-RISK-01 - Explainable Academic Early-Warning System
echo                  Lovely Professional University
echo ======================================================================
echo.

:: Check Python availability
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Python is not found in your PATH!
    echo Please install Python 3.11+ and add it to PATH.
    pause
    exit /b 1
)

echo [1/3] Initializing database and verifying synthetic LPU cohort seed...
python -m backend.app.scripts.seed_demo_data
if %errorlevel% neq 0 (
    echo [WARNING] Seed script reported an error or database already initialized.
) else (
    echo [SUCCESS] Database ready with 60 students and 6 mentors.
)
echo.

echo [2/3] Verification complete.
echo.
echo ======================================================================
echo  ACCESS DIRECTORY:
echo   Portal Login:       http://localhost:8000/login
echo   Student Dashboard:  http://localhost:8000/student
echo   Mentor Workspace:   http://localhost:8000/mentor
echo   Admin Dashboard:    http://localhost:8000/admin
echo   Interactive Swagger: http://localhost:8000/docs
echo.
echo  PRE-SEEDED DEMO CREDENTIALS:
echo   Student (Aarav Sharma):   12511001   / demo123
echo   Mentor (Dr. Manoj Saini): m08        / mentor123
echo   Administrator:            admin      / admin123
echo ======================================================================
echo.
echo [3/3] Launching FastAPI + Uvicorn server on http://localhost:8000 ...
echo Opening default web browser in 2 seconds...
echo.

:: Automatically open default web browser to the login portal after 2-second server warmup
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://localhost:8000/login"

:: Start Uvicorn Server
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

pause
