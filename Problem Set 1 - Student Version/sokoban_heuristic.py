from mathutils import Point, manhattan_distance
from sokoban import SokobanProblem, SokobanState 
from itertools import permutations

def weak_heuristic(problem: SokobanProblem, state: SokobanState): 
    return min(manhattan_distance(state.player, crate) for crate in state.crates) - 1


def is_deadlock(crate, state):
    goals = state.layout.goals
    walkable = state.layout.walkable
    nearest_goal = min(goals, key=lambda g: manhattan_distance(crate, g))

    directions = {
        "right": (Point(1, 0), lambda: crate.x > nearest_goal.x),   # left
        "left":  (Point(-1, 0), lambda: crate.x < nearest_goal.x),  # right
        "down":  (Point(0, 1), lambda: crate.y > nearest_goal.y),   # above
        "up":    (Point(0, -1), lambda: crate.y < nearest_goal.y),  # below
    }

    for _, (offset, goal_condition) in directions.items():
        neighbor = crate + offset
        if neighbor not in walkable and goal_condition():
            return True

    return False


def min_matching_cost(crates, goals):
    crates = list(crates)
    goals = list(goals)

    n = len(crates)
    cost_matrix = [[manhattan_distance(c, g) for g in goals] for c in crates]

    min_cost = float('inf')
    for perm in permutations(range(n)):
        total = sum(cost_matrix[i][perm[i]] for i in range(n))
        min_cost = min(min_cost, total)
    return min_cost



def strong_heuristic(problem, state):
    crates = state.crates
    goals = problem.layout.goals
    player = state.player
    cache = problem.cache()
    if state in cache: 
        return cache[state]
    if problem.is_goal(state): 
        cache[state] = 0.0 
        return 0.0
    # Deadlock detection
    for crate in crates:
        if crate not in goals and is_deadlock(crate, state):
            cache[state] = float('inf')
            return float('inf')

    # Crate-goal matching heuristic
    h_crates = min_matching_cost(crates, goals)

    # Player distance to the nearest crate (to tighten the heuristic more)
    h_player = min((manhattan_distance(player, c) for c in crates), default=0)

    # Weighted combination (obtained by trial and error)
    h = round(h_crates + 0.45 * h_player)
    cache[state] = h
    return h



