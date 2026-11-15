# Rebuild Early Warning System

**Exported**: 11/4/2026, 1:30:31 AM
**Model**: gpt-6
**Version**: ChatGPT Export v1.6.0

---

## You

📎 **Attached**: Pasted text(6).txt (txt)

The idea is solid and fits the syllabus well, but I see four real weaknesses, in order of importance.

**1. The synthetic data makes your accuracy numbers meaningless.** If you generate the labels from rules over the same features, the model just rediscovers your generator, and a teacher who asks "so is 0.9 recall real?" will catch it. Train and validate on a public dataset instead. The Open University Learning Analytics Dataset (OULAD) has real LMS click data, assessment scores, and demographics such as region, prior education and deprivation band. The deprivation band and region give you a real entry-background fairness test. The UCI Student Performance dataset is a smaller fallback. Use synthetic data only to fill the three dashboards for the demo, and say so.

**2. "Early warning" has to be proven, not claimed.** Add one chart: **recall versus week**. Train on data available up to week 2, 4, 6 and 8 only, and plot how early the system catches at-risk students. It is the single most convincing visual for the project, it shows you understand leakage and time splits, and it answers "why does this matter?" better than any dashboard.

**3. The benchmark trigger needs tightening.** "Below class median" always flags about half the class. Trigger on any of three things instead: a score below an absolute floor, a drop against the student's own recent average, or an effort-outcome gap (high attendance, low marks). Then check how many students you flag per week, because alert fatigue kills these systems.

**4. Student-side labels can backfire.** Showing a first-year student "AT RISK" in red can demotivate them. Show "Watch" with the task list and the improvement trend, and keep the raw probability and peer comparison mentor-only. This is a genuine Responsible AI point, and you can cite it in the viva.

Smaller cuts and adjustments:

- **Agents:** build the four agents as four plain functions in a pipeline. If you oversell "agentic AI" and the teacher asks what makes them autonomous, you will struggle.
- **Teacher ranking:** with 10 mentees each, the differences are mostly noise. Present it as "mentor load and mentee trend", not a ranking.
- **Scope:** build the mentor dashboard as the hero (radar, SHAP waterfall, counterfactual, briefing). Keep the student and admin pages thin. The marks are for CO3 to CO5 understanding, not UI polish.
- **Intervention effect:** you can't claim that tasks improve marks without outcome data. Put "measure intervention uplift" under future work, which is where the reinforcement-learning slide fits.

**Next 24 hours:** download OULAD, load the student info, assessment and VLE click tables in pandas, and print the class balance of the final result. If at-risk is under 20%, that decides your metrics (recall and PR-AUC, not accuracy). Then ask me for the feature pipeline and the week-by-week training setup.

**Use a Random Forest as your final model, calibrated and threshold-tuned for recall, with Logistic Regression and a Decision Tree beside it as baselines.** Compare it against one gradient-boosting challenger.

**Why Random Forest for this project**

- **Fit for the data:** your data is tabular (attendance, marks, submissions, LMS activity), with a few thousand rows at most. Tree ensembles beat neural networks here, and a forest needs little tuning.
- **Fit for the course:** it is in your CO4 supervised list, so you can explain it in the viva (bagging, random feature subsets, voting).
- **Fit for explainability:** SHAP's `TreeExplainer` is exact and fast on forests, which feeds your waterfall chart, counterfactuals and briefing generator.
- **Robustness:** it handles non-linear thresholds (such as attendance below 75%), mixed feature types, and noisy data without heavy scaling.

**The challenger:** `HistGradientBoostingClassifier` from scikit-learn (or LightGBM). It usually gains 1 to 3 points on tabular data but overfits more easily on small datasets. Keep the forest unless the boosted model wins clearly on cross-validated PR-AUC. If it wins by under about 2 points, the forest's simplicity and course alignment are worth more.

**The role of each model**

| Model | Role |
| --- | --- |
| Logistic Regression | Baseline; coefficients are readable |
| Decision Tree (depth 3 to 4) | Draw it as a tree; its splits mirror your R1 to R3 rules |
| **Random Forest** | **Production model** |
| Gradient boosting | Challenger |
| k-means | Unsupervised behaviour clusters, not risk scoring |

**What matters more than the algorithm**

1. **Time-aware features and split:** train on data up to week N only, so you avoid leakage and can plot recall against week.
2. **Imbalance:** use `class_weight="balanced_subsample"` and judge by recall, PR-AUC and F2, not accuracy.
3. **Calibration:** wrap the forest in `CalibratedClassifierCV` (isotonic if you have over about 1,000 rows, otherwise sigmoid). Raw forest probabilities are poorly calibrated, and you will show "probability of risk" to a mentor.
4. **Threshold:** choose it on a validation fold so recall reaches at least 0.80, then report the precision cost.
5. **Final design:** a calibrated forest plus the rule engine, and flag "manual review" when the two disagree.

**Starting configuration**

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV

rf = RandomForestClassifier(
    n_estimators=400, max_depth=8, min_samples_leaf=5,
    class_weight="balanced_subsample", random_state=42, n_jobs=-1)
model = CalibratedClassifierCV(rf, method="isotonic", cv=5)

