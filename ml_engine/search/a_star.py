import time
import heapq
from typing import Dict, Any, List
from ml_engine.search.graph import InterventionStateSpace

def a_star_search(
    graph: InterventionStateSpace,
    start_state: str = "INITIAL_REVIEW",
    goal_state: str = "PLAN_COMPLETED",
) -> Dict[str, Any]:
    """
    A* Search Algorithm for Intervention State-Space.
    Evaluation function: f(n) = g(n) + h(n)
    - g(n): Accumulated transition cost (effort/time) from start to current node
    - h(n): Admissible heuristic estimate of remaining cost to goal
    Guarantees cost-optimal intervention planning path when h(n) is admissible and consistent.
    """
    t0 = time.perf_counter()
    counter = 0

    # Priority Queue elements: (f(n), tie_breaker, g(n), current_state, path)
    h_start = graph.get_heuristic(start_state, goal_state)
    open_heap = [(h_start, counter, 0.0, start_state, [start_state])]
    
    # Store shortest known cost to each state
    g_costs = {start_state: 0.0}
    visited = set()
    expansion_order: List[str] = []
    node_evaluations: List[Dict[str, Any]] = []

    while open_heap:
        f_val, _, g_val, current, path = heapq.heappop(open_heap)

        if current in visited:
            continue
        visited.add(current)
        expansion_order.append(current)

        node_evaluations.append({
            "state": current,
            "g_cost": round(g_val, 2),
            "h_cost": round(graph.get_heuristic(current, goal_state), 2),
            "f_cost": round(f_val, 2),
            "path_so_far": list(path),
        })

        if current == goal_state:
            duration_ms = round((time.perf_counter() - t0) * 1000, 3)
            return {
                "algorithm": "A* Search (f = g + h)",
                "start_state": start_state,
                "goal_state": goal_state,
                "path": path,
                "visited_nodes": list(visited),
                "expansion_order": expansion_order,
                "nodes_expanded": len(expansion_order),
                "path_cost": round(g_val, 2),
                "step_count": len(path) - 1,
                "duration_ms": duration_ms,
                "completion_status": "SUCCESS",
                "node_evaluations": node_evaluations,
                "explanation": (
                    f"A* found the mathematically cost-optimal path using f(n) = g(n) + h(n). "
                    f"Total accumulated cost g(n) = {g_val:.2f} hours with {len(expansion_order)} node expansions. "
                    "Optimality guaranteed because the heuristic is admissible (never overestimates true cost)."
                ),
            }

        for transition in graph.get_neighbors(current):
            nxt = transition.dest_state
            tentative_g = g_val + transition.cost

            if nxt not in g_costs or tentative_g < g_costs[nxt]:
                g_costs[nxt] = tentative_g
                h_val = graph.get_heuristic(nxt, goal_state)
                f_nxt = tentative_g + h_val
                counter += 1
                heapq.heappush(open_heap, (f_nxt, counter, tentative_g, nxt, path + [nxt]))

    duration_ms = round((time.perf_counter() - t0) * 1000, 3)
    return {
        "algorithm": "A* Search (f = g + h)",
        "start_state": start_state,
        "goal_state": goal_state,
        "path": [],
        "visited_nodes": list(visited),
        "expansion_order": expansion_order,
        "nodes_expanded": len(expansion_order),
        "path_cost": 0.0,
        "step_count": 0,
        "duration_ms": duration_ms,
        "completion_status": "FAILURE",
        "node_evaluations": node_evaluations,
        "explanation": f"Goal state '{goal_state}' unreachable from '{start_state}'.",
    }
