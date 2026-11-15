# CSE276 Unit II: Knowledge Representation & Logical Reasoning
**LPU-RISK-01 Formal Knowledge Engineering Specification**

---

## 1. Minsky Frames Architecture (`frames.py`)
Minsky's Frame Theory represents structured stereotypical knowledge through collections of named slots, values, and constraints.

In **LPU-RISK-01**, core academic entities are modeled as strongly typed Frames:
1. `StudentFrame`: Registration ID, name, section, mentor ID, CGPA, attendance %, risk status, enrolled subjects.
2. `SubjectFrame`: Subject code, title, delivered lectures, course teacher faculty ID, core/elective flag.
3. `AssessmentFrame`: Assessment ID, course code, mode (online/manual), max marks, weightage.
4. `AttendanceFrame`: Attended, delivered, duty leave, calculated percentage, statutory threshold flag (< 75%).
5. `MentorFrame`: Faculty ID, name, department, assigned caseload, caseload overload indicator (> 15 mentees).
6. `InterventionFrame`: Action ID, student ID, mentor ID, type, priority, approval status.

---

## 2. First-Order Logic Predicates (`predicates.py`)
Predicates define boolean truth functions over university domain objects:

* **$\text{LowAttendance}(s)$:**
  $$\text{attendance\_pct}(s) < 75.0$$
* **$\text{DecliningPerformance}(s)$:**
  $$\text{marks\_drop}(s) \ge 10.0 \lor \text{trend}(s) = \text{"declining"}$$
* **$\text{IncompleteAssignments}(s)$:**
  $$\text{missing\_count}(s) \ge 2$$
* **$\text{NeedsMentorReview}(s)$:**
  $$\text{LowAttendance}(s) \lor (\text{DecliningPerformance}(s) \land \text{IncompleteAssignments}(s))$$
* **$\text{StrugglingInSubject}(s, c)$:**
  $$\text{score}(s, c) < 50.0 \lor \text{attendance}(s, c) < 75.0$$

---

## 3. Production Rules (R1–R4) (`production_rules.py`)
Production systems evaluate forward-chaining condition-action pairs:

* **R1 (Attendance Threshold):**
  * `IF` $\text{attendance\_pct} < 75.0\%$
  * `THEN` Trigger Attendance Recovery Counselling signal.
* **R2 (Assessment Decline):**
  * `IF` Continuous evaluation score drops $\ge 10\%$ across recorded cycles
  * `THEN` Trigger Subject Tutoring & Doubts Clearing signal.
* **R3 (Assignment Completion):**
  * `IF` Overdue submissions count $\ge 2$
  * `THEN` Trigger Assignment Pacing Support signal.
* **R4 (Multi-Indicator Synthesis):**
  * `IF` $\text{COUNT}(\text{Active Rules } \{R1, R2, R3\}) \ge 2$
  * `THEN` Recommend Priority Mentor Diagnostic Meeting.

---

## 4. Propositional Logic & Truth Table (`propositional_logic.py`)
Canonical early-warning policy formula:
$$(P \lor (Q \land R)) \longrightarrow S$$
where:
* $P = \text{LowAttendance}$
* $Q = \text{DecliningPerformance}$
* $R = \text{IncompleteAssignments}$
* $S = \text{NeedsMentorReview}$

The formula has 4 variables ($2^4 = 16$ rows in truth table). It evaluates to satisfiable ($15/16$ true outcomes under material implication), proving that the policy is sound and non-contradictory.

---

## 5. Universal & Existential Cohort Quantification (`first_order_logic.py`)
* $\forall s \in \text{Section}: \neg \text{LowAttendance}(s)$
  Evaluates whether the entire cohort is attendance-compliant; returns specific counterexamples when violated.
* $\exists s \in \text{MenteeGroup}: \text{NeedsMentorReview}(s)$
  Identifies if any mentee requires priority intervention, returning concrete witness profiles.
