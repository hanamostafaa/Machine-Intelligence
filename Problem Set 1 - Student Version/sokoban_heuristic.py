from sokoban import SokobanProblem, SokobanState
from mathutils import Direction, Point, manhattan_distance
from helpers.utils import NotImplemented

# This heuristic returns the distance between the player and the nearest crate as an estimate for the path cost
# While it is consistent, it does a bad job at estimating the actual cost thus the search will explore a lot of nodes before finding a goal
def weak_heuristic(problem: SokobanProblem, state: SokobanState):
    return min(manhattan_distance(state.player, crate) for crate in state.crates) - 1

#TODO: Import any modules and write any functions you want to use
def strong_heuristic(problem: SokobanProblem, state: SokobanState) -> float:
    if state in problem.cache():
        return problem.cache()[state]

    if problem.is_goal(state):
        problem.cache()[state] = 0
        return 0

    crates = state.crates
    goals = problem.layout.goals

    if not crates:
        problem.cache()[state] = 0
        return 0

    # Player to crate distance
    h1 = min(manhattan_distance(state.player, crate) for crate in crates)

    # Misplaced Crates to goal distances
    misplaced_crates = [crate for crate in crates if crate not in goals]
    h2 = sum(min(manhattan_distance(crate, goal) for goal in goals) for crate in misplaced_crates)

    # number of misplaced crates
    h3 = len(misplaced_crates)

    h = max(h1, h2, h3) # max of 3 heuristics

    problem.cache()[state] = h
    return h


    