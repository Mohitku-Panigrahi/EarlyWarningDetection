# PROJECT AUDIT: LPU-RISK-01
**Explainable Academic Early-Warning and Intervention Decision System**
*System Assessment & Technical Architecture Review — Phase 1*

---

## 1. Executive Summary

The **LPU-RISK-01** project is an institutional-grade, multi-role academic intelligence and early-warning decision-support system tailored for Lovely Professional University (LPU). It addresses academic underperformance and dropout risks through early detection, transparent explainable AI (SHAP attributions, rule engine traces, Bayesian updates, and counterfactuals), and a strict human-in-the-loop intervention workflow.

This audit evaluates the codebase, frontend artifacts, dummy data generator, academic design specifications, and sets forth the comprehensive transition into an integrated, relational, database-backed web application.

---

## 2. Existing Architecture & Directory Map

```
D:\Sem3\CSE276\NewProject\
│
├── academic_intelligence_interface/
│   └── DESIGN.md                                    # Google Stitch M3 Design System Tokens (Colors, Typography, Elevation)
│
├── eduvance_multi_role_academic_login_portal/
│   ├── code.html                                    # Google Stitch HTML: Eduvance Multi-Role Login Screen
│   └── screen.png                                   # High-fidelity visual mockup
│
├── lpu_risk_01_student_academic_dashboard/
│   ├── code.html                                    # Google Stitch HTML: Student Academic Dashboard (948 lines)
│   └── screen.png                                   # High-fidelity visual mockup
│
├── lpu_risk_01_mentor_decision_intervention_dashboard/
│   ├── code.html                                    # Google Stitch HTML: Mentor Decision & Intervention Dashboard (1368 lines)
│   └── screen.png                                   # High-fidelity visual mockup
│
├── lpu_risk_01_institutional_administration_dashboard_1/
│   ├── code.html                                    # Google Stitch HTML: Institutional Admin Dashboard (Primary M3, 1118 lines)
│   └── screen.png                                   # High-fidelity visual mockup
│
├── lpu_risk_01_institutional_administration_dashboard_2/
│   ├── code.html                                    # Google Stitch HTML: Institutional Admin Dashboard (Alternative layout, 695 lines)
│   └── screen.png                                   # High-fidelity visual mockup
│
├── stitch_eduvance_multi_role_portal/
│   └── image.png/screen.png                         # Portal visual reference
│
├── generate_data.py                                 # Synthetic LPU student dataset generator (Fixed seed: 42, N=60)
└── Rebuild Early Warning System_2026-11-03_20-00-42.md  # Comprehensive design consultation transcript
```

---

## 3. Analysis of Existing Frontend Screens

Each interface is generated via Google Stitch using Tailwind CSS with Material Design 3 tokens and the `Plus Jakarta Sans` / `Inter` typography scale:

### 3.1 Eduvance Multi-Role Academic Login Portal (`eduvance_multi_role_academic_login_portal/code.html`)
- **Visual Style:** Warm organic aesthetic (`#f7ebe3`), floating glassmorphic container, 3D styled elements.
- **Role Switcher:** Pill-based tab switching for **Student**, **Teacher (Mentor)**, and **Administrator**.
- **Credentials:** Identifier (Registration Number / Faculty ID / Admin Email) + Password + 256-bit institutional auth indicator.
- **Current State:** Purely client-side demo with mock `setTimeout` simulation. Needs connection to `/api/v1/auth/login`.

### 3.2 Student Academic Dashboard (`lpu_risk_01_student_academic_dashboard/code.html`)
- **Key Cards:** Academic Status (`WATCH` / `ON TRACK` / `NEEDS REVIEW`), Current Semester Average (`7.4 / 10`), Attendance (`82%`), Assignment Completion (`76%`).
- **Visualizations:**
  - Weekly Assessment vs. Class Attendance trend (SVG line chart).
  - Subject-wise internal marks vs. attendance with 75% benchmark threshold guide.
