import time
from typing import Dict, Any, List, Optional
from ml_engine.search.graph import InterventionStateSpace

def depth_first_search(
    graph: InterventionStateSpace,
    start_state: str = "INITIAL_REVIEW",
    goal_state: str = "PLAN_COMPLETED",
) -> Dict[str, Any]:
    """
    Depth-First Search (DFS) for Intervention State-Space.
    Explores an intervention trajectory deeply before considering alternatives.
    """
    t0 = time.perf_counter()
    stack = [[start_state]]
    visited = set()
    expansion_order: List[str] = []

    while stack:
        path = stack.pop()
        current = path[-1]

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
                "algorithm": "Depth-First Search (DFS)",
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
                    "DFS explores each intervention pipeline deeply before backtracking. "
                    "May discover valid paths quickly, but does not guarantee the lowest transition cost or fewest steps."
                ),
            }

        # Reverse neighbors to preserve natural left-to-right exploration on stack
        neighbors = graph.get_neighbors(current)
        for transition in reversed(neighbors):
            nxt = transition.dest_state
            if nxt not in visited:
                stack.append(path + [nxt])

    duration_ms = round((time.perf_counter() - t0) * 1000, 3)
    return {
        "algorithm": "Depth-First Search (DFS)",
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
