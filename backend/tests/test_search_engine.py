import pytest
from ml_engine.search.graph import InterventionStateSpace
from ml_engine.search.search_runner import SearchAlgorithmRunner
from ml_engine.search.bfs import breadth_first_search
from ml_engine.search.dfs import depth_first_search
from ml_engine.search.best_first import best_first_search
from ml_engine.search.hill_climbing import hill_climbing_search
from ml_engine.search.a_star import a_star_search

@pytest.fixture
def state_space():
    return InterventionStateSpace()

def test_graph_initialization(state_space):
    assert len(state_space.states) == 8
    assert len(state_space.transitions) >= 11
    assert "INITIAL_REVIEW" in state_space.states
    assert "PLAN_COMPLETED" in state_space.states
    assert state_space.get_heuristic("PLAN_COMPLETED") == 0.0
    assert state_space.get_heuristic("INITIAL_REVIEW") == 3.0

def test_bfs_execution(state_space):
    res = breadth_first_search(state_space, "INITIAL_REVIEW", "PLAN_COMPLETED")
    assert res["completion_status"] == "SUCCESS"
    assert res["path"][0] == "INITIAL_REVIEW"
    assert res["path"][-1] == "PLAN_COMPLETED"
    assert res["step_count"] >= 3
    assert len(res["visited_nodes"]) >= 3
    assert res["path_cost"] > 0

def test_dfs_execution(state_space):
    res = depth_first_search(state_space, "INITIAL_REVIEW", "PLAN_COMPLETED")
    assert res["completion_status"] == "SUCCESS"
    assert res["path"][0] == "INITIAL_REVIEW"
    assert res["path"][-1] == "PLAN_COMPLETED"
    assert res["nodes_expanded"] >= 1

def test_best_first_execution(state_space):
    res = best_first_search(state_space, "INITIAL_REVIEW", "PLAN_COMPLETED")
    assert res["completion_status"] == "SUCCESS"
    assert res["path"][0] == "INITIAL_REVIEW"
    assert res["path"][-1] == "PLAN_COMPLETED"
    assert res["nodes_expanded"] >= 1

def test_hill_climbing_execution(state_space):
    res = hill_climbing_search(state_space, "INITIAL_REVIEW", "PLAN_COMPLETED")
    assert res["completion_status"] in ("SUCCESS", "LOCAL_OPTIMUM")
    assert res["path"][0] == "INITIAL_REVIEW"
    assert len(res["path"]) >= 2

def test_a_star_optimality(state_space):
    res = a_star_search(state_space, "INITIAL_REVIEW", "PLAN_COMPLETED")
    assert res["completion_status"] == "SUCCESS"
    assert res["path"][0] == "INITIAL_REVIEW"
    assert res["path"][-1] == "PLAN_COMPLETED"
    # A* path must have cost equal to minimal cost (e.g. INITIAL -> ATTENDANCE_SUPPORT -> FOLLOW_UP -> PLAN_COMPLETED = 1.5 + 1.5 + 0.5 = 3.5)
    # or INITIAL -> MENTOR_MEETING -> ASSIGNMENT_PLANNING -> FOLLOW_UP -> PLAN_COMPLETED = 1.0 + 1.0 + 1.0 + 0.5 = 3.5
    assert res["path_cost"] <= 4.0
    assert len(res["node_evaluations"]) >= 3

def test_search_runner_comparison(state_space):
    runner = SearchAlgorithmRunner(state_space)
    comparison = runner.compare_all("INITIAL_REVIEW", "PLAN_COMPLETED")
    assert len(comparison["comparison"]) == 5
    for c in comparison["comparison"]:
        assert c["completion_status"] in ("SUCCESS", "LOCAL_OPTIMUM")