```

Tune only `max_depth`, `min_samples_leaf` and `max_features` with stratified 5-fold cross-validation. Anything more is wasted effort at this data size.

**Next 24 hours:** train the logistic regression, depth-4 tree and this forest on one dataset with identical 5-fold splits, and print recall, PR-AUC and F2 in one table. That table decides your final model, and it becomes the "model comparison" slide.

This the Early Warnign projects details we will start creating it again lets build it usinf stitch and antigravity or any better tools that i can use in free plan , i have only gemini pro nothing else what do you say

## ChatGPT

*Refining the project plan*

*Refined the project plan*

*Searched 23 websites*

*Worked for 22s*

Bro, I actually think we should rebuild this project from the ground up. And this time, I want us to approach it like we're building a product that could genuinely be demonstrated to a university administration team, not just a college assignment. 🔥

Your **Explainable Academic Early-Warning and Intervention Decision System (LPU-RISK-01)** has enough technical depth to become one of your strongest academic projects.

But I want to make one important change:

**We will build the AI system first, prove that it works, and then build the interface around its actual outputs.**

No beautiful dashboard displaying fake AI predictions. No claiming 90% accuracy on synthetic data. No unnecessary agentic-AI frameworks.

## 1. My recommended technology stack

| Layer | Technology | Purpose |
| --- | --- | --- |
| UI design | Google Stitch | Design all four role-based interfaces |
| Development | Google Antigravity | Build, integrate, debug and test |
| Frontend | React + TypeScript | Interactive dashboards |
| Styling | Tailwind CSS | Consistent design system |
| Charts | Recharts | Radar, SHAP, trends and fairness |
| Backend | Python + FastAPI | ML and application APIs |
| Database | SQLite initially | Store users, records, predictions and interventions |
| ML | Scikit-learn | Classification and clustering |
| Explainability | SHAP | Explain individual predictions |
| Data processing | Pandas + NumPy | Feature engineering |
| Testing | Pytest | Backend and model verification |

I would not introduce Docker, Kubernetes, microservices or expensive cloud infrastructure. They add complexity without helping us demonstrate the actual syllabus outcomes.

## 2. The tools I would actually use

<box gap={3}>
<row align=start gap={3}>
<AsyncImage query="Google Stitch AI interface design canvas screenshot" aspectRatio="5:4" maxWidth="108px"/>
<box flex="1" gap={1}>
**1. <Entity value="Google Stitch" category="software" disambig="AI-powered UI design tool by Google Labs"/>**
<badge color="success">Use it</badge>
Design the landing page, student dashboard, mentor dashboard and admin dashboard. Establish a common design system before implementation.

<text color="secondary" size="xs"><Link url="https://stitch.withgoogle.com/" title="Open Stitch"/> · Free access subject to current usage limits.</text>
</box>
</row>
<divider color="subtle"/>
<row align=start gap={3}>
<AsyncImage query="Google Antigravity IDE agent manager code editor screenshot" aspectRatio="5:4" maxWidth="108px"/>
<box flex="1" gap={1}>
**2. <Entity value="Google Antigravity" category="software" disambig="AI agentic development IDE"/>**
<badge color="success">Primary development tool</badge>
Let it inspect the project, plan implementation, write code, run tests, debug and integrate frontend with backend.

Your Google AI Pro subscription provides higher Antigravity usage limits than the individual free plan. <Cite refs={["turn135764search0","turn135764search2"]}/>

<text color="secondary" size="xs"><Link url="https://antigravity.google/" title="Open Antigravity"/></text>
</box>
</row>
<divider color="subtle"/>
<row align=start gap={3}>
<AsyncImage query="Google AI Studio developer interface prompt playground" aspectRatio="5:4" maxWidth="108px"/>
<box flex="1" gap={1}>
**3. <Entity value="Google AI Studio" category="software" disambig="Gemini developer platform"/>**
<badge color="success">Free supplementary tool</badge>
Use it to experiment with Gemini, structured outputs and the briefing generator. Free API access has model-specific limits; don't assume your Gemini Pro subscription means unlimited API calls. <Cite refs={["turn135764search1","turn135764search16"]}/>

<text color="secondary" size="xs"><Link url="https://aistudio.google.com/" title="Open AI Studio"/></text>
</box>
</row>
<divider color="subtle"/>
<row align=start gap={3}>
<AsyncImage query="GitHub desktop repository code version control interface" aspectRatio="5:4" maxWidth="108px"/>
<box flex="1" gap={1}>
**4. <Entity value="GitHub" category="software" disambig="Code hosting and version control platform"/>**
<badge color="success">Essential</badge>
Keep every stable milestone committed. Antigravity should never be allowed to rewrite the entire working application without checkpoints.

<text color="secondary" size="xs"><Link url="https://github.com/" title="Open GitHub"/></text>
</box>
</row>
<divider color="subtle"/>
<row align=start gap={3}>
<AsyncImage query="DBeaver SQLite database table viewer interface" aspectRatio="5:4" maxWidth="108px"/>
<box flex="1" gap={1}>
**5. <Entity value="DB Browser for SQLite" category="software" disambig="Free SQLite database management application"/>**
<badge>Optional</badge>
Inspect actual database tables and records during your administration presentation.

<text color="secondary" size="xs"><Link url="https://sqlitebrowser.org/" title="Open DB Browser"/></text>
</box>
</row>
</box>

**My decision:** Stitch + Antigravity + GitHub + your local Python environment are sufficient. I wouldn't pay for another AI coding subscription.

## 3. One important research upgrade: OULAD

I want to change one thing from the original project document.

The original specification proposed approximately 1,000 synthetic students. <FileCite ref_id="turn0file0" line_range_start={88} line_range_end={99}/> Your newer approach of using OULAD is stronger.

<row align=center gap={3}>
<AsyncImage query="Open University Learning Analytics Dataset OULAD data visualization student learning analytics" aspectRatio="5:4" maxWidth="112px"/>
<box flex="1" gap={1}>
**<Entity value="Open University Learning Analytics Dataset (OULAD)" category="other" disambig="Public educational data research dataset"/>**

<badge color="success">Recommended primary dataset</badge>
<text color="secondary" size="xs">32,593 students · 22 module presentations · 7 relational CSV tables</text>
<text size="xs"><Link url="https://analyse.kmi.open.ac.uk/open_dataset" title="Official dataset"/> · <Link url="https://archive.ics.uci.edu/dataset/349/open+university+learning+analytics+dataset" title="UCI download"/></text>
</box>
</row>

It contains:

- Student demographics and entry education.
- Assessment scores and submission dates.
- Daily VLE interactions and click counts.
- Regional and deprivation-band information.
- Final outcomes: Fail, Pass, Distinction and Withdrawn.

<Cite refs={["turn950932search2","turn950932search4"]}/>

However, there's an important research limitation:

**OULAD does not contain LPU attendance records or LPU subject-wise marks.** It is also historical UK distance-learning data, not a representative sample of LPU students.

Therefore, we'll do the following:

| Component | Data source |
| --- | --- |
| ML training | Real OULAD records |
| Week-by-week prediction | OULAD assessment and VLE activity |
| Fairness audit | OULAD entry education, region and deprivation bands |
| LPU-style student profiles | Clearly labelled demonstration records |
| Mentor assignment | Demo institution configuration |
| LPU subject radar | Demo records, not claimed as OULAD measurements |

We must never present demo records as real university data.

One more detail: we'll define the prediction target explicitly. For example, predicting `Fail` versus `Pass/Distinction` is different from predicting `Withdrawn`. We should report them separately rather than quietly combining different academic outcomes.

## 4. The architecture I want us to build

<box border radius="lg" padding={3} gap={2}>
<title size="lg">LPU-RISK-01</title>
<text color="secondary" size="xs">EXPLAINABLE ACADEMIC INTELLIGENCE PLATFORM</text>
<box background="rgba(59,130,246,0.08)" radius="md" padding={3} align=center>
**React + TypeScript Frontend**
<text color="secondary" size="xs">Student · Mentor · Admin · Evaluation</text>
</box>
<box align=center>
<icon name="arrow-down" color="secondary" size="lg"/>
</box>
<box background="rgba(16,185,129,0.08)" radius="md" padding={3} align=center>
**FastAPI Backend**
<text color="secondary" size="xs">Authentication · Permissions · API · Audit log</text>
</box>
<box align=center>
<icon name="arrow-down" color="secondary" size="lg"/>
</box>
<grid columns={2} gap={2}>
<grid-item>
<box border radius="md" padding={2} gap={1}>
**ML Engine**
<text size="xs" color="secondary">Logistic Regression · Decision Tree · Random Forest · Gradient Boosting</text>
</box>
</grid-item>
<grid-item>
<box border radius="md" padding={2} gap={1}>
**Reasoning Engine**
<text size="xs" color="secondary">Production rules · Bayes · Risk fusion</text>
</box>
</grid-item>
<grid-item>
<box border radius="md" padding={2} gap={1}>
**Explainability**
<text size="xs" color="secondary">SHAP · Counterfactual · Fairness</text>
</box>
</grid-item>
<grid-item>
<box border radius="md" padding={2} gap={1}>
**Intervention Engine**
<text size="xs" color="secondary">Monitor · Risk · Explainer · Planner</text>
</box>
</grid-item>
</grid>
<box align=center>
<icon name="arrow-down" color="secondary" size="lg"/>
</box>
<box background="rgba(245,158,11,0.08)" radius="md" padding={3} align=center>
**SQLite Database**
<text color="secondary" size="xs">Users · Students · Weekly records · Predictions · Tasks · Approvals · Audit</text>
</box>
</box>

I would keep the four agents as ordinary Python modules/functions, as your revised specification recommends. No LangChain or multi-agent framework is necessary.

---

## 5. The four dashboards

<box gap={3}>
<row align=start gap={3}>
<AsyncImage query="premium modern student academic dashboard UI dark navy blue progress analytics cards" aspectRatio="5:4" maxWidth="116px"/>
<box flex="1" gap={1}>
**Student dashboard**

- On Track / Watch / At Risk
- Subject performance radar
- Weekly improvement graph
- Today's practice tasks
- Three understandable reasons behind the status
Students should see supportive language, not intimidating risk probabilities.
</box>
</row>
<divider color="subtle"/>
<row align=start gap={3}>
<AsyncImage query="premium education mentor analytics dashboard dark theme student risk analytics SHAP charts" aspectRatio="5:4" maxWidth="116px"/>
<box flex="1" gap={1}>
**Mentor dashboard**
- Ten assigned mentees
- Risk and performance trends
- Attendance versus marks scatter plot
- Individual SHAP waterfall
- Counterfactual explanation
- AI-generated student briefing
- Approve / Edit / Reject interventions
<badge color="success">Our hero dashboard</badge>
</box>
</row>
<divider color="subtle"/>
<row align=start gap={3}>
<AsyncImage query="enterprise university administrator dashboard education analytics fairness heatmap dark interface" aspectRatio="5:4" maxWidth="116px"/>
<box flex="1" gap={1}>
**Admin dashboard**
- Student risk distribution
- Subject and section heatmap
- Mentor workload and mentee trends
- Fairness gap analysis
- Model performance and calibration
- Configurable risk thresholds
- Audit logs
</box>
</row>
<divider color="subtle"/>
<row align=start gap={3}>
<AsyncImage query="machine learning evaluation dashboard precision recall PR curve confusion matrix calibration chart dark UI" aspectRatio="5:4" maxWidth="116px"/>
<box flex="1" gap={1}>
**Research and evaluation dashboard**
- Model comparison
- Recall versus week
- PR-AUC and F2
- Confusion matrix
- Calibration curve
- Fairness metrics
- Feature importance
This is particularly important for your CO4 and CO5 viva.
</box>
</row>

</box>

## 6. Our development roadmap

I don't want Antigravity generating 50 files in one shot. We'll build in controlled milestones.

<list connector="solid" marker="number" gap={3}>
<list-item>
**Phase 0 — Research and data foundation**

- Download OULAD.
- Inspect all CSV schemas.
- Establish prediction target.
- Check class distribution.
- Create data-quality report.
- Build week-based feature extraction.
<badge color="success">First milestone</badge>
</list-item>
<list-item>
**Phase 1 — Machine learning laboratory**
- Logistic Regression.
- Decision Tree (depth 4).
- Random Forest.
- HistGradientBoosting challenger.
- Identical cross-validation splits.
- Recall, precision, PR-AUC and F2.
- Probability calibration and threshold selection.
- Recall versus week chart.
</list-item>
<list-item>
**Phase 2 — Explainable AI and fairness**
- Global and individual SHAP.
- Counterfactual explanations.
- Fairness across entry-background groups.
- K-means behavioural clusters.
- Rule engine and Bayesian reasoning.
</list-item>
<list-item>
**Phase 3 — Backend and database**
- FastAPI.
- SQLite schema.
- Role-based authentication.
- Access permissions.
- Prediction storage.
- Intervention approval and audit logs.
</list-item>
<list-item>
**Phase 4 — Stitch UI and frontend**
- Design system.
- Landing and login.
- Student dashboard.
- Mentor dashboard.
- Admin dashboard.
- Evaluation dashboard.
- Connect real API data.
</list-item>
<list-item>
**Phase 5 — Intelligence and integration**
- Four Python agents.
- RAG-based mentor briefing.
- Human approval workflow.
- Intervention recommendation engine.
- Model disagreement and manual review.
</list-item>
<list-item>
**Phase 6 — Final engineering**
- End-to-end testing.
- Security and permissions testing.
- Reproducible model training.
- Documentation and GitHub README.
- Deployment/demo preparation.
- CO3–CO5 viva preparation.
</list-item>

</list>

One technical rule: week 2, 4, 6 and 8 predictions must only use information available by those cutoffs. We'll also prevent student records from leaking across training and validation splits. Calibration and threshold tuning must use validation data, never the final test set.

## 7. Some engineering decisions I want to lock

| Decision | Our approach |
| --- | --- |
| Primary model | Calibrated Random Forest |
| Main metric | Recall |
| Imbalance metric | PR-AUC and F2 |
| Target recall | 0.80, if achievable |
| Alert threshold | Validation-tuned |
| ML disagreement | Manual review |
| Intervention | Human approval required |
| RL | Future research only |
| LLM | Optional briefing polish |
| Hosting | Local-first initially |

Also, we should not promise that Random Forest will win. It earns the production role only if the actual evaluation supports it.

## 8. What I need you to do first

Let's establish the project workspace before touching Stitch.

Your existing Windows laptop with 16 GB RAM and integrated graphics is sufficient for this workload. We'll use CPU-based scikit-learn and process OULAD's large clickstream CSV efficiently rather than loading everything unnecessarily.

Create this folder:

```text
LPU-RISK-01/
│
├── research/
│   ├── dataset/
│   └── notebooks/
│
├── ml_engine/
│   ├── data/
│   ├── features/
│   ├── models/
│   ├── evaluation/
│   ├── explainability/
│   └── fairness/
│
├── backend/
│   ├── app/
│   └── tests/
│
├── frontend/
│
├── database/
├── documentation/
├── scripts/
└── README.md
```

Our first Antigravity instruction will be to inspect the environment, establish dependencies, download or import OULAD, inspect its tables and produce a dataset report. **It must not start building the frontend yet.**

---

## My final recommendation

I would stick with Stitch and Antigravity. You already have the right tools, and buying another subscription would not solve the difficult part of this project.

What will distinguish this project is not how many AI tools we use. It is whether we can demonstrate:

1. A model trained on real educational data.
2. Evidence that it identifies struggling students earlier.
3. Explanations that a mentor can understand.
4. A fairness audit that reveals potential bias.
5. An intervention process where humans retain control.

**Let's build LPU-RISK-01 as a research-backed academic intelligence platform, not just another student management dashboard.**

Our first deliverable should be the OULAD data pipeline and its actual class-balance report. Then we move to model development, and only after that do we design the final Stitch screens.

Useful references: <Link url="https://analyse.kmi.open.ac.uk/open_dataset" title="OULAD"/> · <Link url="https://stitch.withgoogle.com/" title="Stitch"/> · <Link url="https://antigravity.google/" title="Antigravity"/> · <Link url="https://scikit-learn.org/stable/" title="Scikit-learn"/>.

## You

Unit I Foundations of Artificial Intelligence : Introduction to Artificial Intelligence: Its history and evolution, characteristics and types of Artificial Intelligence, Artificial Intelligence vs Machine Learning vs Deep Learning vs Data Science, Intelligent systems & Artificial Intelligence lifecycle, applications of Artificial Intelligence in healthcare, agriculture, finance, education, manufacturing, robotics and smart cities Artificial Intelligence Problem Solving : Artificial Intelligence problem formulation and state-space representation, problem characteristics, search space and solution space, performance measures, overview of Artificial Intelligence based problem-solving approaches. Unit II Problem Solving using Search Techniques : Uninformed search (Breadth First Search and Depth First Search), informed search (Best First Search, Hill Climbing and A* Search), heuristic functions, comparison and applications of search algorithms Knowledge Representation and Reasoning : Knowledge representation, semantic networks & frames, Production systems & expert systems, Propositional logic & first-order predicate logic, Reasoning under uncertainty using Bayes' theorem Unit III Intelligent Agents : Introduction to intelligent agents and agent architecture, PEAS Framework: Performance Measure, Environment, Actuators and Sensors, Rational agents & agent environments, simple reflex agents & model-based agents, goal-based agents, utility-based agents & learning agents, Autonomous intelligent systems and multi-agent systems, cooperation and coordination, human-AI collaboration and applications of intelligent agents Unit IV Evolution of Modern Artificial Intelligence : Symbolic and statistical Artificial Intelligence, Overview of Machine Learning and its types: supervised, unsupervised and reinforcement learning, Introduction to Deep Learning, Types and applications of Deep Learning Foundation Models and Modern Artificial Intelligence Paradigms : Foundation models, multimodal Artificial Intelligence, Agentic Artificial Intelligence, Edge Artificial Intelligence and Tiny Artificial Intelligence Unit V Generative Artificial Intelligence : Generative Artificial Intelligence concepts and their applications, Large Language Models, prompt engineering fundamentals and prompt design techniques, Retrieval-Augmented Generation (RAG), Hallucination in Large Language Models and their mitigation strategies Responsible and Explainable Artificial Intelligence : Explainable Artificial Intelligence, fairness, bias and transparency, Responsible Artificial Intelligence principles: privacy and security, Artificial Intelligence governance, ethical and societal implications.

these are the topics we have in our cse276 course so the main project can take or use if necessary from these process and methods

## ChatGPT

*Worked for 39s*

Now this changes how I want to architect LPU-RISK-01. And honestly, it makes the project much more interesting!

We have the complete CSE276 syllabus now, so we can design the project around **demonstrable AI concepts from all five units**, rather than adding AI features just to make the project look advanced.

My recommendation: make LPU-RISK-01 a practical implementation of the syllabus, with the academic early-warning problem as its central application.

The important distinction is:

- The project should solve one meaningful problem.
- Every AI technique should have a clear responsibility.
- Every syllabus concept should have visible evidence in the application or its technical evaluation.
- We should not force unrelated topics into the project.

# 1. Mapping all five units to LPU-RISK-01

Here is how I would map the syllabus.

## Unit I — Foundations of Artificial Intelligence

<badge color="success">Core implementation</badge>

| Syllabus topic | How we implement it |
| --- | --- |
| History and evolution of AI | Project documentation and viva explanation |
| Characteristics and types of AI | Explain the system as a narrow AI application |
| AI vs ML vs DL vs Data Science | Architecture documentation |
| Intelligent systems | Complete LPU-RISK-01 application |
| AI lifecycle | Data → preprocessing → training → evaluation → deployment → monitoring |
| AI applications in education | Academic early-warning and intervention system |
| Problem formulation | Define students, academic outcomes, observations and interventions |
| State-space representation | Model academic states and possible support actions |
| Problem characteristics | Partially observable, uncertain, sequential decision-making |
| Search space and solution space | Search for suitable interventions |
| Performance measures | Recall, PR-AUC, F2, fairness gap, explanation coverage |

**Practical implementation:**

We'll create a formal problem definition:

- Initial state: student's current academic profile.
- Observations: marks, attendance, submissions and learning activity.
- Goal state: improved academic engagement and academic performance.
- Actions: recommend practice, mentor meeting, study planning.
- Constraints: limited mentor capacity, intervention costs and human approval.

We can also create an AI lifecycle diagram on the evaluation page.

## Unit II — Problem Solving using Search Techniques and Knowledge Representation

<badge color="success">Core implementation</badge>

This unit gives us an opportunity to make the project more than a classification application.

### A. Search algorithms

| Algorithm | Project application | Demonstration |
| --- | --- | --- |
| BFS | Explore possible intervention sequences by number of steps | Search tree |
| DFS | Explore a possible support strategy deeply | Search traversal |
| Best First Search | Prioritise interventions using a heuristic | Ranked search paths |
| Hill Climbing | Iteratively improve an intervention plan | Before/after plan |
| A* Search | Find a low-cost intervention sequence | Optimal path under defined costs |

For example, suppose a student has low mathematics marks.

The system can explore:

<box border radius="lg" padding={3} gap={2}>
**Intervention planning search**
<box background="rgba(59,130,246,0.09)" padding={3} radius="md" align=center>
**Initial state**

<text color="secondary" size="xs">Mathematics performance below target</text>
</box>
<box align=center>
<icon name="arrow-down" color="secondary"/>
</box>
<grid columns={2} gap={2}>
<grid-item>
<box border radius="md" padding={2} align=center>
**Action A**

<text size="xs" color="secondary">Practice exercises</text>
</box>
</grid-item>
<grid-item>
<box border radius="md" padding={2} align=center>
**Action B**

<text size="xs" color="secondary">Mentor meeting</text>
</box>
</grid-item>
<grid-item>
<box border radius="md" padding={2} align=center>
**Action C**

<text size="xs" color="secondary">Topic revision</text>
</box>
</grid-item>
<grid-item>
<box border radius="md" padding={2} align=center>
**Action D**

<text size="xs" color="secondary">Combined support</text>
</box>
</grid-item>
</grid>
<box align=center>
<icon name="arrow-down" color="secondary"/>
</box>
<box background="rgba(16,185,129,0.09)" padding={3} radius="md" align=center>
**Goal state**

<text color="secondary" size="xs">A feasible, mentor-approved support plan</text>
</box>
</box>

Important: these algorithms will search a defined action-state graph. They won't magically predict which intervention improves marks. Actual intervention effectiveness requires outcome data.

### B. Heuristic functions

We can define a transparent heuristic based on:

- Expected academic relevance.
- Estimated time to complete.
- Mentor workload.
- Student effort required.
- Priority of the academic problem.

A* can use:

$$
f(n)=g(n)+h(n)
$$

Where:

- $g(n)$: cost accumulated so far.
- $h(n)$: estimated remaining cost to reach the goal.

### C. Knowledge representation

This is where we can demonstrate multiple syllabus concepts.

| Concept | Implementation |
| --- | --- |
| Frames | Student, Subject, Assessment and Mentor frames |
| Semantic networks | Student → Subject → Assessment → Risk factor → Intervention |
| Production systems | Configurable R1, R2 and R3 rules |
| Expert systems | Academic support recommendation engine |
| Propositional logic | Rule conditions and logical combinations |
| First-order predicate logic | Predicates such as `LowAttendance(student, subject)` |
| Bayes' theorem | Update risk belief after observing academic signals |

Example production rules:

```python
R1:
IF attendance < 75%
THEN trigger attendance_review

