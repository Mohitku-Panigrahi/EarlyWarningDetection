# DUMMY DATA DICTIONARY: LPU-RISK-01
**Synthetic Student Demonstration Dataset Specification**
*Dataset Provenance: Synthetic LPU Touch Mirror (generate_data.py, Seed: 42, N=60)*

---

## 1. Overview & Data Provenance

All records in this dataset are **strictly synthetic demonstration data** created specifically for the LPU-RISK-01 Academic Early-Warning System project. The schema and behavioral distributions reflect Lovely Professional University academic structures (course codes like `CSE276`, `CSE202`, `CSE205`, `INT335`, `MTH401`, `PEL134`, 8-digit registration IDs starting with `12511xxx`, 75% attendance threshold rules, and continuous internal evaluations).

> [!IMPORTANT]
> This dataset is designated for **DEMONSTRATION MODE ONLY**. Its synthetic labels must never be cited as real-world predictive metrics or institutional evaluations.

---

## 2. Table Specifications & Column Dictionaries

### 2.1 Table: `students`
Primary entity representing enrolled students.

| Column | Meaning / Description | Data Type | Missing Count | Validation Rules | Target DB Field | Notes & Transformations |
|---|---|---|---|---|---|---|
| `student_id` | Unique 8-digit LPU Registration Number | String (8 chars) | 0 | Format: `^12511[0-9]{3}$`, Unique | `students.registration_number` | Primary key identifier |
| `name` | Student's full name | String | 0 | Non-empty, 2-word format | `users.full_name` / `students.name` | Generated from Indian naming pools |
| `section_id` | Assigned class section | String | 0 | Foreign Key to `sections.section_id` (`K3P25IL`, `K3P25IM`, `K3P25IN`) | `students.section` | 20 students per section |
| `mentor_id` | Assigned faculty mentor identifier | String | 0 | Foreign Key to `faculty.faculty_id` | `students.mentor_id` | Exactly 10 students per mentor (Snake balanced) |
| `sem2_sgpa` | Semester 2 SGPA (Prior academic baseline) | Float | 0 | Range: `[4.00, 10.00]`, Rounded to 2 decimals | `academic_records.cgpa` | Prior baseline predictor |
| `cgpa_band` | Categorical grade performance band | String | 0 | Enum: `<6`, `6-8`, `8+` | `students.academic_band` | Derived from `sem2_sgpa` |
| `admission_route`| Qualifying exam admission route | String | 0 | Enum: `LPUNEST`, `JEE Main`, `State CET`, `Board Merit` | `students.admission_route` | Protected/fairness attribute |
| `schooling_board`| Prior 10+2 schooling board | String | 0 | Enum: `CBSE`, `State Board`, `ICSE` | `students.schooling_board` | Protected/fairness attribute |
| `medium_of_instruction`| High school instructional medium | String | 0 | Enum: `English`, `Hindi`, `Regional` | `students.medium_of_instruction` | Protected/fairness attribute |
| `home_region` | Geographic origin region within India | String | 0 | Enum: `North`, `East`, `South`, `West`, `Northeast` | `students.home_region` | Protected/fairness attribute |

---

### 2.2 Table: `courses`
Academic courses registered for the term.

| Column | Meaning / Description | Data Type | Missing Count | Validation Rules | Target DB Field | Notes |
|---|---|---|---|---|---|---|
| `course_code` | Official LPU Course Code | String | 0 | E.g., `CSE276`, `CSE205` | `subjects.subject_code` | Primary Key |
| `title` | Full course title | String | 0 | Non-empty text | `subjects.subject_name` | Official university title |
| `delivered_total`| Total lectures scheduled across semester | Integer | 0 | Range: `[18, 54]` | `subjects.total_lectures` | Aligns with LPU Touch attendance summaries |
| `teacher_id` | Course instructor faculty ID | String | 0 | Foreign Key to `faculty.faculty_id` | `subjects.faculty_id` | Assigned course instructor |

---

### 2.3 Table: `attendance_summary`
Aggregated term-to-date attendance metrics per student and course.