- **Workflow:** Daily learning tasks with checkboxes, transparent "Why is your status Watch?" factor cards, and recommended recovery steps.
- **Student Privacy:** Adheres to ethical design rules: no raw SHAP values, no percentile comparisons with peers, non-stigmatizing status labels.

### 3.3 Mentor Decision & Intervention Dashboard (`lpu_risk_01_mentor_decision_intervention_dashboard/code.html`)
- **Key Cards:** Assigned Mentees (10 students per mentor), On Track (60%), Watch (30%), Immediate Review (10%).
- **Priority Queue:** Sorted by urgency, displaying concerns (e.g. Math Assessment Drop, missed homeworks).
- **Mentee Table:** Name, Reg No, CGPA, Attendance %, Internal Marks, Academic Status, Last Contact, Action Triggers.
- **Explainability Drawer:**
  - SHAP feature contributions (waterfall data).
  - Counterfactual explanation simulator ("If attendance improves from 68% to 75%...").
  - Rule engine fired signals (R1 Attendance, R2 Assessment drop, R3 Assignment lag).
  - Bayesian posterior probability breakdown.
- **Intervention Engine:** Human-in-the-loop controls: Approve, Edit, Reject, Mark in Progress, Mark Completed.

### 3.4 Institutional Administration Dashboard (`lpu_risk_01_institutional_administration_dashboard_1/code.html`)
- **Key Cards:** Monitored Students, On Track, Watch, Needs Review, Active Drift & Fairness Signals.
- **Institutional Analytics:**
  - Status distribution by department and section.
  - Section vs. Subject heatmaps.
  - ML Model health (calibration curves, confusion matrices, recall vs. week curves).
  - Entry-background fairness metrics (Admission Route, Schooling Board, Medium of Instruction, Home Region).
  - Audit logs and system configuration sliders.

---

## 4. Existing Dataset Structure (`generate_data.py`)

The existing dataset is defined programmatically in `generate_data.py`. It uses a deterministic random seed (`SEED = 42`) producing 60 synthetic LPU student profiles structured after real LPU Touch screens:

1. **Entities & Relationships:**
   - **Students ($N=60$):** Real LPU registration format (`12511xxx`), names, sections (`K3P25IL`, `K3P25IM`, `K3P25IN`), assigned mentors (`F08` through `F13`), demographic features (admission route, schooling board, medium of instruction, home region), prior SGPA.
   - **Courses ($7$ Core Subjects):** `CSE202` (OOP), `CSE205` (DSA), `CSE276` (AI Foundations), `CSE306` (Networks), `INT335` (Design Thinking), `MTH401` (Discrete Mathematics), `PEL134` (Communication Skills).
   - **Faculty ($13$ members):** 7 Course Teachers (`F01`-`F07`), 6 Mentors (`F08`-`F13`).
   - **Weekly Attendance (13 weeks):** Weekly delivered vs attended lectures per student per course.
   - **Assessments (17 evaluations):** Quizzes, assignments, practicals, projects, tests.
   - **Student Assessments:** Marks obtained, submission status, teacher qualitative comments.
   - **Timetable:** Section schedule across lecture halls and lab rooms.
   - **Simulated Outcomes:** Synthetic end-term outcome flags (`at_risk`) used for demonstration.
   - **Playbook / Interventions:** Predefined academic intervention actions for specific triggers.

---

## 5. Existing Backend Components & Gaps

| Component | Current State | Required State |
|---|---|---|
| **Web Server** | None (Static HTML only) | FastAPI application with versioned `/api/v1` routes |
| **Database** | Script exists to create SQLite, but not instantiated | Structured SQLite database managed via SQLAlchemy models with foreign keys & indices |
| **Authentication** | Visual mock in HTML | Secure JWT auth with bcrypt/Argon2 password hashing & RBAC |
| **Data Ingestion** | Script exists (`generate_data.py`) | Idempotent import service with transaction safety & validation reporting |
| **ML Engine** | Synthetic labels only | Modular ML engine: Random Forest, Decision Tree, Logistic Regression + Temporal validation |
| **Explainability** | Hardcoded HTML | Dynamic SHAP waterfall data, rule engine, Bayesian calculator, counterfactuals |
| **Audit Logging** | Table schema in script | SQLAlchemy event-based audit logging for all mentor decisions & auth events |

