from sokoban import SokobanProblem, SokobanState
from mathutils import Direction, Point, manhattan_distance
from helpers.utils import NotImplemented

# This heuristic returns the distance between the player and the nearest crate as an estimate for the path cost
# While it is consistent, it does a bad job at estimating the actual cost thus the search will explore a lot of nodes before finding a goal
def weak_heuristic(problem: SokobanProblem, state: SokobanState):
    return min(manhattan_distance(state.player, crate) for crate in state.crates) - 1

# sokoban_heuristics.py

from itertools import permutations
from collections import deque
import math

# --- Helpers ---------------------------------------------------------------

def to_tuple(p):
    """Support both Point-like objects and (x,y) tuples."""
    try:
        return (p.x, p.y)
    except AttributeError:
        return tuple(p)

def manhattan_distance(a, b):
    ax, ay = to_tuple(a)
    bx, by = to_tuple(b)
    return abs(ax - bx) + abs(ay - by)

def is_corner_deadlock(pos, walls, goals_set):
    """
    Simple corner check: if a crate is in a corner (two orthogonal walls) and not on a goal -> deadlocked.
    pos: (x,y) tuple
    walls: set of (x,y)
    goals_set: set of (x,y)
    """
    if pos in goals_set:
        return False
    x,y = pos
    up = (x, y-1)
    down = (x, y+1)
    left = (x-1, y)
    right = (x+1, y)
    # check (up or down) AND (left or right)
    if (up in walls or down in walls) and (left in walls or right in walls):
        return True
    return False

def is_edge_deadlock(pos, walls, goals_set, layout):
    """
    Simple detection: crate stuck along a wall row/column where no goal exists on that corridor.
    This is conservative and cheap: checks along straight lines (left-right or up-down).
    """
    if pos in goals_set:
        return False
    x,y = pos
    # check horizontally: if both up and down are walls (i.e., crate can't be moved vertically)
    up = (x,y-1)
    down = (x,y+1)
    left = (x-1,y)
    right = (x+1,y)
    width, height = layout.width, layout.height

    # vertical blockage (can't move up/down)
    if up in walls and down in walls:
        # check if there's any goal in this row reachable horizontally without crossing a wall
        # scan leftwards until wall, scan rightwards until wall
        # if no goal in that horizontal segment -> deadlock
        lx = x
        while (lx-1, y) not in walls and lx-1 >= 0:
            lx -= 1
        rx = x
        while (rx+1, y) not in walls and rx+1 < width:
            rx += 1
        # check if any goal in [lx..rx] on row y
        for gx in range(lx, rx+1):
            if (gx, y) in goals_set:
                return False
        return True

    # horizontal blockage (can't move left/right)
    if left in walls and right in walls:
        ly = y
        while (x, ly-1) not in walls and ly-1 >= 0:
            ly -= 1
        ry = y
        while (x, ry+1) not in walls and ry+1 < height:
            ry += 1
        for gy in range(ly, ry+1):
            if (x, gy) in goals_set:
                return False
        return True

    return False

# --- Heuristics ------------------------------------------------------------

def _min_assignment_cost(cost_matrix):
    """
    cost_matrix: list of lists with shape (n_crates, n_goals) (assume n_crates <= n_goals).
    If n_crates is small (<=7) compute optimal assignment by brute-force permutations.
    Otherwise fall back to a greedy matching (fast).
    Returns minimal total cost.
    """
    n = len(cost_matrix)
    if n == 0:
        return 0
    m = len(cost_matrix[0])
    # small-case exact solution via permutations of goal indices
    if n <= 7:
        best = math.inf
        goal_indices = list(range(m))
        # generate permutations of m choose n: use permutations of the first m and take combinations implicitly
        # faster: iterate permutations of the goals of length n
        for perm in permutations(goal_indices, n):
            total = 0
            for i in range(n):
                total += cost_matrix[i][perm[i]]
                if total >= best:
                    break
            if total < best:
                best = total
        return best
    # fallback greedy (not guaranteed optimal)
    remaining_goals = set(range(m))
    total = 0
    for i in range(n):
        # choose minimal available goal for crate i
        best_g = min(remaining_goals, key=lambda g: cost_matrix[i][g])
        total += cost_matrix[i][best_g]
        remaining_goals.remove(best_g)
        if not remaining_goals:
            break
    return total

def h_matching_manhattan(problem, state):
    """
    Minimum bipartite matching between crates and goals using Manhattan distances (optimal for small crate counts).
    Admissible (ignores walls).
    """
    crates = list(state.crates)
    goals = list(problem.layout.goals)
    if not crates:
        return 0.0
    # build cost matrix (crates x goals)
    cost_matrix = []
    for c in crates:
        row = []
        for g in goals:
            row.append(manhattan_distance(c, g))
        cost_matrix.append(row)
    return float(_min_assignment_cost(cost_matrix))

