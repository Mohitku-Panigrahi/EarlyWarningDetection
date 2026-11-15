"""
Demo data generator for the Explainable Academic Early-Warning System (CSE276, LPU-RISK-01).
All students, names, marks and faculty are SYNTHETIC. Table shapes mirror LPU Touch screens:
Attendance Summary (L/T/P delivered, attended, duty leave, bonus, %), Assessment list, Timetable.
Run: python generate_data.py   -> creates lpu_risk_demo.db, csv/*.csv, schema.sql   (seed fixed, reproducible)
"""
import sqlite3, hashlib, csv, os, random
from datetime import date, timedelta
import numpy as np

SEED, N, WEEKS = 42, 60, 13
TODAY, SEM_START = date(2026, 11, 4), date(2026, 8, 3)
HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "lpu_risk_demo.db")
rng = np.random.default_rng(SEED); random.seed(SEED)

# ---- courses (delivered totals copied from the real Attendance Summary screen) ----
COURSES = {  # code: (title, delivered, teacher_id, difficulty offset)
    "CSE202": ("OBJECT ORIENTED PROGRAMMING", 46, "F01", 0.00),
    "CSE205": ("DATA STRUCTURES AND ALGORITHMS", 54, "F02", -0.04),
    "CSE276": ("ARTIFICIAL INTELLIGENCE FOUNDATIONS", 33, "F03", 0.00),
    "CSE306": ("COMPUTER NETWORKS", 33, "F04", -0.02),
    "INT335": ("DESIGN THINKING", 18, "F05", 0.05),
    "MTH401": ("DISCRETE MATHEMATICS", 30, "F06", -0.06),
    "PEL134": ("UPPER INTERMEDIATE COMMUNICATION SKILLS-II", 31, "F07", 0.03),
}
FACULTY = [("F01", "Dr. Ritu Malhotra", "course_teacher"), ("F02", "Prof. Kabir Anand", "course_teacher"),
           ("F03", "Dr. Sanjay Verma", "course_teacher"), ("F04", "Prof. Neha Bajaj", "course_teacher"),
           ("F05", "Prof. Arjun Mehta", "course_teacher"), ("F06", "Dr. Sunita Rao", "course_teacher"),
           ("F07", "Prof. Ishita Kapoor", "course_teacher"),
           ("F08", "Dr. Manoj Saini", "mentor"), ("F09", "Prof. Leena Thomas", "mentor"),
           ("F10", "Dr. Pawan Chauhan", "mentor"), ("F11", "Prof. Farah Siddiqui", "mentor"),
           ("F12", "Dr. Rakesh Nanda", "mentor"), ("F13", "Prof. Tanvi Oberoi", "mentor")]
SECTIONS = ["K3P25IL", "K3P25IM", "K3P25IN"]
MENTORS = {"K3P25IL": ["F08", "F09"], "K3P25IM": ["F10", "F11"], "K3P25IN": ["F12", "F13"]}

# ---- assessments: (course, type, title, mode, assigned, due); first 9 mirror the real screenshot ----
D = date
ASSESS = [
    ("PEL134", "Presentation - Individual", "Presentation - Individual", "manual", D(2026,9,4), D(2026,10,10)),
    ("PEL134", "Interview", "Interview", "manual", D(2026,9,17), D(2026,10,30)),
    ("MTH401", "Test", "Test 1", "manual", D(2026,9,14), D(2026,9,21)),
    ("INT335", "Test", "Test", "manual", D(2026,9,1), D(2026,9,21)),
    ("INT335", "Project", "Project", "manual", D(2026,8,30), D(2026,10,23)),
    ("INT335", "Assignment - Situation based problem solving", "Assignment", "manual", D(2026,10,16), D(2026,11,30)),
    ("CSE306", "Test", "Test 1", "manual", D(2026,10,1), D(2026,10,15)),
    ("CSE276", "Test", "Test 1", "manual", D(2026,9,16), D(2026,9,17)),
    ("CSE276", "Project", "Project", "online", D(2026,9,15), D(2026,11,15)),
    ("CSE202", "Test", "Quiz 1", "manual", D(2026,9,18), D(2026,9,25)),
    ("CSE202", "Assignment", "Assignment 1", "online", D(2026,10,5), D(2026,10,20)),
    ("CSE205", "Test", "Test 1", "manual", D(2026,9,21), D(2026,9,28)),
    ("CSE205", "Assignment", "Assignment 1", "online", D(2026,10,10), D(2026,10,25)),
    ("CSE205", "Test", "Lab Practical", "manual", D(2026,10,28), D(2026,11,10)),
    ("CSE306", "Assignment", "Assignment 1", "online", D(2026,10,22), D(2026,11,12)),
    ("MTH401", "Assignment", "Assignment 1", "online", D(2026,10,12), D(2026,10,28)),
    ("MTH401", "Test", "Test 2", "manual", D(2026,10,30), D(2026,11,12)),
]
EVAL_CUTOFF = D(2026, 10, 30)

