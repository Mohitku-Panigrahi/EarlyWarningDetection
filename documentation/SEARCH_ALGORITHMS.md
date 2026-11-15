# CSE276 Unit II: Search Algorithms in Academic Intervention Planning
**LPU-RISK-01 Decision-Support Architecture Specification**

---

## 1. Academic Foundation & Context
In classical Artificial Intelligence (Russell & Norvig, Ch. 3), search algorithms provide a systematic problem-solving methodology when an agent transitions through a discrete state-space to reach a specified target condition.

In **LPU-RISK-01**, student academic friction (identified via attendance drops or continuous evaluation deficits) triggers an intervention planning task. Rather than using unstructured actions, the system represents pedagogical support as a directed state-space graph where transitions incur effort costs ($g(n)$) and have estimated heuristic distances ($h(n)$) toward academic recovery.

---

## 2. Implemented Search Algorithms

| Algorithm | Strategy | Data Structure | Optimality Guarantee | Completeness | Time Complexity | Space Complexity |
|---|---|---|---|---|---|---|
| **BFS** | Level-by-level exploration | FIFO Queue | Optimal in **steps** (unweighted) | Complete | $O(b^d)$ | $O(b^d)$ |
| **DFS** | Deep branch exploration | LIFO Stack | Not optimal | Complete on finite graphs | $O(b^m)$ | $O(bm)$ |
| **Greedy Best-First** | Lowest $h(n)$ heuristic priority | Priority Queue (Min-Heap) | Not optimal | Incomplete (can loop without cycle checks) | $O(b^m)$ | $O(b^m)$ |
| **Hill Climbing** | Steepest local heuristic ascent/descent | In-place current state | Not optimal (Local optima traps) | Incomplete | $O(\infty)$ if plateaued | $O(1)$ |
| **A\*** | $f(n) = g(n) + h(n)$ cost + heuristic | Priority Queue (Min-Heap) | Optimal with **admissible** $h(n)$ | Complete | $O(b^d)$ | $O(b^d)$ |

---

## 3. Algorithm Formulations in LPU-RISK-01

### 3.1 Breadth-First Search (BFS)
* **Objective:** Find the intervention plan with the minimum number of organizational transitions.
* **Mechanism:** Traverses all actions at depth $d$ before exploring depth $d+1$.
* **Pedagogical Meaning:** Discovers the most direct protocol to stabilize a student with the fewest organizational handoffs.

### 3.2 Depth-First Search (DFS)
* **Objective:** Explore an aggressive intervention sequence deeply before backtracking.
* **Mechanism:** Expands the deepest active planning state until the goal or dead-end is reached.
* **Limitation:** Can lead to over-intervention if a deep branch is explored unnecessarily.

### 3.3 Greedy Best-First Search
* **Objective:** Prioritize planning states that appear closest to resolution according to $h(n)$.
* **Evaluation Function:** $f(n) = h(n)$
* **Pedagogical Meaning:** Greedily directs resources toward actions estimated to resolve friction fastest.

### 3.4 Hill Climbing (Local Search)
* **Objective:** Iteratively improve the current academic state by selecting the single neighbor with the lowest remaining friction distance $h(n)$.
* **Local Optima Demonstration:** Terminate immediately when all neighbors have equal or higher heuristic cost, illustrating why greedy human planning without global lookahead gets stuck.

### 3.5 A\* Search ($f(n) = g(n) + h(n)$)
* **Evaluation Function:**
  $$f(n) = g(n) + h(n)$$
  where:
  * $g(n)$: Accumulated transition cost (mentor and student hours invested).
  * $h(n)$: Admissible heuristic estimate of remaining effort to reach `PLAN_COMPLETED`.
* **Admissibility Property:**
  $$h(n) \le h^*(n) \quad \forall n$$
  Our pre-computed heuristic table strictly satisfies admissibility ($h \le h^*$), guaranteeing mathematical cost-optimality.

---

## 4. Empirical Test Verification
Tested in `backend/tests/test_search_engine.py`:
1. `test_graph_initialization`: 8 states, 12 transitions, admissible heuristics verified.
2. `test_bfs_execution`: Traverses minimum transitions with `completion_status == 'SUCCESS'`.
3. `test_dfs_execution`: Valid deep path explored without infinite loops.
4. `test_best_first_execution`: Prioritizes lowest $h(n)$ states.
5. `test_hill_climbing_execution`: Correctly executes local gradient descent and detects local optima.
6. `test_a_star_optimality`: Delivers minimum $g(n)$ cost path ($g \le 4.0\text{h}$).
7. `test_search_runner_comparison`: Validates simultaneous 5-algorithm benchmark matrix.
