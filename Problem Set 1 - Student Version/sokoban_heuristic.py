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
    
    remaining_goals = set(goals)
    total_cost = 0
    crates_with_min_dist = []
    for crate in crates:
        if crate in goals:
            min_dist = 0
            min_goal = crate
        else:
            min_dist = float('inf')
            min_goal = None
            for goal in goals:
                dist = manhattan_distance(goal, crate)
                if dist < min_dist:
                    min_dist = dist
                    min_goal = goal
        crates_with_min_dist.append((crate, min_dist, min_goal))

    crates_with_min_dist.sort(key=lambda x: x[1])
    
    # Greedily assign boxes to targets
    for crate, _, _ in crates_with_min_dist:
        if crate in remaining_goals:
            remaining_goals.remove(crate)
            continue
            
        # Find the closest remaining target
        min_dist = float('inf')
        closest_goal = None
        
        for goal in remaining_goals:
            dist = manhattan_distance(crate, goal)
            if dist < min_dist:
                min_dist = dist
                closest_goal = goal
        
        if closest_goal:
            total_cost += min_dist
            remaining_goals.remove(closest_goal)
        else:
            # If no remaining targets, add minimum distance to any target
            # (this is a simplification - should only happen with more boxes than targets)
            min_dist = min(manhattan_distance(crate,t) for t in goals)
            total_cost += min_dist
    min_player_dist = min(manhattan_distance(state.player, crate) for crate in state.crates) - 1
    total_cost = total_cost / len(crates)
    return round(0.67 * total_cost + 0.3* min_player_dist,1)