| Column | Meaning / Description | Data Type | Missing Count | Validation Rules | Target DB Field | Notes |
|---|---|---|---|---|---|---|
| `student_id` | Student Registration Number | String | 0 | Foreign Key to `students` | `student_subject_performance.student_id` | Composite PK |
| `course_code` | Course Code | String | 0 | Foreign Key to `courses` | `student_subject_performance.subject_id` | Composite PK |
| `delivered` | Lectures delivered to date | Integer | 0 | `delivered <= delivered_total` | Performance table | Delivered lectures count |
| `attended` | Lectures physically attended | Integer | 0 | `0 <= attended <= delivered` | Performance table | Attended lectures count |
| `duty_leave` | Official university approved duty leave | Integer | 0 | `0 <= duty_leave <= (delivered - attended)` | Performance table | Sanctioned academic duty leave |
| `first_week_bonus`| Institutional first-week attendance bonus | Integer | 0 | `0` or `1` | Performance table | LPU policy feature |
| `pct` | Official calculated attendance percentage | Integer | 0 | Range: `[0, 100]`, Formula: `min(100, round(100*(attended+duty_leave)/delivered))` | `student_subject_performance.attendance_percentage` | Institutional metric (<75% triggers warning) |

---

### 2.4 Table: `weekly_attendance`
Temporal weekly lecture attendance tracking across 13 term weeks.

| Column | Meaning / Description | Data Type | Missing Count | Validation Rules | Target DB Field | Notes |
|---|---|---|---|---|---|---|
| `student_id` | Student Registration Number | String | 0 | Foreign Key to `students` | `weekly_academic_metrics.student_id` | Composite PK |
| `course_code` | Course Code | String | 0 | Foreign Key to `courses` | Contextual attribute | Composite PK |
| `week` | Semester calendar week number | Integer | 0 | Range: `[1, 13]` | `weekly_academic_metrics.week_number` | Composite PK |
| `delivered` | Lectures scheduled in that week | Integer | 0 | Range: `[1, 6]` | Metrics table | Weekly delivered |
| `attended` | Lectures attended in that week | Integer | 0 | `0 <= attended <= delivered` | Metrics table | Used for attendance trend slope |

---

### 2.5 Table: `weekly_activity`
Weekly Learning Management System (LMS) digital engagement tracking.

| Column | Meaning / Description | Data Type | Missing Count | Validation Rules | Target DB Field | Notes |
|---|---|---|---|---|---|---|
| `student_id` | Student Registration Number | String | 0 | Foreign Key to `students` | `weekly_academic_metrics.student_id` | Composite PK |
| `week` | Semester week number | Integer | 0 | Range: `[1, 13]` | `weekly_academic_metrics.week_number` | Composite PK |
| `lms_logins_7d`| Active LMS logins in prior 7 days | Integer | 0 | `>= 0` (Poisson distributed) | `weekly_academic_metrics.engagement_metric` | Disengagement indicator (<3 logins/week) |

---

### 2.6 Table: `assessments`
Continuous Internal Evaluation (CA) components.

| Column | Meaning / Description | Data Type | Missing Count | Validation Rules | Target DB Field | Notes |
|---|---|---|---|---|---|---|
| `assessment_id`| Evaluation identifier (e.g. `A01`) | String | 0 | Format: `^A[0-9]{2}$` | `assessments.assessment_code` | Primary Key |
| `course_code` | Subject course code | String | 0 | Foreign Key to `courses` | `assessments.subject_code` | Linked course |
| `type` | Evaluation classification | String | 0 | Enum: `Test`, `Assignment`, `Project`, `Interview`, `Presentation` | `assessments.type` | Evaluation category |
| `title` | Title of the assessment | String | 0 | Non-empty string | `assessments.title` | Descriptive title |
| `mode` | Administration mode | String | 0 | Enum: `manual`, `online` | `assessments.mode` | Submission modality |
| `assigned_date`| Date released to students | Date (ISO) | 0 | Format: `YYYY-MM-DD` | `assessments.assigned_date` | Assignment date |
| `due_date` | Official submission deadline | Date (ISO) | 0 | `due_date >= assigned_date` | `assessments.due_date` | Due date cutoff |
| `max_marks` | Maximum obtainable marks | Integer | 0 | Default: `30` | `assessments.max_marks` | Standardized internal component |
| `faculty_id` | Evaluating faculty member | String | 0 | Foreign Key to `faculty` | `assessments.faculty_id` | Grader ID |