R2:
IF marks_drop > 15
THEN trigger academic_review

R3:
IF attendance >= 80%
AND marks < 40
THEN trigger effort_outcome_gap
```

These are illustrative thresholds. We'll configure them separately from the OULAD model and validate them before presenting them as useful rules.

For Bayesian reasoning:

$$
P(Risk\mid Evidence)=
\frac{P(Evidence\mid Risk)P(Risk)}
{P(Evidence)}
$$

We can display prior probability, likelihood and updated probability on the mentor's student detail page.

---

## Unit III — Intelligent Agents

<badge color="success">Core implementation</badge>

This unit is a natural fit for our project.

Instead of claiming that we are creating autonomous AI agents with independent intelligence, we'll implement four specialised agents as ordinary Python components with clear responsibilities.

<box border radius="lg" padding={3} gap={3}>
<title size="lg">LPU-RISK-01 Agent Pipeline</title>
<box background="rgba(59,130,246,0.08)" padding={3} radius="md" gap={1}>
<row align=center>
**01. Monitor Agent**
<spacer/>
<badge>Observe</badge>
</row>
Reads incoming academic records and detects changes in student behaviour.
</box>
<box align=center>
<icon name="arrow-down" color="secondary"/>
</box>
<box background="rgba(59,130,246,0.08)" padding={3} radius="md" gap={1}>
<row align=center>
**02. Risk Agent**
<spacer/>
<badge>Analyse</badge>
</row>
Runs ML predictions, production rules and Bayesian reasoning.
</box>
<box align=center>
<icon name="arrow-down" color="secondary"/>
</box>
<box background="rgba(59,130,246,0.08)" padding={3} radius="md" gap={1}>
<row align=center>
**03. Explainer Agent**
<spacer/>
<badge>Explain</badge>
</row>
Produces SHAP explanations, rule traces and counterfactuals.
</box>
<box align=center>
<icon name="arrow-down" color="secondary"/>
</box>
<box background="rgba(16,185,129,0.08)" padding={3} radius="md" gap={1}>
<row align=center>
**04. Planner Agent**
<spacer/>
<badge>Recommend</badge>
</row>
Searches possible support actions and proposes a plan.
</box>
<box align=center>
<icon name="arrow-down" color="secondary"/>
</box>
<box border={{size:1,color:"#16A34A"}} padding={3} radius="md" align=center>
**Human mentor decision**

<text color="secondary" size="xs">Approve · Edit · Reject</text>
</box>
</box>

### PEAS framework

We should explicitly document PEAS for the complete system.

| PEAS component | LPU-RISK-01 |
| --- | --- |
| Performance measure | Recall, fairness, intervention review time, explanation coverage |
| Environment | Students, mentors, subjects and academic records |
| Actuators | Alerts, task recommendations, mentor briefing and audit actions |
| Sensors | Attendance, assessment scores, submissions and LMS interactions |

### Agent architectures

We can demonstrate:

- Simple reflex agent: responds to a predefined rule.
- Model-based agent: maintains a student's recent academic state.
- Goal-based agent: searches for a support plan.
- Utility-based agent: balances intervention relevance and mentor effort.
- Learning agent: future extension using observed intervention outcomes.

### Multi-agent systems and collaboration

Our four components cooperate through a shared student state and structured outputs.

The mentor remains the final decision-maker.

That demonstrates human-AI collaboration and coordination without pretending that our Python functions are fully autonomous agents.

---

## Unit IV — Evolution of Modern Artificial Intelligence

<badge color="success">Core concepts + selective implementation</badge>

This unit needs some careful scope management.

We should implement the ML paradigms that genuinely help the application, and explain the others through architecture and demonstrations rather than adding unnecessary neural networks.

| Syllabus concept | Our implementation |
| --- | --- |
| Symbolic AI | Rules, logic, frames and expert system |
| Statistical AI | Bayesian reasoning |
| Supervised learning | Logistic Regression, Decision Tree, Random Forest, Gradient Boosting |
| Unsupervised learning | K-means behavioural clustering |
| Reinforcement learning | Future work: learn intervention policies from outcome data |
| Deep learning | Explain why it is unnecessary for our current tabular dataset |
| Foundation models | Optional Gemini-based briefing polish |
| Multimodal AI | Explain potential integration of text, marks and learning activity |
| Agentic AI | Four specialised components coordinating in a pipeline |
| Edge AI | Local CPU inference and local database |
| Tiny AI | Lightweight rule engine and compact prediction pipeline |

### One feature worth adding: behavioural clustering

K-means can identify different academic behaviour patterns without using the risk label.

For example:

- Consistent learners.
- Irregular learners.
- High-effort, low-outcome learners.
- Low-engagement learners.

We can use PCA to display these clusters in a 2D visualisation.

We must not treat clusters as psychological diagnoses or assume they represent fixed student identities.

### What about deep learning and foundation models?

We don't need to train a neural network on a relatively small tabular dataset.

Instead, our viva can explain why a Random Forest is more appropriate for the primary task, while Gemini can optionally help convert verified evidence into readable mentor briefings.

That is a stronger engineering decision than using deep learning just because it is in the syllabus.

---

## Unit V — Generative AI, Responsible AI and Explainable AI

<badge color="success">Core implementation</badge>

This is another major strength of our project.

### A. Generative AI and LLMs

We can build a mentor briefing generator that converts structured academic evidence into a short, readable briefing.

Example:

<box border radius="lg" padding={3} gap={2}>
<row align=center justify=between>
**AI-generated mentor briefing**
<badge color="success">Evidence-backed</badge>
</row>
**Student academic observation**

- Mathematics marks have declined over recent weeks.
- Attendance remains relatively high.
- Assignment completion has decreased.
- The ML model identifies mathematics performance and assignment completion as important risk factors.
<divider color="subtle"/>
**Suggested mentor briefing**
The student appears to be maintaining attendance but experiencing difficulty translating effort into academic performance. Review the mathematics topics causing difficulty and discuss assignment completion barriers. Consider a focused revision plan followed by a progress review.
<text color="secondary" size="xs">Illustrative example, not an actual student prediction.</text>

</box>

We will demonstrate:

| Topic | Implementation |
| --- | --- |
| LLM | Optional Gemini integration |
| Prompt engineering | Structured role, context, constraints and output format |
| Prompt design | Few-shot examples and evidence-grounded instructions |
| RAG | Retrieve relevant passages from an academic intervention playbook |
| Hallucination mitigation | Restrict generation to supplied facts and retrieved passages |
| Verification | Display source passages and require mentor approval |

### B. Retrieval-Augmented Generation

Our RAG pipeline:

<box border radius="lg" padding={3} gap={2}>
<box background="rgba(59,130,246,0.08)" padding={3} radius="md" align=center>
**Student's verified academic evidence**
</box>
<box align=center>
<icon name="arrow-down" color="secondary"/>
</box>
<box background="rgba(59,130,246,0.08)" padding={3} radius="md" align=center>
**Retrieve relevant playbook passages**
<text color="secondary" size="xs">TF-IDF or lightweight retrieval</text>
</box>
<box align=center>
<icon name="arrow-down" color="secondary"/>
</box>
<box background="rgba(59,130,246,0.08)" padding={3} radius="md" align=center>
**Prompt construction**
<text color="secondary" size="xs">Verified facts + retrieved context + output constraints</text>
</box>
<box align=center>
<icon name="arrow-down" color="secondary"/>
</box>
<box background="rgba(16,185,129,0.08)" padding={3} radius="md" align=center>
**Mentor briefing**
<text color="secondary" size="xs">Recommendations with supporting evidence</text>
</box>
</box>

We should keep the briefing useful even when Gemini is unavailable. The template-based generator will be the reliable fallback.

### C. Explainable AI

This will be one of the most important parts of the mentor dashboard.

| Technique | Where it appears |
| --- | --- |
| Global SHAP | Admin model insights |
| Individual SHAP | Mentor student detail |
| SHAP waterfall | Why a prediction was made |
| Counterfactual | What actionable change could alter the prediction |
| Feature importance | Model evaluation |
| Model comparison | Evaluation dashboard |

Example:

<box border radius="lg" padding={3} gap={2}>
**Why was this student flagged?**
<text color="secondary" size="xs">Illustrative SHAP explanation</text>
{#each [{n:"Low assessment score",v:0.34},{n:"Declining submissions",v:0.23},{n:"LMS inactivity",v:0.17},{n:"Attendance",v:-0.12}] as item}
<box gap={1}>
<row justify=between>
<text size="sm" weight="medium">{item.n}</text>
<text size="sm" tabularNums color={item.v>0?"danger":"success"}>{item.v>0?"+":""}{item.v.toFixed(2)}</text>
</row>
<box background="surface-tertiary" height="9px" radius="full" clip>
<box background={item.v>0?"#DC7777":"#16A34A"} width={`${Math.abs(item.v)/0.4*100}%`} height="9px" radius="full"/>
</box>
</box>
{/each}
<caption>Illustrative values only. Real SHAP values will come from the trained model.</caption>
</box>

### D. Responsible AI

This should not be a documentation-only feature. We should make it visible in the actual application.

| Principle | Practical implementation |
| --- | --- |
| Fairness | False-negative and false-positive rates across groups |
| Bias | Compare models trained with and without sensitive/background features |
| Transparency | Explain prediction factors and limitations |
| Privacy | Role-based access and minimum necessary data |
| Security | Password hashing, authentication and API protection |
| Human oversight | Mentor approval before intervention |
| Governance | Audit trail and model version tracking |
| Ethical AI | No automatic penalties or student discrimination |

An important distinction: region and deprivation band can be used for fairness auditing, but we should carefully consider whether these attributes should be available to the prediction model at all. We will document that decision.

---

# 2. The complete syllabus-to-project coverage matrix

This is what I would use when presenting the project to your CSE276 faculty.

| Unit | Main project implementation | Visible proof |
| --- | --- | --- |
| I | Problem formulation, AI lifecycle | Architecture and problem definition |
| II | Search, heuristics, knowledge representation, Bayes | Search visualiser, rule engine |
| III | PEAS, rational agents, coordination | Agent pipeline and logs |
| IV | Supervised and unsupervised ML | Model comparison and clusters |
| V | LLM, RAG, prompt engineering | Mentor briefing generator |
| V | XAI and Responsible AI | SHAP, counterfactual, fairness and audit |

**My proposed coverage target:**

<box border radius="lg" padding={3} gap={3}>
<title size="xl">5 / 5</title>
**Course units represented**
<row align=center justify=between>
<text color="secondary" size="xs">Unit I</text>
<badge color="success">Core</badge>
</row>
<box background="surface-tertiary" height="7px" radius="full"><box background="#16A34A" width="100%" height="7px" radius="full"/></box>
<row align=center justify=between>
<text color="secondary" size="xs">Unit II</text>
<badge color="success">Core</badge>
</row>
<box background="surface-tertiary" height="7px" radius="full"><box background="#16A34A" width="100%" height="7px" radius="full"/></box>
<row align=center justify=between>
<text color="secondary" size="xs">Unit III</text>
<badge color="success">Core</badge>
</row>
<box background="surface-tertiary" height="7px" radius="full"><box background="#16A34A" width="100%" height="7px" radius="full"/></box>
<row align=center justify=between>
<text color="secondary" size="xs">Unit IV</text>
<badge color="success">Core + selective</badge>
</row>
<box background="surface-tertiary" height="7px" radius="full"><box background="#16A34A" width="100%" height="7px" radius="full"/></box>
<row align=center justify=between>
<text color="secondary" size="xs">Unit V</text>
<badge color="success">Core</badge>
</row>
<box background="surface-tertiary" height="7px" radius="full"><box background="#16A34A" width="100%" height="7px" radius="full"/></box>
<caption>Coverage means that the concepts are represented in the design or implementation, not that every syllabus topic requires a separate production feature.</caption>
</box>

# 3. What I would actually build — final feature scope

I don't want this to become a collection of disconnected demonstrations. We should have one central product with supporting AI laboratories.

I propose five major modules:

<box gap={3}>
<row align=start gap={3}>
<AsyncImage query="dark modern education analytics dashboard student performance interface" aspectRatio="1:1" maxWidth="88px"/>
<box flex="1" gap={1}>
**01. Academic Intelligence**

Student profiles, academic records, weekly monitoring, predictions and performance trends.
<badge color="success">Essential</badge>
</box>
</row>
<divider color="subtle"/>
<row align=start gap={3}>
<AsyncImage query="machine learning explainable AI SHAP visualization analytics interface" aspectRatio="1:1" maxWidth="88px"/>
<box flex="1" gap={1}>
**02. Explainable AI Laboratory**

Model comparison, SHAP, counterfactuals, Bayesian reasoning, fairness and calibration.
<badge color="success">Essential</badge>
</box>
</row>
<divider color="subtle"/>
<row align=start gap={3}>
<AsyncImage query="AI agent workflow graph node visualizer dark interface" aspectRatio="1:1" maxWidth="88px"/>
<box flex="1" gap={1}>
**03. Intelligent Agent Command Center**

Four-agent pipeline, PEAS, decision logs, search algorithms and intervention planning.
<badge color="success">Essential</badge>
</box>
</row>
<divider color="subtle"/>
<row align=start gap={3}>
<AsyncImage query="RAG knowledge base document retrieval AI assistant dashboard dark UI" aspectRatio="1:1" maxWidth="88px"/>
<box flex="1" gap={1}>
**04. Knowledge and Generative AI**

Knowledge graphs, intervention playbook, RAG and mentor briefing generator.
<badge color="success">Essential</badge>
</box>
</row>
<divider color="subtle"/>
<row align=start gap={3}>
<AsyncImage query="enterprise responsible AI fairness audit model governance dashboard dark interface" aspectRatio="1:1" maxWidth="88px"/>
<box flex="1" gap={1}>
**05. Governance and Evaluation**

Fairness audit, model health, access control, audit trail and research documentation.
<badge color="success">Essential</badge>
</box>
</row>
</box>

# 4. What we should NOT build

Even though these topics are in your syllabus, I would not force all of them into the main product.

- Train a deep neural network just to demonstrate deep learning.
- Implement reinforcement learning without actual intervention outcome data.
- Build a complex autonomous multi-agent framework.
- Add computer vision or speech recognition.
- Build a multimodal chatbot without a genuine use case.
- Use expensive cloud infrastructure.
- Make the project dependent on Gemini API availability.

We can explain these concepts in the technical documentation and viva, and implement small isolated demonstrations only if faculty specifically requires them.

# 5. One thing I want to establish before coding

Let's make the project follow this principle:

**Every important AI concept should have three things:**

1. A working implementation.
2. A visual demonstration.
3. A technical explanation that you can defend in your viva.

For example, if your teacher asks, "Why did you use A* instead of BFS?", you should be able to open the search laboratory, demonstrate both algorithms on the same intervention graph, and explain the difference in cost and heuristic guidance.

That's the standard I want.

---

# 6. Let's lock our project direction

{@body const [scope,setScope]=DIL.useState("comprehensive")}
{@body const [priority,setPriority]=DIL.useState("balanced")}
{@body const [mode,setMode]=DIL.useState("local")}
<box border radius="lg" padding={3} gap={3}>
**Project development configuration**

**1. How much of the syllabus should we implement?**
<radio-group direction="col" value={scope} onChange={setScope}>
<radio value="comprehensive">Comprehensive — all five units represented, practical and theoretical coverage</radio>
<radio value="focused">Focused — only concepts directly useful for early-warning</radio>
<radio value="balanced">Balanced — strong core implementation, remaining concepts in an AI laboratory</radio>
</radio-group>
<divider color="subtle"/>
**2. What should be our main priority?**
<radio-group direction="col" value={priority} onChange={setPriority}>
<radio value="balanced">Balanced research + impressive working product</radio>
<radio value="research">ML accuracy, explainability and research quality</radio>
<radio value="product">Premium interface and university demonstration</radio>
</radio-group>
<divider color="subtle"/>
**3. Where should the application run?**
<radio-group direction="col" value={mode} onChange={setMode}>
<radio value="local">Local-first Windows application (recommended)</radio>
<radio value="web">Locally hosted web application</radio>
<radio value="cloud">Cloud-deployed web application</radio>
</radio-group>
<button block onClick={()=>GenUI.issueNewTurn("Lock the LPU-RISK-01 development configuration: syllabus coverage: "+scope+"; priority: "+priority+"; deployment: "+mode+". Now prepare the final technical architecture, repository structure, development milestones and first Antigravity master prompt.")}>Lock project direction <icon name="arrow-right" size="sm"/></button>
</box>

My recommendation is **Comprehensive + Balanced + Local-first**.

We have an opportunity to make this a genuinely strong CSE276 project, where the interface is impressive, but the actual intelligence behind it is what earns respect.

## You

lets make the prompt for stitch whats in each student , teacher and admins should which types of graph how it should looks making it looks natural rather than an ai created project

## ChatGPT

*Worked for 12s*

Absolutely. This is where we need to be very deliberate. I don't want LPU-RISK-01 to look like another generic AI-generated dashboard with glowing blue cards, random graphs, gradients and unnecessary animations.

I want it to look like a **real university academic intelligence platform**, something a university might actually use to monitor students, support mentors and make administrative decisions.

Think of the design quality of a professional SaaS product: clean typography, meaningful data visualisation, subtle colours, carefully organised information and realistic academic records.

We will design three separate experiences:

1. Student — supportive, simple and progress-oriented.
2. Teacher/Mentor — analytical, detailed and decision-oriented.
3. Admin — institutional, strategic and governance-oriented.

**Important:** We will give Stitch one prompt at a time. This produces more consistent and controllable screens than asking it to generate the entire application in one prompt.

# 1. Design direction

<box gap={2}>
<title size="lg">LPU-RISK-01 — Visual identity</title>
<text color="secondary" size="sm">A modern academic intelligence and student success platform.</text>
<grid columns={2} gap={2}>
<grid-item>
<box background="#F5F7FA" radius="lg" padding={3} theme="light" gap={2}>
<box background="#FFFFFF" radius="md" padding={2}>
<row align=center justify=between>
<box background="#173B68" radius="sm" size="25px" align=center justify=center>
<icon name="graduation-cap" color="#FFFFFF" size="sm"/>
</box>
<text color="#64748B" size="xs">LIGHT THEME</text>
</row>
<title color="#172B45" size="xl">Academic</title>
<title color="#172B45" size="xl">Intelligence</title>
<box background="#E6EEF8" radius="sm" height="7px"/>
<box background="#DDEBE3" radius="sm" height="7px" width="70%"/>
</box>
<text color="#172B45" weight="semibold" size="sm">Light / primary</text>
<text color="#64748B" size="xs">Professional, calm, readable.</text>
</box>
</grid-item>
<grid-item>
<box background="#151D2B" radius="lg" padding={3} theme="dark" gap={2}>
<box background="#202B3C" radius="md" padding={2}>
<row align=center justify=between>
<box background="#477BB5" radius="sm" size="25px" align=center justify=center>
<icon name="graduation-cap" color="#FFFFFF" size="sm"/>
</box>
<text color="#A9B8CA" size="xs">DARK THEME</text>
</row>
<title color="#FFFFFF" size="xl">Academic</title>
<title color="#FFFFFF" size="xl">Intelligence</title>
<box background="#354B68" radius="sm" height="7px"/>
<box background="#355B4A" radius="sm" height="7px" width="70%"/>
</box>
<text color="#FFFFFF" weight="semibold" size="sm">Dark / secondary</text>
<text color="#A9B8CA" size="xs">Optional, restrained contrast.</text>
</box>
</grid-item>
</grid>
**Recommended palette**
<row align=center gap={2}>
{#each ["#173B68","#477BB5","#E8EEF5","#F5F7FA","#23845D","#D49B3D","#C65C5C"] as c}
<box background={c} height="32px" flex="1" radius="md"/>
{/each}
</row>
<caption>Deep navy, muted blue, soft grey, white, restrained green, amber and red.</caption>
</box>

My design rules:

- Default to light mode.
- White and very light grey backgrounds.
- Deep navy navigation.
- Use green, amber and red only for meaningful statuses.
- Use realistic spacing and consistent alignment.
- No unnecessary glassmorphism, neon, glowing borders or AI-themed decorations.
- Charts must have proper axis labels, legends and meaningful units.
- Use believable sample data, explicitly marked as demonstration data.
- Desktop-first, but responsive for smaller screens.
- Avoid excessive rounded cards; use subtle borders and restrained shadows.

# 2. Stitch Prompt 01 — Student Dashboard

<badge color="success">Prompt 1 · Student experience</badge>

<AsyncImageGroup query={["modern university student portal dashboard academic performance light theme UI","student academic progress dashboard weekly grades attendance chart clean SaaS design"]} aspectRatio="5:4" layout="carousel"/>

The student interface should feel welcoming, not like a surveillance or punishment system.

The student should understand three things immediately:

- How am I performing?
- What should I improve?
- What should I do today?

<WritingBlock id="62101" variant="document"># STITCH DESIGN PROMPT — LPU-RISK-01 STUDENT DASHBOARD

Design a production-quality Student Academic Dashboard for LPU-RISK-01, an Explainable Academic Early-Warning and Intervention Decision System for a university.

## 1. Product context

This is an actual academic support platform, not a generic AI dashboard.

The platform monitors:

- Subject-wise academic performance
- Attendance
- Internal assessment marks
- Assignment completion
- Learning activity
- Weekly improvement trends

It helps students understand their academic progress and receive personalised academic support.

The interface must feel like a professionally designed university SaaS product.

## 2. Overall visual direction

Use a clean, premium, light-themed interface.

Design references:

- Modern university student portals
- Professional education SaaS platforms
- Linear's information hierarchy
- Notion's simplicity
- Stripe's clean data presentation

Visual rules:

- Main background: #F5F7FA
- Cards: #FFFFFF
- Primary navy: #173B68
- Secondary blue: #477BB5
- Success green: #23845D
- Warning amber: #D49B3D
- Text: #263548
- Secondary text: #778397
- Thin neutral borders.
- Subtle shadows only.
- Consistent 8px spacing system.
- Use Inter or a similar modern sans-serif font.

Avoid:

- Neon colours
- Glowing elements
- Excessive gradients
- Glassmorphism
- Random decorative AI icons
- Oversized statistics
- Unnecessary animations

## 3. Main layout

Create a desktop dashboard at 1440px width.

LEFT SIDEBAR:

- LPU-RISK-01 logo and product name.
- Overview
- My Academic Performance
- Subject Progress
- My Tasks
- Academic History
- Profile
- Help & Support

Use simple Lucide-style icons.

At the bottom show:

- Student profile avatar
- Student name
- Registration number
- Logout

TOP NAVIGATION:

- Breadcrumb: Student / Overview
- Academic session selector
- Semester selector
- Notification icon
- Student profile menu

## 4. Main dashboard content

HEADER:

"Good morning, Aarav"

Subtitle:
"Here is your academic progress and what you can improve this week."

Show a small academic period label.

### SECTION A — Academic status overview

Create four compact statistic cards:

1. Academic Status
  - Status: WATCH
  - Supporting text: "Some subjects need attention."
  - Use amber, not alarming red.
2. Current Semester Average
  - Example: 7.4 / 10
  - Show previous semester comparison.
3. Attendance
  - Example: 82%
  - Show attendance target of 85%.
4. Assignment Completion
  - Example: 76%
  - Show completed versus pending assignments.

All numbers are demonstration data.

### SECTION B — Academic performance trend

Create a LARGE line chart titled:

"Your Academic Progress"

Use a dual-series line chart:

- Weekly assessment performance (%)
- Attendance (%)

X-axis: Week 1 to Week 8.
Y-axis: Percentage, 0–100.

Use:

- Blue for assessment performance.
- Green for attendance.
- Subtle gridlines.
- Visible but small data point markers.
- Hover tooltip showing the exact weekly values.

The chart must look like a real academic analytics chart, not a decorative illustration.

### SECTION C — Subject-wise performance

Create a horizontal grouped bar chart titled:

"Subject Performance"

Subjects:

- Mathematics
- Programming
- Database Management
- Artificial Intelligence
- Computer Networks

For each subject show:

- Internal marks (%)
- Attendance (%)

Use two distinguishable muted colours.

Show a small legend and readable subject labels.

Do NOT use a radar chart here. A grouped bar chart is easier for students to interpret and compare.

### SECTION D — Today's learning tasks

Create a practical task list.

Example:

- Complete Mathematics Unit 3 practice.
- Submit DBMS assignment.
- Review Programming pointers.
- Attend mentor discussion.

Each task should contain:

- Subject
- Task title
- Due date
- Priority
- Mark as completed button.

Use simple checkboxes and subtle status indicators.

### SECTION E — Understand your academic status

Create a small explanation panel.

Title: "Why is your status Watch?"

Show three understandable factors:

- Mathematics assessment performance has declined.
- Assignment completion needs improvement.
- Attendance is close to the expected target.

Include a supportive improvement suggestion.

Do not display raw ML probability, SHAP technical terminology or peer comparisons to students.

### SECTION F — Improvement recommendations

Create a small panel:
"Your next steps"

Show three recommendations:

- Practice mathematics for 30 minutes daily.
- Complete pending assignments.
- Discuss difficult topics with your mentor.

Include an improvement trend indicator.

## 5. Design behaviour

- Sidebar navigation should have a clear active state.
- Semester selector should be visible.
- Task completion should have a visual state.
- Charts should have tooltips.
- Status should be supportive and non-stigmatising.
- All data must look realistic and consistent.

## 6. Final quality requirements

The dashboard must look like a real university product designed by an experienced product design team.

Do not make it look like an AI-generated template.

Prioritise usability, readable information, balanced whitespace, clear hierarchy and natural data visualisation.

Generate the complete Student Dashboard screen with realistic demonstration data.</WritingBlock>

# 3. Stitch Prompt 02 — Teacher / Mentor Dashboard

<badge color="success">Prompt 2 · Our hero dashboard</badge>

<AsyncImageGroup query={["professional academic advisor student analytics dashboard light theme","student risk analytics scatter plot mentor dashboard SaaS","SHAP waterfall explainable AI analytics dashboard clean interface"]} aspectRatio="5:4" layout="carousel"/>

This is the most important screen in our project.

The mentor should be able to answer:

- Which students need attention?
- Why are they struggling?
- Is it an attendance problem or an effort-outcome gap?
- What does the AI recommend?
- Should I approve the recommendation?

I want the mentor dashboard to feel like a serious academic decision-support system.

<WritingBlock id="62102" variant="document"># STITCH DESIGN PROMPT — LPU-RISK-01 MENTOR DASHBOARD

Design a premium, enterprise-grade Mentor Dashboard for LPU-RISK-01, an Explainable Academic Early-Warning and Intervention Decision System.

This is the primary analytical workspace of the application.

The mentor is responsible for monitoring approximately 10 assigned students, understanding academic difficulties, reviewing AI explanations and approving or modifying interventions.

The design must look like a real university academic management and decision-support platform.

## 1. Design language

Use the same design system as the Student Dashboard.

- Light theme.
- Background #F5F7FA.
- White cards.
- Deep navy #173B68.
- Blue #477BB5.
- Green #23845D.
- Amber #D49B3D.
- Red #C65C5C.
- Inter typography.
- Thin borders.
- Subtle shadows.
- Clean professional spacing.

No neon, excessive gradients, glass effects or decorative AI artwork.

## 2. Main layout

Desktop resolution: 1440px.

LEFT SIDEBAR:

- LPU-RISK-01 logo
- Overview
- My Mentees
- Academic Monitoring
- Risk Analysis
- Intervention Planner
- Student Briefings
- Decision History
- Profile

Bottom:

- Mentor profile
- Faculty/department
- Logout

TOP BAR:

- Breadcrumb: Mentor / Overview
- Academic semester selector
- Section filter
- Search students
- Notification icon
- Mentor profile

## 3. Dashboard header

Title: "Mentor Overview"

Subtitle:
"Monitor your assigned students, identify academic concerns and coordinate timely support."

Show:

- Academic session
- Section
- Last updated timestamp

## 4. SECTION A — Mentor overview statistics

Four compact cards:

1. Assigned Mentees: 10
2. Students On Track: 6
3. Students on Watch: 3
4. Students Requiring Review: 1

These are illustrative numbers.

Each card should have a small supporting label and restrained status colour.

Avoid oversized numbers and excessive visual decoration.

## 5. SECTION B — Mentee monitoring table

This is one of the most important components.

Title: "My Assigned Students"

Create a professional data table with:

- Student name
- Registration ID
- Current CGPA
- Attendance
- Latest internal score
- Academic status
- Weekly trend sparkline
- Last mentor interaction
- View details action

Use 10 believable demonstration student records.

Status labels:

- On Track
- Watch
- Needs Review

Sort by support priority, not by a competitive student ranking.

Include:

- Search
- Subject filter
- Status filter
- Pagination
- Clear table headers

Keep the table compact but readable.

## 6. SECTION C — Academic effort vs outcome analysis

Create a scatter plot titled:

"Attendance vs Academic Performance"

X-axis: Attendance (%)
Y-axis: Assessment performance (%)

Include four conceptual quadrants:

1. High attendance + high performance:
Consistent progress.
2. Low attendance + low performance:
Engagement concern.
3. High attendance + low performance:
Effort-outcome gap.
4. Low attendance + high performance:
Attendance monitoring.

Show student points with small labels on hover.

Use:

- Muted blue points for general students.
- Amber for students needing review.
- Subtle quadrant backgrounds.
- Clearly labelled axes.
- A small legend.

This chart must help mentors understand the difference between attendance problems and learning difficulties.

Do not make the plot overly colourful.

## 7. SECTION D — Academic trend monitoring

Create a weekly line chart:

"Weekly Mentee Performance"

Show:

- Average assessment performance.
- Average attendance.

X-axis: Week 1–8.
Y-axis: Percentage.

Include a selector:

- All mentees
- Selected student

Show a compact tooltip.

## 8. SECTION E — Student detail and explainability

Design a large student detail drawer or dedicated student-detail screen.

The mentor selects a student from the table.

Header:

- Student name
- Registration number
- CGPA
- Current academic status
- Last updated

Inside the detail view:

A. Subject performance

Use a horizontal grouped bar chart comparing:

- Attendance
- Internal marks
- Assignment completion

Across the five subjects.

B. Individual SHAP waterfall

Title: "Why did the model predict this risk?"

Show a genuine-looking waterfall chart layout.

Display:

- Baseline model output.
- Positive feature contributions.
- Negative feature contributions.
- Final model output.

Example feature labels:

- Internal assessment score
- Assignment completion
- VLE activity
- Attendance trend
- Previous academic performance

Use red/amber for factors increasing risk and green/blue for factors reducing risk.

Clearly label the chart as model explanation, not causal proof.

C. Production rule trace

Show:

- R1: Attendance threshold checked.
- R2: Assessment decline detected.
- R3: Effort-outcome gap checked.

For each rule show:

- Condition
- Result: Triggered / Not triggered
- Reason

D. Counterfactual explanation

Create a compact card:

"What could change this prediction?"

Example:
"If assignment completion improves while other features remain unchanged, the model's predicted risk may decrease."

Display the current and alternative model prediction where actual counterfactual calculations are available.

E. Bayesian reasoning

Show:

- Prior risk probability.
- Evidence likelihood.
- Updated posterior probability.

Use a small horizontal probability comparison visualisation.

## 9. SECTION F — AI-generated mentor briefing

Create a professional document-style briefing card.

Title: "Student Support Briefing"

Include:

- Academic observations.
- Main contributing factors.
- Rule engine findings.
- Recommended next steps.
- Relevant intervention playbook reference.

Actions:

- Generate briefing
- Copy briefing
- View source evidence

Briefing must look like a professional academic report, not a chatbot conversation.

## 10. SECTION G — Intervention approval

Create a human-oversight panel.

Display a recommended intervention:

Example:
"Mathematics Unit 3 targeted practice"

Show:

- Why it was suggested.
- Expected student effort.
- Suggested completion date.
- Supporting evidence.

Buttons:

- Approve
- Edit
- Reject

Show a small decision history beneath the recommendation.

Never show that an intervention was automatically executed.

## 11. SECTION H — Mentor workload

Show:

- Number of mentees.
- Number of pending reviews.
- Number of approved interventions.
- Number of completed mentor interactions.

Use a simple horizontal bar or compact progress indicator.

Do not rank teachers against each other.

## 12. Interaction and presentation

- Selecting a student opens the detail view.
- Table filters are usable.
- Charts have informative tooltips.
- Approval actions have clear visual states.
- Maintain consistent spacing and typography.
- Keep the main screen information-dense but organised.

## Final design requirement

This should look like an actual professional academic advisor platform used by university faculty.

The mentor should feel that this system helps them make better decisions, rather than replacing their judgement.

Prioritise meaningful data, practical workflows and exceptional information hierarchy.</WritingBlock>

# 4. Stitch Prompt 03 — Admin Dashboard

<badge color="success">Prompt 3 · Institutional intelligence</badge>

<AsyncImageGroup query={["enterprise education institutional analytics dashboard light theme","university administrator analytics dashboard heatmap student performance","responsible AI model fairness monitoring dashboard professional UI"]} aspectRatio="5:4" layout="carousel"/>

The admin dashboard should feel different from the other two.

The administrator is not interested in individual practice tasks. They want to understand the overall health of the academic institution, model performance, fairness, mentor workload and intervention activity.

<WritingBlock id="62103" variant="document"># STITCH DESIGN PROMPT — LPU-RISK-01 ADMIN DASHBOARD

Design a professional Institutional Administration Dashboard for LPU-RISK-01, an Explainable Academic Early-Warning and Intervention Decision System.

This dashboard is intended for university administrators, academic coordinators and system administrators.

Its purpose is to monitor academic trends, student support requirements, mentor workload, ML model performance, fairness and governance.

This is an institutional analytics product, not a generic business sales dashboard.

## 1. Visual identity

Use the shared LPU-RISK-01 design system.

- Light background #F5F7FA.
- White content cards.
- Navy #173B68.
- Blue #477BB5.
- Green #23845D.
- Amber #D49B3D.
- Red #C65C5C.
- Inter typography.
- Fine neutral borders.
- Consistent spacing.
- Professional and restrained visualisations.

Avoid:

- Neon dashboards.
- Excessive gradients.
- Glowing effects.
- Unnecessary animated elements.
- Oversized decorative icons.

## 2. Layout

Desktop: 1440px.

LEFT SIDEBAR:

- LPU-RISK-01
- Institutional Overview
- Student Analytics
- Academic Performance
- Mentor Management
- Intervention Monitoring
- AI Model Health
- Fairness & Responsible AI
- Audit Logs
- System Configuration

TOP BAR:

- Breadcrumb: Administration / Overview
- Academic session
- Semester
- Department selector
- Section selector
- Notification
- Administrator profile

## 3. Dashboard header

Title: "Institutional Overview"

Subtitle:
"Academic intelligence, student support and system governance at a glance."

Show current academic period and last data refresh.

## 4. SECTION A — Institutional summary

Create five compact KPI cards:

1. Total monitored students.
2. Students On Track.
3. Students on Watch.
4. Students Requiring Review.
5. Pending Mentor Decisions.

Each card should show:

- Main value.
- Supporting description.
- Change versus previous period, if available.

Use realistic demonstration values and avoid implying actual LPU institutional data.

## 5. SECTION B — Student academic distribution

Create a stacked bar chart titled:

"Academic Status Distribution"

Group by academic section or department.

Show:

- On Track
- Watch
- Needs Review

Use restrained green, amber and red.

Include a filter for:

- Department
- Semester
- Academic session

The chart should make institutional differences easy to compare.

## 6. SECTION C — Section and subject heatmap

Create a professional heatmap:

"Academic Risk by Section and Subject"

Rows:

- Academic sections.

Columns:

- Mathematics
- Programming
- DBMS
- Artificial Intelligence
- Computer Networks

Each cell represents the average model-predicted risk probability or a clearly defined academic performance indicator.

Use a sequential, colour-blind-conscious colour scale.

Include:

- Legend.
- Hover values.
- Subject filters.
- Section labels.

Do not use ambiguous colours without explaining what they represent.

## 7. SECTION D — Weekly institutional trend

Create a multi-series line chart:

"Academic Monitoring Trend"

Show:

- Weekly average assessment score.
- Average attendance.
- Number of students requiring review.

Use separate scales or clearly distinguish the count series.

X-axis: Week 1–8.

Include an informative tooltip.

## 8. SECTION E — Mentor workload and mentee trends

Title: "Mentor Support Overview"

Use a horizontal bar chart showing:

- Mentor name.
- Assigned mentees.
- Pending reviews.
- Approved interventions.

Beside it show a small trend visualisation of mentee academic improvement.

Do not create a simplistic teacher leaderboard or performance ranking.

Explicitly communicate that mentor workload and student improvement depend on cohort composition and sample size.

## 9. SECTION F — AI model health

This section is essential.

Create a structured model-monitoring area.

Four metric cards:

- Recall
- Precision
- PR-AUC
- F2 Score

Then include:

A. Model comparison chart

Compare:

- Logistic Regression
- Decision Tree
- Random Forest
- HistGradientBoosting

Use a grouped bar chart comparing recall, precision and F2, with metric selection where necessary.

B. Confusion matrix

Display a 2×2 confusion matrix:

- True Positive
- False Positive
- True Negative
- False Negative

Use clearly labelled axes.

C. Calibration chart

Plot predicted probability versus observed frequency.

Include a diagonal reference line.

D. Model information

Show:

- Active model name.
- Training date.
- Model version.
- Dataset version.
- Selected decision threshold.
- Last evaluation date.

All values should be labelled as demonstration values until connected to actual evaluation results.

## 10. SECTION G — Fairness and Responsible AI

Create a dedicated fairness monitoring panel.

Title:
"Fairness & Responsible AI"

Include:

A. False-negative rate by entry-background group.

Use grouped bars to compare groups.

B. False-positive rate by entry-background group.

Use a separate grouped bar chart.

C. Fairness gap indicator.

Show the difference between the relevant group rates, clearly stating the metric definition.

D. Feature importance comparison.

Show top SHAP features across different entry-background groups.

Use a grouped horizontal bar chart.

E. Governance status.

Display:

- Human approval compliance.
- Audit log availability.
- Model version tracking.
- Data access control status.

Never imply that fairness is guaranteed just because a chart exists.

## 11. SECTION H — Intervention monitoring

Create a stacked bar chart:

"Intervention Status"

Categories:

- Suggested
- Approved
- Rejected
- Completed

Add a small table:

- Intervention type.
- Number of students.
- Approval count.
- Completion count.

Do not claim that interventions improve academic marks unless actual outcome evaluation supports it.

## 12. SECTION I — System governance and configuration

Create a compact configuration section.

Include:

- Risk thresholds.
- Mentor allocation cap.
- Academic benchmark configuration.
- Model version.
- Data refresh status.
- User access management.

Show an audit-log preview with:

- Timestamp.
- User.
- Action.
- Affected record.
- Approval status.

## 13. Design and interaction

- Use a logical dashboard grid.
- Give the model health and fairness sections enough visual importance.
- Keep cards compact and readable.
- Use meaningful chart legends and axes.
- Provide clear filtering.
- Make the sidebar consistent with the other dashboards.
- Avoid excessive cards and charts competing for attention.

## Final quality requirement

The interface must look like an enterprise-grade institutional academic analytics platform.

It should feel designed for actual university administration and governance.

The design must communicate trust, transparency, academic responsibility and informed decision-making.

Do not make it look like a generic AI-generated dashboard template.</WritingBlock>

# 5. Graph selection — final design decisions

This is important because choosing the right graph matters more than making every chart look fancy.

Here is the graph specification I want Stitch to follow.

| Dashboard | Graph | Why we're using it |
| --- | --- | --- |
| Student | Dual-line chart | Weekly academic progress |
| Student | Grouped horizontal bars | Subject comparison |
| Mentor | Scatter plot | Attendance vs marks |
| Mentor | Sparkline | Individual student trends |
| Mentor | SHAP waterfall | Individual prediction explanation |
| Mentor | Horizontal bars | Subject-wise performance |
| Admin | Stacked bar | Academic status distribution |
| Admin | Heatmap | Section vs subject |
| Admin | Line chart | Institutional trends |
| Admin | Horizontal bars | Mentor workload |
| Admin | Confusion matrix | Model evaluation |
| Admin | Calibration curve | Probability reliability |
| Admin | Grouped bars | Fairness comparison |
| Admin | Feature importance | Model interpretation |

**One deliberate choice:** no unnecessary radar charts everywhere. Radar charts often look attractive but become difficult to interpret with many subjects and overlapping measures. We should use them only where they genuinely help.

# 6. How to use Stitch properly

Follow this exact order:

<list marker="number" gap={2}>
<list-item>Open <Link url="https://stitch.withgoogle.com/" title="Google Stitch"/>.</list-item>
<list-item>Start a new project called `LPU-RISK-01`.</list-item>
<list-item>Paste the Student Dashboard prompt first.</list-item>
<list-item>Review the generated screen and correct spacing, typography and graph choices.</list-item>
<list-item>Generate the Mentor Dashboard using its separate prompt. Refer to the same design system.</list-item>
<list-item>Generate the Admin Dashboard using its separate prompt.</list-item>
<list-item>Keep all three in the same project and maintain consistent sidebar, header, cards, colours and typography.</list-item>
</list>

## 7. My final design advice

Don't accept Stitch's first output blindly.

After each screen is generated, evaluate it on these five things:

- Does it look like a real university product?
- Can someone understand the information in five seconds?
- Are the charts appropriate for the data?
- Does every component have a practical purpose?
- Are all three dashboards visually consistent?

And one important thing for our later Antigravity development: Stitch's output is the visual reference, not the application's backend. We will connect the graphs to actual FastAPI endpoints and database records. The demonstration values must never be mistaken for trained model results.

**Start with the Mentor Dashboard if you want to judge the overall visual direction.** It's our most technically interesting screen, and getting its design language right will make the Student and Admin dashboards much easier to keep consistent.

## You

now give me the antigravity prompt for connecting all and make the perfect backend plus i have created and add in the folder an dummy data for 50 lpu students use that

## ChatGPT

*Worked for a couple of seconds*

Now we move from design to the actual engineering. The goal is to make LPU-RISK-01 a **fully connected, database-backed application**, not just three attractive dashboards displaying static numbers.

I want Antigravity to work like a senior full-stack engineer: inspect your existing project, understand the Stitch-generated frontend, inspect the 50-student dummy dataset, design the backend around the actual data, connect every role, and verify that everything works.

One important decision: the 50 LPU student records should be treated as **synthetic demonstration data**, not real institutional records or evidence of actual model accuracy. The system should clearly distinguish demo predictions from experimentally validated ML results.

## Master Antigravity prompt

Copy this into Antigravity with your LPU-RISK-01 project folder open.

<WritingBlock id="73182" variant="document"># MASTER ENGINEERING PROMPT — LPU-RISK-01

## Full Backend Architecture, Database Integration, Authentication, API Development & Frontend Connection

You are acting as a **Senior Software Architect, Backend Engineer, Database Engineer, ML Engineer, and Integration Tester**.

Your task is to transform my existing LPU-RISK-01 project into a functional, integrated, database-driven academic early-warning and intervention decision system.

This is NOT a request to create another mockup or a frontend-only prototype.

I already have frontend designs created using Google Stitch for three different roles:

1. Student Dashboard
2. Mentor/Teacher Dashboard
3. Institutional Admin Dashboard

I have also added a dummy dataset containing 50 LPU student records inside the project folder.

Your responsibility is to inspect what already exists, understand the actual structure and data, and connect everything properly.

---

# 1. FIRST: INSPECT THE ENTIRE PROJECT

Before modifying anything:

- Inspect the complete project directory.
- Identify the existing frontend framework, components, routes, styles, and assets.
- Identify all existing backend code, if any.
- Locate the dummy dataset containing 50 LPU student records.
- Inspect its file format, columns, data types, missing values, duplicates, and relationships.
- Inspect existing Stitch-generated screens and understand their intended functionality.
- Read existing documentation and configuration files.
- Identify incomplete, duplicated, or disconnected components.

Do not assume the dataset is CSV or JSON. Detect its actual format.

Create a project assessment document:

`documentation/PROJECT_AUDIT.md`

It must contain:

- Existing architecture
- Existing frontend screens
- Existing dataset structure
- Existing backend components
- Missing functionality
- Integration problems
- Proposed implementation sequence

**IMPORTANT:**

Do not delete or overwrite existing work unnecessarily.

Do not replace my existing Stitch frontend with a completely different design.

Preserve the established visual identity, layout, typography, charts, and navigation wherever possible.

Do not start coding before understanding the existing project.

---

# 2. TARGET SYSTEM ARCHITECTURE

Build a clean, modular, maintainable architecture.

Preferred technology stack:

### Frontend

- React
- TypeScript
- Existing Stitch-generated components and styles
- Tailwind CSS if already used
- Recharts for charts if compatible with the existing frontend

### Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy
- SQLite initially

### Data and AI

- Pandas
- NumPy
- Scikit-learn
- SHAP
- SciPy if needed

### Testing

- Pytest
- HTTPX for API testing
- Frontend component and integration tests using the existing test framework

Do not introduce unnecessary technologies.

Do not add Docker, Kubernetes, microservices, Redis, or paid cloud infrastructure unless there is a demonstrated requirement.

The system must run locally on Windows 11.

Use a modular monolithic architecture with clear separation between:

- Frontend
- API layer
- Business logic
- Database layer
- ML engine
- Explainability
- Decision engine
- Authentication and authorization

---

# 3. DATABASE DESIGN

Create a proper relational database.

Do not store the entire application in one JSON file.

Design appropriate tables with primary keys, foreign keys, constraints, indexes, and timestamps.

At minimum, consider these entities:

### Users

- id
- full_name
- email
- password_hash
- role
- is_active
- created_at
- updated_at

Roles:

- student
- mentor
- admin

### Students

- id
- user_id
- registration_number
- department
- programme
- semester
- section
- admission_year
- mentor_id
- academic_status

### Mentors

- id
- user_id
- department
- designation

### Subjects

- id
- subject_code
- subject_name
- semester
- credits

### Student Subject Performance

- id
- student_id
- subject_id
- attendance_percentage
- internal_marks
- maximum_internal_marks
- assignment_completion
- assessment_date

### Academic Records

- id
- student_id
- semester
- cgpa
- semester_average
- attendance_average
- recorded_at

### Weekly Academic Metrics

- id
- student_id
- week_number
- attendance_percentage
- assessment_score
- assignment_completion
- engagement_metric
- recorded_at

### Risk Assessments

- id
- student_id
- model_version
- prediction
- probability
- decision_threshold
- status
- assessment_week
- explanation_summary
- created_at

### Interventions

- id
- student_id
- mentor_id
- intervention_type
- recommendation
- reason
- priority
- status
- created_at
- updated_at

Intervention statuses:

- proposed
- approved
- rejected
- in_progress
- completed

### Mentor Decisions

- id
- intervention_id
- mentor_id
- decision
- comments
- decided_at

### Audit Logs

- id
- user_id
- action
- entity_type
- entity_id
- details
- timestamp

### Model Registry

- id
- model_name
- model_version
- dataset_version
- metrics
- threshold
- status
- created_at

### System Settings

- id
- setting_key
- setting_value
- updated_at

You may add additional tables where required.

Create proper SQLAlchemy models, relationships, database initialization, and migrations or a controlled schema-versioning mechanism.

Never store plaintext passwords.

Use UTC timestamps in storage and display dates appropriately in the frontend.

---

# 4. IMPORT THE 50 DUMMY LPU STUDENTS

This is one of the most important requirements.

Locate the existing 50-student dummy dataset and use the actual records.

Do not generate a new dataset if the existing one is usable.

First inspect the data and create:

`documentation/DUMMY_DATA_DICTIONARY.md`

Document:

- Every original column
- Meaning of the column
- Data type
- Missing-value count
- Validation rules
- Mapping to database fields
- Any transformations performed

Then implement a reusable import pipeline.

Suggested file:

`backend/app/services/student_import_service.py`

The import process must:

1. Read the existing dataset.
2. Validate its schema.
3. Normalize data types.
4. Detect duplicate student IDs.
5. Validate attendance ranges.
6. Validate marks against maximum marks.
7. Validate assignment completion.
8. Handle missing values explicitly.
9. Validate mentor assignments.
10. Insert records using database transactions.
11. Report successful and failed records.
12. Prevent duplicate imports.

Make the import idempotent.

Running the seed command twice must not create another 50 duplicate students.

Do not silently discard invalid records.

Create an import report containing:

- Total records detected
- Successfully imported
- Updated records
- Rejected records
- Validation errors
- Missing values handled

Create a controlled seed command, for example:

`python -m backend.app.scripts.seed_demo_data`

Adapt this command to the existing project structure.

### Demo data rules

- Preserve original synthetic student records.
- Do not invent actual LPU student information.
- Clearly label the records as synthetic demonstration data.
- Do not present them as real university records.
- Do not invent actual historical intervention outcomes.
- Do not create fabricated ML evaluation metrics.

If a field is missing, use a transparent, documented default only where appropriate.

If the dataset contains no weekly history, do not pretend that historical measurements exist. Generate a clearly labelled synthetic demo timeline only if it is necessary for the dashboard, and document that transformation.

---

# 5. AUTHENTICATION AND ROLE-BASED ACCESS CONTROL

Implement a working authentication system.

Required functionality:

- Login
- Logout
- Password hashing
- Session/token management
- Protected routes
- Role-based authorization
- Current-user profile
- Profile update
- Password reset workflow
- Account activation/deactivation

Use secure password hashing such as Argon2 or bcrypt.

Use appropriate JWT or secure session handling.

Never hardcode secrets in source code.

Read secrets from environment variables.

Create `.env.example` without exposing real secrets.

### Role permissions

STUDENT:

- View only their own academic profile.
- View their own attendance and marks.
- View their own status and explanations.
- View assigned tasks and recommendations.
- View their academic history.
- Update permitted profile information.

MENTOR:

- View only students assigned to them.
- View academic performance of assigned students.
- Review risk assessments.
- View explanations and rules fired.
- View intervention recommendations.
- Approve, edit, or reject proposed interventions.
- Record mentor decisions.
- View their own workload.

ADMIN:

- View institutional-level aggregate analytics.
- Manage users and mentor assignments.
- View student and academic records according to authorized administrative permissions.
- Monitor model performance.
- Review fairness reports.
- View intervention statistics.
- View audit logs.
- Manage system settings.

Implement authorization at the backend API level.

Hiding a button in React is NOT sufficient security.

A student must never access another student's records by changing a URL or API ID.

A mentor must never access another mentor's assigned students without explicit administrative permission.

---

# 6. BUILD THE BACKEND API

Use versioned endpoints:

`/api/v1/`

Organize endpoints into FastAPI routers.

Required API groups:

### Authentication

- POST /api/v1/auth/login
- POST /api/v1/auth/logout
- GET /api/v1/auth/me
- POST /api/v1/auth/forgot-password
- POST /api/v1/auth/reset-password

### Student

- GET /api/v1/student/dashboard
- GET /api/v1/student/profile
- PUT /api/v1/student/profile
- GET /api/v1/student/performance
- GET /api/v1/student/subjects
- GET /api/v1/student/attendance
- GET /api/v1/student/history
- GET /api/v1/student/tasks
- GET /api/v1/student/explanation

### Mentor

- GET /api/v1/mentor/dashboard
- GET /api/v1/mentor/mentees
- GET /api/v1/mentor/mentees/{student_id}
- GET /api/v1/mentor/mentees/{student_id}/performance
- GET /api/v1/mentor/mentees/{student_id}/risk
- GET /api/v1/mentor/mentees/{student_id}/explanation
- GET /api/v1/mentor/workload
- GET /api/v1/mentor/interventions

### Intervention decisions

- POST /api/v1/interventions
- GET /api/v1/interventions/{intervention_id}
- PATCH /api/v1/interventions/{intervention_id}
- POST /api/v1/interventions/{intervention_id}/approve
- POST /api/v1/interventions/{intervention_id}/reject
- POST /api/v1/interventions/{intervention_id}/complete

### Admin

- GET /api/v1/admin/dashboard
- GET /api/v1/admin/students
- GET /api/v1/admin/academic-analytics
- GET /api/v1/admin/department-analytics
- GET /api/v1/admin/subject-analytics
- GET /api/v1/admin/mentor-analytics
- GET /api/v1/admin/intervention-analytics
- GET /api/v1/admin/model-health
- GET /api/v1/admin/fairness
- GET /api/v1/admin/audit-logs
- GET /api/v1/admin/system-settings
- PUT /api/v1/admin/system-settings

### Health and system

- GET /api/v1/health
- GET /api/v1/health/database
- GET /api/v1/system/info

Add filtering, sorting, pagination, and validation where appropriate.

Do not return entire database tables unnecessarily.

Use proper HTTP status codes and consistent error responses.

Generate OpenAPI documentation through FastAPI.

---

# 7. STUDENT DASHBOARD INTEGRATION

Connect my existing Stitch Student Dashboard to real API responses.

Every displayed value must come from the database or a clearly labelled derived calculation.

Connect:

### KPI cards

- Academic status
- Semester average
- Attendance
- Assignment completion

### Charts

- Weekly assessment performance
- Attendance trend
- Subject-wise internal marks
- Subject-wise attendance

### Other components

- Subject progress
- Pending tasks
- Academic history
- Status explanation
- Recommended actions

Status labels:

- ON TRACK
- WATCH
- NEEDS REVIEW

Avoid frightening or stigmatizing labels.

The student should see supportive, understandable explanations.

For example:

"Your attendance has decreased over the last three recorded weeks. Improving attendance may help you stay consistent."

Do not display raw SHAP values or complex model terminology to students.

Never compare one student publicly with other students.

---

# 8. MENTOR DASHBOARD INTEGRATION

Connect the existing mentor dashboard.

The mentor dashboard should show actual assigned mentees from the database.

### KPI cards

- Total assigned mentees
- On Track
- Watch
- Needs Review

### Mentee table

- Student name
- Registration number
- CGPA
- Attendance
- Internal score
- Academic status
- Last contact
- View details

### Charts

1. Attendance vs assessment scatter plot.
2. Weekly attendance and marks trends.
3. Subject-wise academic performance.

### Individual student detail

Create a complete detail page or panel with:

- Academic overview
- Subject-wise performance
- Attendance history
- Assessment history
- Risk assessment
- Model explanation
- Rule trace
- Counterfactual explanation
- Bayesian reasoning
- Intervention recommendations
- Mentor decision history

### Human-in-the-loop intervention system

The system may recommend an intervention, but must NEVER execute an intervention automatically.

Mentor actions:

- Approve
- Edit
- Reject
- Mark in progress
- Mark completed

Every decision must be stored in the database.

Every decision must create an audit log.

The mentor must be able to understand why a recommendation was generated.

---

# 9. ADMIN DASHBOARD INTEGRATION

Connect the existing admin dashboard to institutional aggregate queries.

### KPI cards

- Total monitored students
- On Track
- Watch
- Needs Review
- Pending mentor decisions

### Academic analytics

Implement:

1. Academic status distribution.
2. Status distribution by department or section.
3. Section versus subject heatmap.
4. Weekly academic trends.
5. Attendance trends.
6. Subject performance trends.

### Mentor analytics

Show:

- Assigned mentees
- Pending reviews
- Approved interventions
- Completed interventions

Do not create simplistic teacher ranking systems.

Workload information should support resource planning, not punish mentors.

### Intervention analytics

Show:

- Proposed
- Approved
- Rejected
- In progress
- Completed

Do not claim intervention effectiveness or improvement percentages unless genuine before-and-after outcome data exists.

### System monitoring

Show:

- Database health
- Backend health
- Dataset version
- Model version
- Last model evaluation
- Current prediction threshold
- Data freshness

---

# 10. MACHINE LEARNING ENGINE

Keep ML separate from the API and frontend.

Suggested location:

`ml_engine/`

Create modular components for:

- Data preprocessing
- Feature engineering
- Model training
- Model evaluation
- Prediction
- Explainability
- Fairness evaluation
- Model registry

Potential algorithms:

1. Logistic Regression — baseline.
2. Decision Tree — interpretable comparison.
3. Random Forest — candidate primary model.
4. HistGradientBoosting — challenger.
5. K-Means — exploratory student segmentation.

Do not assume Random Forest is automatically the best model. Select the primary model based on measured evaluation results.

### Critical distinction: demo data vs research data

The 50 LPU dummy student records are for demonstration and application integration.

Do NOT use their synthetic labels to claim real-world predictive accuracy.

Do NOT claim that training on 50 synthetic records creates a validated institutional prediction model.

Keep the following clearly separated:

A. DEMO MODE

- Uses the 50 synthetic LPU records.
- Supports realistic dashboards and workflow testing.
- Can use documented, deterministic demonstration rules.
- Must label predictions as DEMONSTRATION ESTIMATES.
- Must not display fabricated research metrics.

B. RESEARCH MODE

- Uses the separately prepared research dataset, such as OULAD, when available.
- Has a reproducible preprocessing and training pipeline.
- Has proper train, validation, and test separation.
- Uses temporal feature cutoffs to prevent future-data leakage.
- Reports actual measured metrics.

Do not mix demo records and research records without explicit provenance.

### Evaluation metrics

Calculate actual:

- Recall
- Precision
- F1
- F2
- PR-AUC
- Confusion matrix
- Calibration curve

Focus on recall and PR-AUC when evaluating early-warning detection, while also monitoring false positives.

Never optimize or report accuracy alone.

Store model version, dataset version, training timestamp, evaluation metrics, and decision threshold.

Never use the final test set to tune thresholds.

---

# 11. EXPLAINABLE AI

Implement SHAP explanations for supported trained models.

Required outputs:

- Global feature importance
- Individual feature contributions
- SHAP waterfall data
- Positive and negative contributions
- Baseline prediction
- Final model output

Explain clearly:

SHAP describes how model features contribute to a prediction. It does not prove that a feature caused a student's academic outcome.

### Counterfactual explanation

Generate carefully constrained explanations.

Example:

"If attendance increased from its current level to 80%, while other recorded features remained unchanged, the model output would change from X to Y."

Clearly identify this as a model scenario, not a guarantee of actual improvement.

### Rule engine

Implement transparent production rules.

Example:

R1: Attendance below a configured threshold.

R2: Assessment score declining over multiple recorded periods.

R3: Low assignment completion.

R4: Multiple academic indicators showing deterioration.

Each rule should have:

- Rule ID
- Rule description
- Conditions
- Triggered values
- Explanation
- Suggested action

Rules must be configurable and testable.

### Bayesian reasoning

Implement a transparent Bayesian calculation where valid prior probabilities and likelihoods are available.

Show:

- Prior
- Evidence
- Likelihood
- Posterior

Document assumptions.

Do not invent probabilities and present them as empirically validated.

---

# 12. DECISION SUPPORT AND AGENT COMPONENTS

Create four modular Python components:

1. Monitor
2. Risk
3. Explainer
4. Planner

These are application components, not autonomous AI agents.

### Monitor

Collect and validate academic indicators.

### Risk

Run the configured prediction or demonstration decision process.

### Explainer

Produce readable rule, model, and Bayesian explanations.

### Planner

Suggest possible mentor interventions.

All recommendations require human approval.

Do not allow the system to independently contact students, modify academic records, or execute interventions.

---

# 13. DATA VISUALIZATION RULES

Connect all charts to actual backend responses.

Use the appropriate visualization for each analytical question.

Student:

- Line chart for weekly trends.
- Grouped horizontal bars for subject comparison.
- Progress bars for assignment completion.
- Small status indicators.

Mentor:

- Scatter plot for attendance versus marks.
- Line chart for trends.
- Grouped bars for subject performance.
- SHAP waterfall for individual model explanation.

Admin:

- Stacked bars for academic status distribution.
- Heatmap for section-subject comparison.
- Line chart for institutional trends.
- Horizontal bars for mentor workload.
- Confusion matrix and calibration plot for model health.
- Grouped bars for fairness comparisons.

Every chart must include:

- Meaningful title
- Clear axis labels
- Units
- Legend where necessary
- Useful tooltip
- Empty state
- Loading state
- Error state

Do not use decorative charts with hardcoded values.

Do not use a radar chart just to make a dashboard look sophisticated.

---

# 14. FRONTEND-BACKEND INTEGRATION

Create a clean API service layer in the frontend.

For example:

`frontend/src/services/api.ts`

Add:

- Centralized API base URL
- Authentication token handling
- Request/response handling
- Error handling
- Typed API responses
- Loading state support

Create typed interfaces for:

- User
- Student
- Mentor
- Subject
- AcademicPerformance
- RiskAssessment
- Intervention
- DashboardAnalytics

Remove hardcoded dashboard data once its API connection is verified.

Do not make every component issue independent API calls if a shared service or query layer is appropriate.

Ensure role-based routing.

When a user logs in:

- Student goes to Student Dashboard.
- Mentor goes to Mentor Dashboard.
- Admin goes to Admin Dashboard.

Preserve the existing Stitch designs.

Do not redesign the application unless a specific technical issue requires it.

---

# 15. SECURITY, PRIVACY AND AUDITABILITY

Implement:

- Password hashing
- Role-based authorization
- Input validation
- SQL injection protection through ORM usage
- CORS restrictions
- Secure secret management
- Login failure handling
- Protected API endpoints
- Audit logs for important operations
- Data provenance
- Error handling without leaking sensitive information

Do not log passwords, access tokens, or sensitive personal information.

Use synthetic demo identities and clearly documented demo credentials.

Do not hardcode production credentials.

Do not expose administrative APIs to student accounts.

---

# 16. TESTING AND VERIFICATION

Do not finish after generating code.

Test the complete application.

### Backend tests

- Database initialization
- Dataset import
- Duplicate prevention
- Invalid dataset handling
- Authentication
- Password verification
- Role authorization
- Student data isolation
- Mentor assignment isolation
- Admin access
- Dashboard aggregation
- Intervention approval
- Intervention rejection
- Audit logging
- ML prediction interface
- Rule engine
- Explanation generation

### Frontend tests

- Login
- Role-based redirection
- Student dashboard loading
- Mentor dashboard loading
- Admin dashboard loading
- Charts rendering from API responses
- Empty states
- API failure states
- Intervention decision workflow

### Integration tests

Verify the entire workflow:

1. Import the 50 dummy students.
2. Initialize the database.
3. Create or seed demonstration accounts.
4. Log in as a student.
5. Confirm that the correct student's information is displayed.
6. Log in as a mentor.
7. Confirm only assigned mentees are visible.
8. Open an individual mentee.
9. Review their academic data and explanation.
10. Approve or reject an intervention.
11. Confirm the database was updated.
12. Confirm an audit log was created.
13. Log in as an admin.
14. Verify institutional aggregates reflect the database.
15. Confirm the three dashboards remain connected after restarting the application.

Run tests and fix actual errors.

Do not report a test as passed if it was not executed.

---

# 17. REQUIRED PROJECT STRUCTURE

Adapt this structure to the existing project rather than blindly recreating everything.

LPU-RISK-01/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── layouts/
│   │   ├── services/
│   │   ├── hooks/
│   │   ├── types/
│   │   ├── contexts/
│   │   └── routes/
│   └── ...
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   ├── core/
│   │   ├── database/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── agents/
│   │   └── scripts/
│   └── tests/
│
├── ml_engine/
│   ├── data/
│   ├── preprocessing/
│   ├── features/
│   ├── models/
│   ├── evaluation/
│   ├── explainability/
│   └── fairness/
│
├── research/
│   ├── dataset/
│   └── notebooks/
│
├── database/
│
├── documentation/
│
├── scripts/
│
├── .env.example
├── .gitignore
└── README.md

Keep the original dataset in its existing location unless a safe, documented reorganization is necessary.

---

# 18. RUNNING THE APPLICATION

Make the application easy to launch on Windows.

Create:

- Backend setup instructions
- Frontend setup instructions
- Database initialization instructions
- Demo data import instructions
- Demo account instructions
- Testing instructions

Provide a convenient development startup script if appropriate.

The README must include actual commands that work in PowerShell.

Document:

- Required Python version
- Required Node.js version
- Dependencies
- Database location
- API address
- Frontend address
- Demo credentials
- Dataset import command
- Test commands
- Troubleshooting

Do not assume a command works without testing it.

---

# 19. WORKING METHOD — FOLLOW THIS STRICTLY

Do not attempt a blind, massive rewrite.

Work in controlled engineering phases.

PHASE 1 — Project audit and dataset inspection.

PHASE 2 — Database schema and dummy data import.

PHASE 3 — Authentication and role-based access control.

PHASE 4 — Student APIs and dashboard integration.

PHASE 5 — Mentor APIs and intervention workflow.

PHASE 6 — Admin analytics and system monitoring.

PHASE 7 — ML engine, rule engine, explainability, and fairness.

PHASE 8 — Complete frontend integration.

PHASE 9 — Testing, debugging, security review, and documentation.

After every phase:

- Run relevant tests.
- Fix errors.
- Update documentation.
- Record what was completed.
- Identify remaining problems.

Do not silently skip unfinished requirements.

If something cannot be implemented because the dataset lacks a necessary field, explain the limitation and implement a safe alternative.

If an architectural decision is uncertain, inspect the code and choose the simplest maintainable option.

Do not fabricate functionality, metrics, records, or test results.

Do not leave TODO comments as a substitute for required implementation.

---

# 20. FINAL ACCEPTANCE CRITERIA

The project is considered complete only when:

1. Existing Stitch frontend screens are preserved and connected.
2. The 50 dummy students are imported into SQLite.
3. Duplicate imports are prevented.
4. Authentication works.
5. Student, mentor, and admin permissions are enforced by the backend.
6. Each role sees the correct dashboard.
7. Dashboard charts use database-backed data.
8. Mentors can review students.
9. Mentors can approve, edit, and reject interventions.
10. Decisions are saved and audited.
11. Admin analytics reflect actual database records.
12. Demo predictions are distinguishable from validated ML predictions.
13. Explainability and rules are implemented transparently.
14. Backend and frontend tests pass.
15. The application can be started locally using documented commands.
16. The README explains the entire system.

### FINAL INSTRUCTION

Start with PHASE 1 only.

Inspect the project, locate and analyze the existing 50-student dummy dataset, inspect the Stitch frontend, and prepare the project audit.

Do not immediately start rewriting the entire application.

After completing the audit, present me with:

- Existing project structure
- Dataset analysis
- Architecture proposal
- Database schema proposal
- Existing frontend integration plan
- Identified risks
- Phase 2 implementation plan

Then proceed phase by phase, preserving all existing work.

Build this as a credible academic decision-support system that I can demonstrate to university administrators and explain confidently during my project evaluation.</WritingBlock>

## How I recommend executing this

Don't ask Antigravity to complete all 20 sections in one uncontrolled generation. The prompt explicitly tells it to work in phases.

<box border radius="lg" gap={3} padding={3}>
**Recommended execution sequence**

<list connector="solid" marker="number" gap={3}>
<list-item>
**Phase 1 — Audit**

Let it inspect your actual 50-student dataset and Stitch frontend. Review `PROJECT_AUDIT.md` before approving implementation.
</list-item>
<list-item>
**Phase 2 — Database**

Build SQLite tables, relationships, import pipeline, and verify that all 50 records are imported correctly.
</list-item>
<list-item>
**Phase 3 — Authentication**

Test student, mentor, and admin logins and verify permissions.
</list-item>
<list-item>
**Phase 4–6 — Connect dashboards**

Connect Student → Mentor → Admin, in that order.
</list-item>
<list-item>
**Phase 7 — Intelligence layer**

Integrate ML, SHAP, rules, Bayesian reasoning, and fairness evaluation.
</list-item>
<list-item>
**Phase 8–9 — Final integration**

Test complete workflows, fix issues, and prepare the demonstration.
</list-item>
</list>
</box>

## Three things I particularly want you to verify

1. **The 50 students actually appear in SQLite.** Don't accept a dashboard that simply reads the original JSON/CSV file and pretends to be database-connected.
2. **Mentor assignments are real database relationships.** A mentor should see only their assigned students, not all 50.
3. **The charts are genuinely data-driven.** Changing a student's attendance in the database should update the appropriate student, mentor, and admin analytics.

One more important architectural decision: keep your 50-student demonstration environment separate from the OULAD research/model-evaluation environment. That distinction will make your project much more defensible during your university presentation.

**My recommendation:** Start Antigravity with this prompt and let it finish Phase 1. Once it gives you its audit, share that report here. We can critically review the architecture before it starts creating the database and backend.