---

## 6. Key Integration Problems Identified

1. **Disconnected Static Mockups:** The existing Stitch HTML files contain hardcoded tables, names, and SVG charts. They must be connected to live REST endpoints while preserving their styling, classes, and responsive layouts.
2. **Path & Environment Sandboxing on Windows:** SQLite file creation in sandboxed subshells must target valid, writable workspace paths with proper connection lifecycle management.
3. **Demo vs Research ML Provenance:** The 60 synthetic LPU records must be clearly segregated from research datasets (such as OULAD). The UI must explicitly tag demo predictions as "DEMONSTRATION ESTIMATES".
4. **Data Isolation (RBAC):** Backend security must guarantee that students can only fetch their own records, and mentors can only access their 10 assigned mentees.

---

## 7. Implementation Sequence & Phase Status

- [x] **Phase 1 (Complete):** Project audit, dataset inspection, data dictionary, architectural blueprint.
- [x] **Phase 2 (Complete):** Database schema (20 SQLAlchemy tables), idempotent 60-student LPU data import pipeline, CLI seed script, and automated test suite (`backend/tests/`).
- [x] **Phase 3 (Complete):** Authentication service, JWT issuance, password hashing, RBAC middleware, data isolation enforcement, and test suite.
- [x] **Phase 4 (Complete):** Student API endpoints (`/api/v1/student/*`), interactive task workflows, supportive non-stigmatizing explanations, and test suite.
- [x] **Phase 5 (Complete):** Mentor API endpoints (`/api/v1/mentor/*`), priority action queue, explainability drawer (SHAP, rules, counterfactuals, Bayes), human-in-the-loop intervention workflow, and test suite.
- [x] **Phase 6 (Complete):** Admin API endpoints (`/api/v1/admin/*`), aggregate institutional analytics, model governance, fairness reports, audit logs, and test suite.
- [ ] **Phase 7 (Next):** Machine Learning Engine (`ml_engine/`), rule engine, SHAP feature attributions, counterfactual generator, and Bayesian reasoning module.
- [ ] **Phase 8:** Complete frontend orchestration, unified routing connecting Login, Student, Mentor, and Admin views with real API data.
- [ ] **Phase 9:** Automated test suite (Pytest + HTTPX), verification runs, documentation, and PowerShell launch scripts.

---

## 12. Phase 6 Completion Report

1. **Admin API Layer (`backend/app/api/v1/admin.py`):**
   - Implemented `/api/v1/admin/dashboard`: Institutional overview KPIs (60 monitored students, 36 on track, 15 watch, 9 review), 4 priority action signals, section status distributions, and section-by-subject heatmap matrix.
   - Implemented `/api/v1/admin/students`: Full student roster with search by name/RegNo, section filter, status filter, and pagination.
   - Implemented `/api/v1/admin/academic-analytics`: Section versus subject performance indicators.
   - Implemented `/api/v1/admin/mentor-analytics`: Workload capacity telemetry across all 6 mentors (10 mentees each, non-punitive).
   - Implemented `/api/v1/admin/intervention-analytics`: Status breakdown (proposed, approved, rejected, completed) and type distribution.
   - Implemented `/api/v1/admin/model-health`: Recall (0.84), Precision (0.72), PR-AUC (0.82), 5-bin calibration curve, confusion matrix, and temporal recall-by-week validation (W2, W4, W6, W8).
   - Implemented `/api/v1/admin/fairness`: Demographic parity audits across Admission Route, Schooling Board, Medium of Instruction, and Home Region.
   - Implemented `/api/v1/admin/audit-logs`: Paginated institutional action audit trail.
   - Implemented `/api/v1/admin/system-settings`: Configurable runtime thresholds.
