import time
from collections import deque
from typing import Dict, Any, List, Optional
from ml_engine.search.graph import InterventionStateSpace

def breadth_first_search(
    graph: InterventionStateSpace,
    start_state: str = "INITIAL_REVIEW",
    goal_state: str = "PLAN_COMPLETED",
) -> Dict[str, Any]:
    """
    Breadth-First Search (BFS) for Intervention State-Space.
    Finds the path with the fewest state transitions.
    """
    t0 = time.perf_counter()
    queue = deque([[start_state]])
    visited = set([start_state])
    expansion_order: List[str] = []
    parent_map = {}

    if start_state == goal_state:
        duration_ms = round((time.perf_counter() - t0) * 1000, 3)
        return {
            "algorithm": "Breadth-First Search (BFS)",
            "start_state": start_state,
            "goal_state": goal_state,
            "path": [start_state],
            "visited_nodes": [start_state],
            "expansion_order": [start_state],
            "nodes_expanded": 1,
            "path_cost": 0.0,
            "step_count": 0,
            "duration_ms": duration_ms,
            "completion_status": "SUCCESS",
            "explanation": "Start state is identical to goal state.",
        }

    while queue:
        path = queue.popleft()
        current = path[-1]
        expansion_order.append(current)

        if current == goal_state:
            # Calculate cost
            total_cost = 0.0
            for i in range(len(path) - 1):
                s1, s2 = path[i], path[i + 1]
                for edge in graph.get_neighbors(s1):
                    if edge.dest_state == s2:
                        total_cost += edge.cost
                        break

            duration_ms = round((time.perf_counter() - t0) * 1000, 3)
            return {
                "algorithm": "Breadth-First Search (BFS)",
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
                    "BFS guarantees the minimum number of transitions when edge costs are uniform. "
                    f"Explored {len(expansion_order)} nodes across {len(path)-1} sequential planning stages."
                ),
            }

        for transition in graph.get_neighbors(current):
            nxt = transition.dest_state
            if nxt not in visited:
                visited.add(nxt)
                queue.append(path + [nxt])

    duration_ms = round((time.perf_counter() - t0) * 1000, 3)
    return {
        "algorithm": "Breadth-First Search (BFS)",
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