# ---- weekly timetable of section K3P25IL (from screenshot, Mon-Fri); other sections copy it ----
TT = [
 ("Monday","09:20","10:10","26-507","P","CSE202"),("Monday","10:10","11:00","37-909","L","MTH401"),
 ("Monday","12:40","13:30","37-604","T","MTH401"),("Monday","14:20","15:10","28-406","P","CSE276"),
 ("Monday","15:10","16:00","28-406","P","CSE276"),("Monday","16:00","16:50","28-406","L","PEL134"),
 ("Tuesday","12:40","13:30","37-607","L","MTH401"),("Tuesday","13:30","14:20","37-803","L","CSE276"),
 ("Tuesday","16:00","16:50","28-502A","L","CSE306"),
 ("Wednesday","09:20","10:10","37-706","L","CSE306"),("Wednesday","12:40","13:30","28-506","L","CSE202"),
 ("Wednesday","13:30","14:20","28-506","L","CSE202"),("Wednesday","14:20","15:10","28-506","L","INT335"),
 ("Wednesday","15:10","16:00","33-306","L","CSE205"),("Wednesday","16:00","16:50","33-306","L","CSE205"),
 ("Thursday","09:20","10:10","37-808","L","CSE276"),("Thursday","11:00","11:50","33-306X","L","CSE205"),
 ("Thursday","11:50","12:40","33-306X","L","CSE205"),("Thursday","13:30","14:20","28-508","L","CSE202"),
 ("Thursday","14:20","15:10","28-508","L","CSE202"),("Thursday","15:10","16:00","28-508","P","PEL134"),
 ("Thursday","16:00","16:50","28-508","P","PEL134"),
 ("Friday","09:20","10:10","33-308","P","CSE205"),("Friday","10:10","11:00","33-308","P","CSE205"),
 ("Friday","11:00","11:50","37-901","L","INT335"),("Friday","11:50","12:40","36-802","P","PEL134"),
 ("Friday","12:40","13:30","28-507A","P","CSE202"),("Friday","14:20","15:10","28-507A","P","CSE306"),
 ("Friday","15:10","16:00","28-507A","P","CSE306"),("Friday","16:00","16:50","28-507A","L","MTH401"),
]

PLAYBOOK = [  # (id, course, trigger, topic, task_text, minutes) -> also the RAG corpus for the briefing generator
 ("PB01","MTH401","low_marks","Unit 1 logic and sets","Solve 10 problems from Unit 1 (propositional logic, sets, relations) and mark them done.",40),
 ("PB02","MTH401","low_marks","Proof techniques","Write 3 proofs by induction and 2 by contradiction; bring doubts to the mentor.",45),
 ("PB03","CSE205","low_marks","Graph traversal","Trace BFS and DFS by hand on 3 graphs, then code one in your language.",45),
 ("PB04","CSE205","low_marks","Complexity","Solve 5 array/linked-list problems and state the time complexity of each.",40),
 ("PB05","CSE276","low_marks","PEAS and agents","Write PEAS descriptions for 3 environments and classify each agent type.",30),
 ("PB06","CSE276","low_marks","Bayes theorem","Solve 4 Bayes' theorem numericals with a frequency table.",30),
 ("PB07","CSE202","low_marks","OOP design","Implement a small class hierarchy using inheritance and polymorphism.",45),
 ("PB08","CSE306","low_marks","Subnetting","Solve 5 subnetting problems and draw the TCP/IP vs OSI layer table.",40),
 ("PB09","INT335","low_marks","Design thinking","Prepare an empathy map and a one-line problem statement for your project.",30),
 ("PB10","PEL134","low_marks","Communication","Record a 3-minute self-introduction and list 3 things to improve.",25),
 ("PB11","ALL","low_attendance","Attendance recovery","Meet your mentor this week and agree an attendance plan for the weakest subject.",20),
 ("PB12","ALL","missing_submission","Submissions","Submit the pending assignment within 48 hours or request an extension from the teacher.",30),
 ("PB13","ALL","lms_inactive","LMS activity","Log in to the LMS today and complete one pending activity.",15),
]
CONFIG = {"attendance_threshold_pct": 75, "internal_marks_low_pct": 0.50, "missed_assignments_for_medium": 2,
          "lms_inactive_logins_7d": 3, "benchmark_margin_pct": 0.10, "mentor_cap": 10, "risk_threshold": 0.40}

