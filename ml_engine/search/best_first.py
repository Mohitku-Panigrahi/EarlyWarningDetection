import time
import heapq
from typing import Dict, Any, List
from ml_engine.search.graph import InterventionStateSpace

def best_first_search(
    graph: InterventionStateSpace,
    start_state: str = "INITIAL_REVIEW",
    goal_state: str = "PLAN_COMPLETED",
) -> Dict[str, Any]:
    """
    Greedy Best-First Search for Intervention State-Space.
    Prioritizes nodes strictly by estimated proximity to goal: f(n) = h(n).
    """
    t0 = time.perf_counter()
    counter = 0
    # Priority Queue elements: (h(n), tie_breaker_counter, current_state, path)
    h_start = graph.get_heuristic(start_state, goal_state)
    open_heap = [(h_start, counter, start_state, [start_state])]
    visited = set()
    expansion_order: List[str] = []

    while open_heap:
        h_val, _, current, path = heapq.heappop(open_heap)

        if current in visited:
            continue
        visited.add(current)
        expansion_order.append(current)

        if current == goal_state:
            total_cost = 0.0
            for i in range(len(path) - 1):
                s1, s2 = path[i], path[i + 1]
                for edge in graph.get_neighbors(s1):
                    if edge.dest_state == s2:
                        total_cost += edge.cost
                        break

            duration_ms = round((time.perf_counter() - t0) * 1000, 3)
            return {
                "algorithm": "Greedy Best-First Search",
                "start_state": start_state,
                "goal_state": goal_state,
                "path": path,
                "visited_nodes": list(visited),
                "expansion_order": expansion_order,
                "nodes_expanded": len(expansion_order),
                "path_cost": round(total_cost, 2),
                "step_count": len(path) - 1,
                "duration_ms": duration_ms,
                "completion_status": "SUCCESS",
                "explanation": (
                    "Best-First Search greedily expands the node with the lowest heuristic estimate h(n). "
                    "Focuses search direction toward target resolution, but can be misled into non-optimal paths."
                ),
            }

        for transition in graph.get_neighbors(current):
            nxt = transition.dest_state
            if nxt not in visited:
                counter += 1
                h_nxt = graph.get_heuristic(nxt, goal_state)
                heapq.heappush(open_heap, (h_nxt, counter, nxt, path + [nxt]))

    duration_ms = round((time.perf_counter() - t0) * 1000, 3)
    return {
        "algorithm": "Greedy Best-First Search",
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
        "explanation": f"Goal state '{goal_state}' unreachable from '{start_state}'.",
    }