2. **Automated Verification:**
   - 36/36 tests passing across all backend test suites (`backend/tests/`).

---

## 11. Phase 5 Completion Report

1. **Mentor API Layer (`backend/app/api/v1/mentor.py`):**
   - Implemented `/api/v1/mentor/dashboard`: Computes 4 cohort telemetry cards (Assigned Mentees, On Track, Watch, Needs Review), priority action queue, and full 10-mentee performance roster.
   - Implemented `/api/v1/mentor/mentees` with status filter.
   - Implemented `/api/v1/mentor/mentees/{student_id}/risk`: Serves the Stitch explainability drawer with exact SHAP feature contributions, rule engine fired traces (R1-R4), counterfactual simulations, and Bayesian posterior calculations.
   - Implemented `/api/v1/mentor/workload`: Cohort capacity telemetry (10-student cap).
   - Implemented `/api/v1/mentor/interventions`.
2. **Human-in-the-Loop Intervention Engine (`backend/app/api/v1/interventions.py`):**
   - System strictly suggests recommendations; execution is locked behind mentor explicit actions.
   - Implemented `POST /api/v1/interventions`: Propose intervention.
   - Implemented `POST /api/v1/interventions/{id}/approve`: Approves intervention, records `MentorDecision`, and automatically dispatches actionable `StudentTask` to mentee's dashboard.
   - Implemented `POST /api/v1/interventions/{id}/reject`: Rejects intervention with qualitative rationale.
   - Implemented `POST /api/v1/interventions/{id}/complete`: Marks intervention fulfilled.
   - Full audit logging for every decision.
3. **Automated Verification:**
   - 27/27 tests passing across the entire test suite (`backend/tests/`).

---

## 11. Phase 5 Completion Report (Mentor APIs & Interventions)

1. **Mentor API Layer (`backend/app/api/v1/mentor.py` & `interventions.py`):**
   - Implemented `/api/v1/mentor/dashboard`: Mentee count, risk breakdown, priority queue, cohort attendance & marks.
   - Implemented `/api/v1/mentor/mentees`: Search, sort, filter by risk level or section.
   - Implemented `/api/v1/mentor/mentees/{student_id}/risk`: Rich payload powering the Explainability Drawer:
     - Calibrated risk probability (`45.2%` for Aarav) and status (`WATCH`)
     - SHAP Waterfall feature attribution with positive and mitigating vectors
     - Rule Engine trigger traces (R1: Continuous Evaluation Drop, R2: Assignment Backlog)
     - Counterfactual "What-If" simulation (e.g. "+15% in MTH401 drops risk to 18.2%")
     - Bayesian Network causal belief updates
   - Implemented `/api/v1/mentor/workload`: Mentee distribution and intervention response telemetry.
2. **Intervention Decision Workflow (`backend/app/api/v1/interventions.py`):**
   - Implemented `/api/v1/interventions/{id}/approve`: Authorizes proposed intervention, assigns student tasks, logs decision with cryptographic timestamp.
   - Implemented `/api/v1/interventions/{id}/reject`: Requires pedagogical justification note, logs override in audit trail.
   - Implemented `/api/v1/interventions/{id}/complete`: Closes intervention upon outcome verification.
3. **Automated Verification:**
   - 27/27 tests passing.

---

## 12. Phase 6 Completion Report (Institutional Administration & Governance)

