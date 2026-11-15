# LPU-RISK-01: Research & Algorithm Lab User & Technical Guide
**Interactive Workspace for CSE276 Artificial Intelligence Foundations**

---

## 1. Overview
The **Research & Algorithm Lab** (`/lab`) provides faculty, students, and evaluators with a dedicated interactive sandbox for investigating core AI techniques in university decision support without cluttering operational dashboards.

---

## 2. Lab Modules

### 2.1 Search Algorithm Lab
* **Location:** Tab 1 (`#pane-search`)
* **Features:**
  * Algorithm selector: BFS, DFS, Best-First Search, Hill Climbing, A* Search ($f = g + h$).
  * Dynamic start and goal state selectors.
  * Real-time interactive SVG graph rendering 8 states and 12 transitions.
  * Node highlighting: Visited states (blue), Optimal Path (navy/emerald), Unvisited (grey).
  * 5-Algorithm comparison matrix benchmarking steps, expanded nodes, effort hours, and execution duration.

### 2.2 Knowledge Representation & Logic Lab
* **Location:** Tab 2 (`#pane-knowledge`)
* **Features:**
  * Interactive student telemetry sliders (attendance %, marks drop %, missing tasks).
  * Live Minsky Frame JSON view.
  * First-Order Predicate evaluation badges (`LowAttendance`, `DecliningPerformance`, `IncompleteAssignments`, `NeedsMentorReview`).
  * Production Rules (R1–R4) execution trace with plain-language explanations.
  * Propositional logic inference verification.

### 2.3 Bayesian Reasoning Lab
* **Location:** Tab 3 (`#pane-bayesian`)
* **Features:**
  * Interactive Prior probability slider $P(H) \in [0.05, 0.80]$.
  * Multi-indicator evidence checkboxes ($E_1, E_2, E_3$).
  * Step-by-step mathematical breakdown: Prior, Likelihoods $P(E|H)$ and $P(E|\neg H)$, Marginal $P(E)$, and Posterior $P(H|E)$.
  * Bayes Factor and normalization validation.

### 2.4 Model Benchmark Lab
* **Location:** Tab 4 (`#pane-models`)
* **Features:**
  * Supervised classifier benchmark matrix:
    * Calibrated Random Forest (Selected Early-Warning Model)
    * Logistic Regression (Linear Interpretable Baseline)
    * Decision Tree (Depth 4 Orthogonal Rule Tree)
    * HistGradientBoosting (Challenger Ensemble)
  * Metrics reported: Recall, Precision, F1, F2, PR-AUC, and Brier calibration score.
  * Unsupervised K-Means behavioral personas ($k=4$).

### 2.5 Dataset Explorer
* **Location:** Tab 5 (`#pane-dataset`)
* **Features:**
  * Demonstration cohort metrics ($N=60$ students, 3 sections, 6 mentors).
  * Admission route, schooling board, and medium of instruction distributions.
  * Zero-leakage temporal snapshot documentation (Weeks 2, 4, 6, 8).