FIRST = ["Aarav","Vivaan","Aditya","Arjun","Reyansh","Krishna","Ishaan","Kabir","Rohan","Dev","Ananya","Diya","Ira",
 "Kavya","Meera","Naina","Riya","Saanvi","Tara","Zoya","Harsh","Yash","Manav","Nikhil","Pranav","Rahul","Siddharth",
 "Tanmay","Varun","Aryan","Isha","Jiya","Khushi","Lavanya","Mahi","Nisha","Pooja","Roshni","Sneha","Trisha","Ibomcha",
 "Thoiba","Bijoy","Subham","Debasish","Priyanka","Ankita","Gurpreet","Harpreet","Simran","Jaskaran","Amandeep",
 "Mohammad","Faiz","Sara","Ayesha","Joseph","Maria","Lalit","Tenzin"]
LAST = ["Sharma","Verma","Singh","Gupta","Mishra","Patel","Reddy","Nair","Das","Panda","Sahu","Behera","Mohanty","Kaur",
 "Gill","Sandhu","Khan","Ansari","Devi","Singha","Thapa","Joshi","Kulkarni","Iyer","Menon","Chatterjee","Bose","Yadav",
 "Kumar","Jha","Rana","Meitei","Sethi","Bhatt","Chopra","Malik","Saini","Tiwari","Pillai","Dsouza"]

ARCH_PARAMS = {  # att_base, skill_base, att slope over term, lms logins/week, assignment submit prob
 "strong": (0.93, 0.82, 0.0, 9.0, 0.97), "steady": (0.87, 0.66, 0.0, 7.0, 0.92),
 "struggling": (0.74, 0.44, -0.08, 3.5, 0.65), "effort_gap": (0.90, 0.66, 0.0, 7.0, 0.88),
 "disengaged": (0.68, 0.58, -0.20, 2.5, 0.60)}
DRIFT = {"disengaged": -0.12, "struggling": -0.05, "strong": 0.02}
clip = lambda x, a, b: max(a, min(b, x))
sha = lambda s: hashlib.sha256(s.encode()).hexdigest()

def comment(frac, status):
    if status == "Not Submitted": return "Submission missing. Complete and submit at the earliest."
    if status == "Absent": return "Absent for the evaluation. Contact the teacher."
    if frac >= .8: return "Strong performance. Maintain consistency."
    if frac >= .6: return "Good attempt. Revise weak concepts and justify answers."
    if frac >= .4: return "Needs improvement in fundamentals. Practise more problems."
    return "Below expectation. Meet your mentor and follow the practice plan."

# ---------------- build students ----------------
names = set()
while len(names) < N: names.add(f"{random.choice(FIRST)} {random.choice(LAST)}")
names = sorted(names); random.shuffle(names)
regs = sorted(random.sample(range(12511001, 12511999), N))
archs = ["strong"]*12 + ["steady"]*24 + ["struggling"]*9 + ["effort_gap"]*9 + ["disengaged"]*6
random.shuffle(archs)
# fixed demo personas: 0 = maths effort-gap student, 1 = disengaged, 2 = strong
for i, a in [(0, "effort_gap"), (1, "disengaged"), (2, "strong")]:
    j = archs.index(a, 3) if a in archs[3:] and archs[i] != a else i
    archs[i], archs[j] = a, archs[i] if j != i else a

ROUTES = ["LPUNEST", "JEE Main", "State CET", "Board Merit"]; RW = [.45, .25, .15, .15]
BOARDS = ["CBSE", "State Board", "ICSE"]; BW = [.50, .35, .15]
MEDIUMS = ["English", "Hindi", "Regional"]; MW = [.70, .20, .10]
REGIONS = ["North", "East", "South", "West", "Northeast"]; GW = [.30, .25, .15, .10, .20]

