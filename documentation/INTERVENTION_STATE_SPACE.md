# LPU-RISK-01: Intervention State-Space Architecture
**Formal Graph Specification & Pedagogical Transition Model**

---

## 1. State Definitions

States in `ml_engine/search/graph.py` represent discrete stages of student support, avoiding arbitrary graph representations.

| State ID | Name | Category | Workload (h) | Urgency | Description |
|---|---|---|---|---|---|
| `INITIAL_REVIEW` | Initial Academic Review | Detection | 0.5h | MEDIUM | Early friction flagged by Monitor component (Att < 75% or test drop). |
| `MENTOR_MEETING` | Diagnostic Mentor Interview | Diagnostics | 1.0h | HIGH | Mentor conducts root-cause interview to identify hurdles. |
| `ATTENDANCE_SUPPORT` | Attendance Recovery Plan | Action | 2.0h | HIGH | 3-week attendance recovery plan with biometric verification. |
| `SUBJECT_TUTORING` | Remedial Subject Tutoring | Action | 4.0h | MEDIUM | Department peer tutoring in weak core course (e.g. MTH401, CSE205). |
| `ASSIGNMENT_PLANNING` | Assignment Pacing Support | Action | 1.5h | LOW | Milestone calendar for backlog continuous assessments. |
| `FACULTY_REFERRAL` | Course Teacher Referral | Action | 1.0h | MEDIUM | Consultation with assigned course teacher for conceptual doubts. |
| `FOLLOW_UP_REVIEW` | Progress Follow-up Review | Evaluation | 0.5h | LOW | Bi-weekly evaluation of student recovery trajectory. |
| `PLAN_COMPLETED` | Intervention Plan Completed | Resolution | 0.0h | LOW | Target state: Academic indicators stabilized; audited and closed. |

---

## 2. Transition Matrix & Edge Properties

| ID | Source | Target | Action | Cost $g(n)$ | Heuristic $h(n)$ | Preconditions |
|---|---|---|---|---|---|---|
| `T01` | `INITIAL_REVIEW` | `MENTOR_MEETING` | Schedule Mentoring Session | 1.0h | 3.0 | Flagged by Monitor component |
| `T02` | `INITIAL_REVIEW` | `ATTENDANCE_SUPPORT` | Direct Attendance Tracking | 1.5h | 4.0 | Attendance < 75% |
| `T03` | `MENTOR_MEETING` | `ATTENDANCE_SUPPORT` | Authorize Attendance Plan | 1.0h | 3.0 | Attendance deficit confirmed in interview |
| `T04` | `MENTOR_MEETING` | `SUBJECT_TUTORING` | Assign Subject Tutor | 2.0h | 2.5 | Test score drop in core course |
| `T05` | `MENTOR_MEETING` | `ASSIGNMENT_PLANNING` | Create Assignment Calendar | 1.0h | 2.5 | Overdue assignments $\ge 2$ |
| `T06` | `MENTOR_MEETING` | `FACULTY_REFERRAL` | Refer to Course Faculty | 1.0h | 2.8 | Conceptual roadblock identified |
| `T07` | `ATTENDANCE_SUPPORT` | `FOLLOW_UP_REVIEW` | Log Attendance Milestone | 1.5h | 1.5 | Attendance tracked for 2 weeks |
| `T08` | `SUBJECT_TUTORING` | `FOLLOW_UP_REVIEW` | Assess Tutorial Outcomes | 2.0h | 1.0 | $\ge 3$ tutoring sessions attended |
| `T09` | `ASSIGNMENT_PLANNING` | `FOLLOW_UP_REVIEW` | Verify Submissions | 1.0h | 1.0 | All backlog tasks submitted on LMS |
| `T10` | `FACULTY_REFERRAL` | `FOLLOW_UP_REVIEW` | Collect Faculty Feedback | 1.0h | 1.2 | Faculty consultation conducted |
| `T11` | `FOLLOW_UP_REVIEW` | `PLAN_COMPLETED` | Finalize & Close Plan | 0.5h | 0.0 | Academic indicators returned to ON TRACK |
| `T12` | `FOLLOW_UP_REVIEW` | `MENTOR_MEETING` | Re-convene Mentor Meeting | 1.0h | 3.5 | Insufficient progress observed |

---

## 3. Admissible Heuristic Formulation
The heuristic $h(n)$ models the minimal remaining effort hours to reach `PLAN_COMPLETED`:
* $h(\text{PLAN\_COMPLETED}) = 0.0$
* $h(\text{FOLLOW\_UP\_REVIEW}) = 0.5$
* $h(\text{ASSIGNMENT\_PLANNING}) = 1.5$
* $h(\text{FACULTY\_REFERRAL}) = 1.5$
* $h(\text{ATTENDANCE\_SUPPORT}) = 2.0$
* $h(\text{SUBJECT\_TUTORING}) = 2.5$
* $h(\text{MENTOR\_MEETING}) = 2.0$
* $h(\text{INITIAL\_REVIEW}) = 3.0$

Because $h(n) \le h^*(n)$ for all nodes, the heuristic is **strictly admissible**, ensuring A* search returns the optimal solution.
