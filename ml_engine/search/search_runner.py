from typing import Dict, Any, List, Optional
from ml_engine.search.graph import InterventionStateSpace
from ml_engine.search.bfs import breadth_first_search
from ml_engine.search.dfs import depth_first_search
from ml_engine.search.best_first import best_first_search
from ml_engine.search.hill_climbing import hill_climbing_search
from ml_engine.search.a_star import a_star_search

class SearchAlgorithmRunner:
    """
    Central runner and comparison harness for CSE276 Unit II Search Algorithms.
    Allows executing individual algorithms or running a comparative benchmark.
    """

    def __init__(self, state_space: Optional[InterventionStateSpace] = None):
        self.graph = state_space or InterventionStateSpace()

    def execute_algorithm(
        self,
        algorithm_name: str,
        start_state: str = "INITIAL_REVIEW",
        goal_state: str = "PLAN_COMPLETED",
    ) -> Dict[str, Any]:
        """Executes a single search algorithm on the intervention state-space."""
        algo_key = algorithm_name.strip().lower()

        if algo_key in ("bfs", "breadth_first_search", "breadth-first search", "breadth first search"):
            return breadth_first_search(self.graph, start_state, goal_state)
        elif algo_key in ("dfs", "depth_first_search", "depth-first search", "depth first search"):
            return depth_first_search(self.graph, start_state, goal_state)
        elif algo_key in ("best_first", "best-first", "best first", "best-first search", "greedy_best_first"):
            return best_first_search(self.graph, start_state, goal_state)
        elif algo_key in ("hill_climbing", "hill-climbing", "hill climbing"):
            return hill_climbing_search(self.graph, start_state, goal_state)
        elif algo_key in ("a_star", "a*", "a_star_search", "astar"):
            return a_star_search(self.graph, start_state, goal_state)
        else:
            raise ValueError(
                f"Unknown algorithm '{algorithm_name}'. Supported: BFS, DFS, Best-First, Hill Climbing, A*"
            )

    def compare_all(
        self,
        start_state: str = "INITIAL_REVIEW",
        goal_state: str = "PLAN_COMPLETED",
    ) -> Dict[str, Any]:
        """Runs all 5 algorithms and outputs a structured comparative analysis."""
        algorithms = ["BFS", "DFS", "Best-First", "Hill Climbing", "A*"]
        results = []

        for algo in algorithms:
            res = self.execute_algorithm(algo, start_state, goal_state)
            results.append({
                "algorithm": res["algorithm"],
                "path": res["path"],
                "step_count": res["step_count"],
                "path_cost": res["path_cost"],
                "nodes_expanded": res["nodes_expanded"],
                "duration_ms": res["duration_ms"],
                "completion_status": res["completion_status"],
            })

        return {
            "start_state": start_state,
            "goal_state": goal_state,
            "comparison": results,
            "graph_summary": {
                "total_states": len(self.graph.states),
                "total_transitions": len(self.graph.transitions),
            },
        }

    def get_graph_data(self) -> Dict[str, Any]:
        """Returns the serialized state-space graph for frontend rendering."""
        return self.graph.to_graph_data()