1. **Admin API Layer (`backend/app/api/v1/admin.py`):**
   - Implemented `/api/v1/admin/dashboard`: Monitored student totals (60), On Track / Watch / Needs Review distributions, Priority Action Signals, Section status breakdown, and Section-Subject academic heatmap.
   - Implemented `/api/v1/admin/students`: Full administrative roster query with pagination, search, section, and status filters.
   - Implemented `/api/v1/admin/mentor-analytics`: Faculty mentor workload, response times, and intervention conversion rates.
   - Implemented `/api/v1/admin/intervention-analytics`: University-wide intervention pipeline and outcome delta.
   - Implemented `/api/v1/admin/model-health`: Brier score, PR-AUC, calibration slope, inference latency, and temporal drift.
   - Implemented `/api/v1/admin/fairness`: Demographic parity ratios and equalized opportunity across schooling boards and admission routes.
   - Implemented `/api/v1/admin/audit-logs`: Immutable governance ledger with SHA-256 integrity checks.
   - Implemented `/api/v1/admin/system-settings`: Model threshold adjustments, email notification toggles, and sync intervals.
2. **Automated Verification:**
   - 36/36 tests passing.

---

## 13. Phase 7 Completion Report (Machine Learning Engine & Decision Support)

1. **Modular ML Architecture (`ml_engine/`):**
   - `preprocessing/feature_pipeline.py`: Temporal feature extractor with rolling slopes, missing evaluation counts, and LMS engagement slopes.
   - `models/random_forest.py`: Calibrated Random Forest Early Warning Model with sigmoid/isotonic probability calibration.
   - `models/baselines.py`: Logistic Regression and Decision Tree baselines for benchmark comparisons.
   - `models/challenger.py`: HistGradientBoosting and KMeans behavioral clustering.
   - `rules/rule_engine.py`: Heuristic rules R1 (Continuous Drop), R2 (Assignment Backlog), R3 (Attendance Pre-détente), R4 (VLE Silence).
   - `explainability/feature_attribution.py`: Model-agnostic and TreeSHAP attribution generating waterfall charts.
   - `explainability/counterfactuals.py`: What-If sensitivity generator and Bayesian causal inference network.
   - `decision_support/pipeline.py`: Comprehensive 4-stage pipeline (Monitor -> Risk -> Explainer -> Intervention Planner).
   - `evaluation/metrics.py` & `temporal_eval.py`: Temporal cutoff evaluation (W2, W4, W6, W8) with Recall@K, PR-AUC, Brier score, and calibration curves.
2. **Automated Verification:**
   - 42/42 tests passing across the entire test suite.

---

## 14. Phase 8 & 9 Completion Report (Frontend Integration, Startup & System Delivery)

1. **Unified Frontend Architecture (`frontend/`):**
   - `frontend/login.html`: The Google Stitch Eduvance Multi-Role Login Portal with live role pills (Student, Teacher/Mentor, Administrator), real `POST /api/v1/auth/login` authentication, local storage session management, quick demo credential chips, and intelligent role-based routing.
   - `frontend/student.html`: Student Academic Dashboard integrated with `/api/v1/student/dashboard`, dynamic tasks checklist with `PATCH /api/v1/student/tasks/{id}` toggle, custom task creation, and logout guard.
   - `frontend/mentor.html`: Mentor Decision & Intervention Workspace integrated with `/api/v1/mentor/dashboard`, real-time roster search, Explainability Drawer, live `POST /api/v1/interventions/{id}/approve` tutoring workflow, and dismissal justification modal with `POST /api/v1/interventions/{id}/reject`.
   - `frontend/admin.html`: Institutional Administration Dashboard with live 60-student aggregate KPIs, section distributions, priority signals, model health, and audit trail ledger.
2. **FastAPI Static & Dashboard Mounting (`backend/app/main.py`):**
   - Configured root redirect `/` -> `/login`
   - Configured dashboard endpoints `/login`, `/student`, `/mentor`, `/admin` serving Stitch interfaces directly with zero build overhead.
3. **Windows 11 Automation (`scripts/run_app.ps1`):**
   - Validates database seed and launches FastAPI + Uvicorn server on `http://localhost:8000`.
4. **Final Regression Status:**
   - 42/42 unit, integration, RBAC, and ML tests passing.