---

### 2.7 Table: `student_assessments`
Actual student submissions, scores, and instructor feedback.

| Column | Meaning / Description | Data Type | Missing Count | Validation Rules | Target DB Field | Notes |
|---|---|---|---|---|---|---|
| `student_id` | Student Registration Number | String | 0 | Foreign Key to `students` | `student_assessments.student_id` | Composite PK |
| `assessment_id`| Assessment Identifier | String | 0 | Foreign Key to `assessments` | `student_assessments.assessment_id` | Composite PK |
| `marks` | Marks obtained | Float / Null | Handled | If status Present: `0 <= marks <= max_marks`; If Pending: `Null` | `student_assessments.marks` | Step-size: 0.5 |
| `status` | Submission / Attendance state | String | 0 | Enum: `Present`, `Submitted`, `Not Submitted`, `Absent`, `Pending` | `student_assessments.status` | Submission state |
| `teacher_comment`| Constructive feedback string | String | 0 | Contextual pedagogical guidance | `student_assessments.feedback` | Human mentor readable |

---

### 2.8 Table: `faculty`
Faculty personnel and mentor allocations.

| Column | Meaning / Description | Data Type | Missing Count | Validation Rules | Target DB Field | Notes |
|---|---|---|---|---|---|---|
| `faculty_id` | Unique Faculty Code (`F01`-`F13`) | String | 0 | Unique identifier | `mentors.mentor_code` | Primary Key |
| `name` | Full name of academic faculty | String | 0 | Non-empty string | `users.full_name` | Name with honorific |
| `role` | Institutional responsibility | String | 0 | Enum: `course_teacher`, `mentor` | `users.role` | 7 teachers, 6 mentors |

---

### 2.9 Table: `playbook`
Catalog of codified intervention action cards (decision support catalog).

| Column | Meaning / Description | Data Type | Missing Count | Validation Rules | Target DB Field | Notes |
|---|---|---|---|---|---|---|
| `id` | Playbook card ID (e.g. `PB01`) | String | 0 | Unique | `playbook.id` | Primary Key |
| `course_code` | Target subject or `ALL` | String | 0 | Valid course code or `ALL` | `playbook.course_code` | Scope of intervention |
| `trigger` | Early warning rule trigger | String | 0 | Enum: `low_marks`, `low_attendance`, `missing_submission`, `lms_inactive` | `playbook.trigger` | Trigger condition |
| `topic` | Specific academic topic | String | 0 | E.g. "Unit 1 logic and sets", "Subnetting" | `playbook.topic` | Curriculum focus |
| `task_text` | Actionable task instructions | String | 0 | Concise, student-friendly directive | `playbook.task_text` | Action assigned to student |
| `minutes` | Estimated student effort required | Integer | 0 | Range: `[15, 45]` | `playbook.estimated_minutes` | Workload estimate |

---

## 3. Data Integrity & Validation Pipeline Rules

1. **Duplicate Prevention:** The ingestion pipeline checks existing registration numbers and composite keys (`student_id`, `course_code`, `week`).
2. **Attendance Range Constraints:** Enforced strictly via SQL check constraints `0 <= attended <= delivered` and percentage `0 <= pct <= 100`.
3. **Marks Range Constraints:** Enforced `0.0 <= marks <= 30.0` with status-aware nullability for pending evaluations.
4. **Mentor Workload Balancing:** The generator enforces a strict 10-mentee cap per mentor across the 3 sections (`6 mentors * 10 = 60 students`).
5. **Idempotence Guarantee:** Ingestion runs inside isolated database transactions (`BEGIN...COMMIT`), reporting inserted, updated, and skipped rows without duplicating state.
