from sokoban import SokobanProblem, SokobanState
from mathutils import Direction, Point, manhattan_distance
from helpers.utils import NotImplemented

# This heuristic returns the distance between the player and the nearest crate as an estimate for the path cost
# While it is consistent, it does a bad job at estimating the actual cost thus the search will explore a lot of nodes before finding a goal
def weak_heuristic(problem: SokobanProblem, state: SokobanState):
    return min(manhattan_distance(state.player, crate) for crate in state.crates) - 1

#TODO: Import any modules and write any functions you want to use
def strong_heuristic(problem: SokobanProblem, state: SokobanState) -> float:

    if problem.is_goal(state):
        return 0

    crates = state.crates
    goals = problem.layout.goals

    if not crates:
        return 0

    # Sum of each crate's distance to nearest goal
    total_distance = 0
    min_player_dist = min(manhattan_distance(state.player, crate) for crate in state.crates) - 1
    misplaced_crates = [crate for crate in crates if crate not in goals]
    for crate in misplaced_crates:
        min_dist = min(manhattan_distance(crate, goal) for goal in goals)
        total_distance += min_dist
    return total_distance + min_player_dist