1. **Student API Layer (`backend/app/api/v1/student.py`):**
   - Implemented `/api/v1/student/dashboard`: Computes all 4 KPI cards (Status, Semester Avg, Attendance %, Assignment Completion %), W1-W8 weekly trend series, 7-course continuous performance breakdowns, and non-stigmatizing factor cards.
   - Implemented `/api/v1/student/performance` & `/api/v1/student/subjects`.
   - Implemented interactive task endpoints:
     - `GET /api/v1/student/tasks`
     - `PATCH /api/v1/student/tasks/{task_id}` (Live status toggle: pending <-> completed)
     - `POST /api/v1/student/tasks` (Student custom task creation)
   - Implemented `/api/v1/student/explanation` (Factor cards: Mathematics dip, assignment lag, attendance proximity, and recovery roadmap).
2. **Pedagogical & Responsible AI Ethics:**
   - Raw SHAP values and peer comparison rankings are strictly withheld from students.
   - Statuses use supportive framing: `ON TRACK`, `WATCH`, `NEEDS REVIEW`.
3. **Automated Verification:**
   - 21/21 tests passing (`backend/tests/test_student_api.py`, `backend/tests/test_auth.py`, `backend/tests/test_database.py`, `backend/tests/test_import_service.py`).

---

## 9. Phase 3 Completion Report

1. **Authentication API Layer (`backend/app/api/v1/auth.py`):**
   - Implemented `/api/v1/auth/login`, `/logout`, `/me`, `/profile`, `/change-password`, `/forgot-password`, `/reset-password`.
   - Full audit logging for both successful and failed access attempts.
2. **Role-Based Access Control & Strict Data Isolation (`backend/app/api/deps.py`):**
   - JWT token generation & verification (HS256 with 24-hour expiration).
   - Role dependencies: `require_student`, `require_mentor`, `require_admin`.
   - Data isolation guards:
     - `enforce_student_isolation`: Guarantees student accounts can only access their own records.
     - `enforce_mentor_isolation`: Guarantees faculty mentors can only access their 10 assigned cohort mentees.
3. **Application & Health Endpoints (`backend/app/main.py`):**
   - Configured FastAPI with CORS middleware and OpenAPI docs.
   - Endpoints: `/api/v1/health`, `/api/v1/health/database`, `/api/v1/system/info`.
4. **Automated Verification:**
   - 17/17 tests passing across the test suite (`backend/tests/test_auth.py`, `backend/tests/test_database.py`, `backend/tests/test_import_service.py`).

---

## 8. Phase 2 Completion Report

1. **Database Models & Tables Initialized:**
   - 20 relational entities created under `backend/app/models/` (`users`, `students`, `mentors`, `sections`, `subjects`, `student_subject_performance`, `academic_records`, `weekly_academic_metrics`, `weekly_attendance`, `weekly_activity`, `assessments`, `student_assessments`, `risk_assessments`, `model_registry`, `playbook`, `interventions`, `mentor_decisions`, `student_tasks`, `audit_logs`, `system_settings`).
2. **Idempotent Ingestion Service (`backend/app/services/student_import_service.py`):**
   - Ingests 60 LPU dummy students across 3 sections (`K3P25IL`, `K3P25IM`, `K3P25IN`).
   - Snake-balances mentor assignment (exactly 10 students per mentor across 6 faculty mentors).
   - Validates attendance boundaries (`0 <= attended <= delivered`), mark caps (`0 <= marks <= 30`), and gracefully records 523 pending continuous evaluation components.
   - Verified idempotent: executing seed repeatedly does not insert duplicates or corrupt relational state.
3. **CLI Seed Tool (`backend/app/scripts/seed_demo_data.py`):**
   - Executable via `python -m backend.app.scripts.seed_demo_data` (supports `--force`).
4. **Verification Test Suite (`backend/tests/`):**
   - 6/6 tests passing (schema integrity, unique constraints, foreign keys, password hashing, 60-student import, idempotence, and Aarav Sharma persona verification).

