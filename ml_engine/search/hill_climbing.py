import time
from typing import Dict, Any, List
from ml_engine.search.graph import InterventionStateSpace

def hill_climbing_search(
    graph: InterventionStateSpace,
    start_state: str = "INITIAL_REVIEW",
    goal_state: str = "PLAN_COMPLETED",
) -> Dict[str, Any]:
    """
    Hill Climbing (Greedy Local Search) for Intervention State-Space.
    Moves iteratively to the neighboring state with the strictly lowest heuristic distance h(n).
    Demonstrates local optima limitations when stuck on plateaus or local extrema.
    """
    t0 = time.perf_counter()
    current = start_state
    path = [current]
    expansion_order = [current]
    visited = set([current])
    step_evaluations: List[Dict[str, Any]] = []

    while current != goal_state:
        current_h = graph.get_heuristic(current, goal_state)
        neighbors = graph.get_neighbors(current)

        if not neighbors:
            break

        # Evaluate candidate neighbors
        best_neighbor = None
        best_h = current_h
        evaluated_candidates = []

        for edge in neighbors:
            nxt = edge.dest_state
            h_val = graph.get_heuristic(nxt, goal_state)
            evaluated_candidates.append({
                "neighbor": nxt,
                "heuristic": h_val,
                "action": edge.action,
            })
            # Strictly improve heuristic
            if h_val < best_h:
                best_h = h_val
                best_neighbor = nxt

        step_evaluations.append({
            "current_state": current,
            "current_heuristic": current_h,
            "candidates": evaluated_candidates,
            "selected_move": best_neighbor,
        })

        # Check for local optimum / plateau
        if best_neighbor is None or best_neighbor in visited:
            duration_ms = round((time.perf_counter() - t0) * 1000, 3)
            return {
                "algorithm": "Hill Climbing (Local Search)",
                "start_state": start_state,
                "goal_state": goal_state,
                "path": path,
                "visited_nodes": list(visited),
                "expansion_order": expansion_order,
                "nodes_expanded": len(expansion_order),
                "path_cost": 0.0,
                "step_count": len(path) - 1,
                "duration_ms": duration_ms,
                "completion_status": "LOCAL_OPTIMUM" if current != goal_state else "SUCCESS",
                "step_evaluations": step_evaluations,
                "explanation": (
                    f"Hill climbing stopped at state '{current}' (h={current_h:.1f}) because no neighboring state "
                    f"had a strictly lower heuristic distance. Classic demonstration of local optimum trap."
                ),
            }

        current = best_neighbor
        visited.add(current)
        path.append(current)
        expansion_order.append(current)

    # Calculate total path cost
    total_cost = 0.0
    for i in range(len(path) - 1):
        s1, s2 = path[i], path[i + 1]
        for edge in graph.get_neighbors(s1):
            if edge.dest_state == s2:
                total_cost += edge.cost
                break

    duration_ms = round((time.perf_counter() - t0) * 1000, 3)
    return {
        "algorithm": "Hill Climbing (Local Search)",
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
        "step_evaluations": step_evaluations,
        "explanation": (
            "Hill Climbing reached the goal state by strictly ascending/descending along steepest heuristic gradients. "
            f"Completed in {len(path)-1} transitions with total effort cost of {total_cost:.2f} hours."
        ),
    }