S = []
for i in range(N):
    a = archs[i]; ab, sb, slope, lam, psub = ARCH_PARAMS[a]
    medium = str(rng.choice(MEDIUMS, p=MW))
    weak = {}
    if a == "effort_gap":
        pool = ["CSE205", "MTH401", "CSE306", "CSE276"]
        for c in (["MTH401"] if i == 0 else random.sample(pool, random.choice([1, 2]))): weak[c] = -0.27
    att_base = clip(ab + rng.normal(0, .03), .5, .98); skill_base = clip(sb + rng.normal(0, .05), .25, .95)
    skill = {}
    for c, (_, _, _, diff) in COURSES.items():
        med = -0.05 if (c == "PEL134" and medium == "Regional") else -0.02 if (c == "PEL134" and medium == "Hindi") else 0
        skill[c] = clip(skill_base + diff + weak.get(c, 0) + med + rng.normal(0, .05), .10, .97)
    S.append(dict(idx=i, reg=str(regs[i]), name=names[i], arch=a, att_base=att_base, skill_base=skill_base,
                  slope=slope + (rng.normal(0, .02) if a not in ("struggling", "disengaged") else 0),
                  lam=lam, psub=psub, skill=skill, weak=weak, medium=medium,
                  route=str(rng.choice(ROUTES, p=RW)), board=str(rng.choice(BOARDS, p=BW)),
                  region=str(rng.choice(REGIONS, p=GW)),
                  sgpa=round(clip(1.0 + 9.5*skill_base + rng.normal(0, .35), 4.0, 9.9), 2)))
for k, s in enumerate(S): s["section"] = SECTIONS[k % 3]

# ---------------- weekly attendance ----------------
wk_deliv = {}
for c, (_, tot, _, _) in COURSES.items():
    base, rem = divmod(tot, WEEKS); extra = set(random.sample(range(WEEKS), rem))
    wk_deliv[c] = [base + (1 if w in extra else 0) for w in range(WEEKS)]
WEEKLY, SUMMARY, ACTIVITY = [], [], []
for s in S:
    s["att_c"] = {}
    for c, (_, tot, _, _) in COURSES.items():
        ac = clip(s["att_base"] + rng.normal(0, .03), .45, .99); s["att_c"][c] = ac; att = 0
        for w in range(WEEKS):
            p = clip(ac + s["slope"]*(w/(WEEKS-1) - .5) + rng.normal(0, .04), .15, 1.0)
            x = int(rng.binomial(wk_deliv[c][w], p)); att += x
            WEEKLY.append((s["reg"], c, w+1, wk_deliv[c][w], x))
        dl = int(rng.integers(1, 3)) if rng.random() < .25 else 0
        dl = min(dl, tot - att) if tot - att > 0 else 0
        SUMMARY.append((s["reg"], c, tot, att, dl, 0, min(100, round(100*(att+dl)/tot))))
    for w in range(WEEKS):
        trend = s["slope"]*3*(w/(WEEKS-1) - .5)
        ACTIVITY.append((s["reg"], w+1, int(rng.poisson(max(.3, s["lam"]*(1+trend))))))

# ---------------- assessments ----------------
A_ROWS = []; ev_flag = {}
for k, (c, typ, title, mode, asg, due) in enumerate(ASSESS, 1):
    aid = f"A{k:02d}"   # rows 1-9 mirror the screenshot: only A01, A02, A03, A08 had marks entered; rest pending
    ev_flag[aid] = due <= EVAL_CUTOFF and (k in (1, 2, 3, 8) or (k > 9 and rng.random() < .85))
    A_ROWS.append((aid, c, typ, title, mode, asg.isoformat(), due.isoformat(), 30, COURSES[c][2]))
SA = []
span = (TODAY - SEM_START).days
for s in S:
    for (aid, c, typ, title, mode, asg, due, mx, tid) in A_ROWS:
        due_d = date.fromisoformat(due)
        if not ev_flag[aid]:
            SA.append((s["reg"], aid, None, "Pending", "")); continue
        t = clip((due_d - SEM_START).days / span, 0, 1)
        sk = clip(s["skill"][c] + DRIFT.get(s["arch"], 0)*t, .05, .98)
        is_asg = typ.startswith("Assignment")
        if is_asg and rng.random() > s["psub"]:
            SA.append((s["reg"], aid, 0.0, "Not Submitted", comment(0, "Not Submitted"))); continue
        if (not is_asg) and rng.random() < {"disengaged": .08, "struggling": .04}.get(s["arch"], .01):
            SA.append((s["reg"], aid, 0.0, "Absent", comment(0, "Absent"))); continue
        fr = clip(sk + rng.normal(0, .08), .05, 1.0); m = round(mx*fr*2)/2
        SA.append((s["reg"], aid, m, "Present" if not is_asg else "Submitted", comment(m/mx, "ok")))