def h_deadlock_penalty(problem, state, corner_penalty=1000.0, edge_penalty=50.0):
    """
    Matching + heavy penalty if any crate is in an immediate deadlock (corner or corridor deadlock).
    This heuristic is NOT strictly admissible if penalties are large, but helps prune dead states.
    """
    crates = list(state.crates)
    goals = list(problem.layout.goals)
    if not crates:
        return 0.0
    layout = problem.layout
    # convert walls and goals to tuple sets
    walls = {to_tuple(p) for p in {Point(x, y) for x in range(layout.width)
                        for y in range(layout.height)
                        if Point(x, y) not in layout.walkable}} if False else None
    # The above weirdness: we don't assume Point class available here.
    # Use problem.layout.walkable / width/height to reconstruct walls if available.
    # Safer: derive walls from layout.walkable if present (layout.walkable likely exists).
    cache = problem.cache()
    if 'walls' not in cache:
        try:
            walkable = {to_tuple(p) for p in layout.walkable}
            cache['walls'] = {(x, y) for x in range(layout.width)
                              for y in range(layout.height)
                              if (x, y) not in walkable}
        except Exception:
            cache['walls'] = set()
    walls = cache['walls']


    if 'goals' not in cache:
        try:
            cache['goals'] = {to_tuple(g) for g in goals}
        except Exception:
            cache['goals'] = set()
    goals_set = cache['goals']

    # base matching cost
    base = h_matching_manhattan(problem, state)
    penalty = 0.0
    for c in crates:
        ct = to_tuple(c)
        if is_corner_deadlock(ct, walls, goals_set):
            penalty += corner_penalty
        elif is_edge_deadlock(ct, walls, goals_set, layout):
            penalty += edge_penalty
    return float(base + penalty)

def h_sum_nearest_manhattan(problem, state):
    crates = list(state.crates)
    goals = list(problem.layout.goals)
    if not crates:
        return 0.0
    total = 0
    for c in crates:
        total += min(abs(c.x - g.x) + abs(c.y - g.y) for g in goals)
    return float(total)

def h_deadlock_light(problem, state):
    crates = list(state.crates)
    goals = list(problem.layout.goals)
    layout = problem.layout
    cache = problem.cache()

    if 'walls' not in cache:
        walkable = { (p.x, p.y) for p in layout.walkable }
        cache['walls'] = {(x, y) for x in range(layout.width)
                          for y in range(layout.height)
                          if (x, y) not in walkable}
    walls = cache['walls']

    if 'goals' not in cache:
        cache['goals'] = {(g.x, g.y) for g in goals}
    goals_set = cache['goals']

    base = h_sum_nearest_manhattan(problem, state)
    penalty = 0.0
    for c in crates:
        if is_corner_deadlock((c.x, c.y), walls, goals_set):
            penalty += 200  # lighter than 1000
    return base + penalty

ALL_HEURISTICS = {
    'matching_manhattan': h_matching_manhattan,
    'deadlock_penalty': h_deadlock_penalty,
    'sum_nearest_manhattan': h_sum_nearest_manhattan, # light versions 
    'deadlock_light': h_deadlock_light # light versions 
}

def select_heuristic(name):
    """Return the heuristic callable by name (or raise KeyError)."""
    return ALL_HEURISTICS[name]

# ---------------------------------------------------------------------------

def strong_heuristic2(problem, state):
    return select_heuristic('deadlock_light')(problem, state)

def strong_heuristic(problem: SokobanProblem, state: SokobanState) -> float:
    cache = problem.cache()
    if state in cache:
        return cache[state]

    if problem.is_goal(state):
        cache[state] = 0.0
        return 0.0

    layout = problem.layout

    if 'walls' not in cache:
        walkable = {(p.x, p.y) for p in layout.walkable}
        cache['walls'] = {(x, y) for x in range(layout.width)
                          for y in range(layout.height)
                          if (x, y) not in walkable}
    walls = cache['walls']

    if 'goals' not in cache:
        cache['goals'] = [(g.x, g.y) for g in layout.goals]
    goals = cache['goals']

    if 'goal_dists' not in cache:
        goal_dists = {}
        for x in range(layout.width):
            for y in range(layout.height):
                if (x, y) not in walls:
                    goal_dists[(x, y)] = min(abs(x - gx) + abs(y - gy) for gx, gy in goals)
        cache['goal_dists'] = goal_dists
    goal_dists = cache['goal_dists']

    crates = [(c.x, c.y) for c in state.crates]
    if not crates:
        cache[state] = 0.0
        return 0.0

    for (cx, cy) in crates:
        if (cx, cy) not in goals:
            if ((cx + 1, cy) in walls or (cx - 1, cy) in walls) and \
               ((cx, cy + 1) in walls or (cx, cy - 1) in walls):
                cache[state] = float('inf')
                return float('inf')

    px, py = state.player.x, state.player.y
    h_player = min(abs(px - cx) + abs(py - cy) for (cx, cy) in crates)
    h_crates = sum(goal_dists[(cx, cy)] for (cx, cy) in crates)

    h = h_crates + 0.25 * h_player

    h = round(h)  

    cache[state] = h
    return h