# ---------------- outcomes (SIMULATED end-term result, used only as training label) ----------------
OUT, SOUT = [], []
for s in S:
    fin = {}
    for c in COURSES:
        f = 100*(s["skill"][c] + .10*(s["att_c"][c] - .80) + DRIFT.get(s["arch"], 0)*.6 + rng.normal(0, .09))
        fin[c] = round(clip(f, 5, 99), 1); OUT.append((s["reg"], c, fin[c], int(fin[c] < 45)))
    v = list(fin.values())
    SOUT.append((s["reg"], round(sum(v)/len(v), 1), int(sum(v)/len(v) < 52 or sum(x < 40 for x in v) >= 2)))

# ---------------- mentor assignment: by section, 10 each, risk-balanced snake ----------------
cur = {}
for s in S:
    mk = [r for r in SA if r[0] == s["reg"] and r[2] is not None]
    mp = sum(r[2] for r in mk)/(30*len(mk)) if mk else .6
    ap = np.mean([r[6] for r in SUMMARY if r[0] == s["reg"]])/100
    cur[s["reg"]] = .6*mp + .4*ap
for sec in SECTIONS:
    grp = sorted([s for s in S if s["section"] == sec], key=lambda s: cur[s["reg"]])
    m1, m2 = MENTORS[sec]
    for j, s in enumerate(grp): s["mentor"] = m1 if (j % 4) in (0, 3) else m2

# ---------------- write sqlite ----------------
if os.path.exists(DB): os.remove(DB)
con = sqlite3.connect(DB); cu = con.cursor()
cu.executescript("""
CREATE TABLE sections(section_id TEXT PRIMARY KEY);
CREATE TABLE faculty(faculty_id TEXT PRIMARY KEY, name TEXT, role TEXT);
CREATE TABLE courses(course_code TEXT PRIMARY KEY, title TEXT, delivered_total INT, teacher_id TEXT REFERENCES faculty);
CREATE TABLE students(student_id TEXT PRIMARY KEY, name TEXT, section_id TEXT REFERENCES sections, mentor_id TEXT REFERENCES faculty,
  sem2_sgpa REAL, cgpa_band TEXT, admission_route TEXT, schooling_board TEXT, medium_of_instruction TEXT, home_region TEXT);
CREATE TABLE attendance_summary(student_id TEXT, course_code TEXT, delivered INT, attended INT, duty_leave INT, first_week_bonus INT, pct INT,
  PRIMARY KEY(student_id, course_code));
CREATE TABLE weekly_attendance(student_id TEXT, course_code TEXT, week INT, delivered INT, attended INT, PRIMARY KEY(student_id, course_code, week));
CREATE TABLE weekly_activity(student_id TEXT, week INT, lms_logins_7d INT, PRIMARY KEY(student_id, week));
CREATE TABLE assessments(assessment_id TEXT PRIMARY KEY, course_code TEXT, type TEXT, title TEXT, mode TEXT, assigned_date TEXT, due_date TEXT,
  max_marks INT, faculty_id TEXT);
CREATE TABLE student_assessments(student_id TEXT, assessment_id TEXT, marks REAL, status TEXT, teacher_comment TEXT, PRIMARY KEY(student_id, assessment_id));
CREATE TABLE timetable(section_id TEXT, day TEXT, start_time TEXT, end_time TEXT, room TEXT, kind TEXT, course_code TEXT);
CREATE TABLE outcomes_simulated(student_id TEXT, course_code TEXT, final_pct REAL, course_at_risk INT, PRIMARY KEY(student_id, course_code));
CREATE TABLE student_outcomes_simulated(student_id TEXT PRIMARY KEY, mean_final_pct REAL, at_risk INT);
CREATE TABLE sim_ground_truth(student_id TEXT PRIMARY KEY, archetype TEXT, weak_courses TEXT);  -- demo only, never a model feature
CREATE TABLE users(username TEXT PRIMARY KEY, role TEXT, password_sha256 TEXT, ref_id TEXT);
CREATE TABLE playbook(id TEXT PRIMARY KEY, course_code TEXT, trigger TEXT, topic TEXT, task_text TEXT, minutes INT);
CREATE TABLE config(key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE tasks(task_id INTEGER PRIMARY KEY AUTOINCREMENT, student_id TEXT, course_code TEXT, source TEXT, playbook_id TEXT, text TEXT,
  status TEXT DEFAULT 'open', created_at TEXT, done_at TEXT);
CREATE TABLE interventions(id INTEGER PRIMARY KEY AUTOINCREMENT, student_id TEXT, mentor_id TEXT, kind TEXT, proposed_by TEXT, decision TEXT,
  note TEXT, created_at TEXT, decided_at TEXT);
CREATE TABLE risk_scores(student_id TEXT, as_of_week INT, ml_prob REAL, rule_level TEXT, shap_json TEXT, rules_fired TEXT, counterfactual TEXT,
  PRIMARY KEY(student_id, as_of_week));
CREATE TABLE audit_log(id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, actor TEXT, action TEXT, detail TEXT);
CREATE VIEW v_aggregate_attendance AS
  SELECT student_id, SUM(delivered) delivered, SUM(attended) attended, SUM(duty_leave) duty_leave,
         MIN(100, ROUND(100.0*(SUM(attended)+SUM(duty_leave))/SUM(delivered))) pct FROM attendance_summary GROUP BY student_id;
""")
cu.executemany("INSERT INTO sections VALUES(?)", [(x,) for x in SECTIONS])
cu.executemany("INSERT INTO faculty VALUES(?,?,?)", FACULTY)
cu.executemany("INSERT INTO courses VALUES(?,?,?,?)", [(c, v[0], v[1], v[2]) for c, v in COURSES.items()])
band = lambda g: "<6" if g < 6 else "6-8" if g < 8 else "8+"
cu.executemany("INSERT INTO students VALUES(?,?,?,?,?,?,?,?,?,?)",
    [(s["reg"], s["name"], s["section"], s["mentor"], s["sgpa"], band(s["sgpa"]), s["route"], s["board"], s["medium"], s["region"]) for s in S])
cu.executemany("INSERT INTO attendance_summary VALUES(?,?,?,?,?,?,?)", SUMMARY)
cu.executemany("INSERT INTO weekly_attendance VALUES(?,?,?,?,?)", WEEKLY)
cu.executemany("INSERT INTO weekly_activity VALUES(?,?,?)", ACTIVITY)
cu.executemany("INSERT INTO assessments VALUES(?,?,?,?,?,?,?,?,?)", A_ROWS)
cu.executemany("INSERT INTO student_assessments VALUES(?,?,?,?,?)", SA)
cu.executemany("INSERT INTO timetable VALUES(?,?,?,?,?,?,?)", [(sec, *r) for sec in SECTIONS for r in TT])
cu.executemany("INSERT INTO outcomes_simulated VALUES(?,?,?,?)", OUT)
cu.executemany("INSERT INTO student_outcomes_simulated VALUES(?,?,?)", SOUT)
cu.executemany("INSERT INTO sim_ground_truth VALUES(?,?,?)", [(s["reg"], s["arch"], ",".join(s["weak"])) for s in S])
users = [("admin", "admin", sha("admin123"), "admin")] + \
        [(f"m{f[0][1:]}", "mentor", sha("mentor123"), f[0]) for f in FACULTY if f[2] == "mentor"] + \
        [(s["reg"], "student", sha("demo123"), s["reg"]) for s in S]
cu.executemany("INSERT INTO users VALUES(?,?,?,?)", users)
cu.executemany("INSERT INTO playbook VALUES(?,?,?,?,?,?)", PLAYBOOK)
cu.executemany("INSERT INTO config VALUES(?,?)", [(k, str(v)) for k, v in CONFIG.items()])
con.commit()

# ---------------- csv + schema dump ----------------
os.makedirs(os.path.join(HERE, "csv"), exist_ok=True)
for (t,) in cu.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'").fetchall():
    cur2 = con.execute(f"SELECT * FROM {t}")
    with open(os.path.join(HERE, "csv", f"{t}.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow([d[0] for d in cur2.description]); w.writerows(cur2.fetchall())
with open(os.path.join(HERE, "schema.sql"), "w") as f:
    f.write(";\n\n".join(r[0] for r in con.execute("SELECT sql FROM sqlite_master WHERE sql IS NOT NULL")) + ";\n")

# ---------------- report ----------------
n_risk = sum(r[2] for r in SOUT)
print(f"students={N}  at_risk={n_risk} ({100*n_risk/N:.0f}%)  assessments={len(A_ROWS)}  weekly_rows={len(WEEKLY)}")
for s in S[:3]:
    print("DEMO", s["reg"], s["name"], s["arch"], s["section"], s["mentor"], "weak=", list(s["weak"]))
con.close()
