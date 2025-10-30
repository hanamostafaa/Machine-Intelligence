from sokoban import SokobanProblem, SokobanState
from mathutils import Direction, Point, manhattan_distance
from helpers.utils import NotImplemented
import itertools
import math

def weak_heuristic(problem: SokobanProblem, state: SokobanState):
    return min(manhattan_distance(state.player, crate) for crate in state.crates) - 1

def is_deadlocked(goals, cx, cy, walls):
    # Corner deadlock (unless on a goal)
    if ((cx-1, cy) in walls and (cx, cy-1) in walls) or \
       ((cx+1, cy) in walls and (cx, cy-1) in walls) or \
       ((cx-1, cy) in walls and (cx, cy+1) in walls) or \
       ((cx+1, cy) in walls and (cx, cy+1) in walls):
        return True

    # Tight wall corner
    if ((cx-1, cy) in walls or (cx+1, cy) in walls) and \
       ((cx, cy-1) in walls or (cx, cy+1) in walls):
        return True

    # Wall-aligned scanning deadlocks
    if (cx-1, cy) in walls or (cx+1, cy) in walls:
        return is_stuck_along_wall(cx, cy, walls, goals, vertical=True)
    if (cx, cy-1) in walls or (cx, cy+1) in walls:
        return is_stuck_along_wall(cx, cy, walls, goals, vertical=False)

    return False


def is_stuck_along_wall(cx, cy, walls, goals, vertical=True):
    if vertical:
        # Up
        y = cy - 1
        while (cx, y) not in walls:
            if (cx, y) in goals:
                return False
            if ((cx-1, y) not in walls) and ((cx+1, y) not in walls):
                return False
            y -= 1

        # Down
        y = cy + 1
        while (cx, y) not in walls:
            if (cx, y) in goals:
                return False
            if ((cx-1, y) not in walls) and ((cx+1, y) not in walls):
                return False
            y += 1
    else:
        # Left
        x = cx - 1
        while (x, cy) not in walls:
            if (x, cy) in goals:
                return False
            if ((x, cy-1) not in walls) and ((x, cy+1) not in walls):
                return False
            x -= 1

        # Right
        x = cx + 1
        while (x, cy) not in walls:
            if (x, cy) in goals:
                return False
            if ((x, cy-1) not in walls) and ((x, cy+1) not in walls):
                return False
            x += 1
    return True


matching_cache = {}
def min_matching_cost(crates, goals):
    crates_key = tuple(sorted((c.x, c.y) for c in crates))

    if crates_key in matching_cache:
        return matching_cache[crates_key]

    min_cost = math.inf
    for perm in itertools.permutations(goals, len(crates)):
        cost = sum(abs(cx - gx) + abs(cy - gy)
                   for (cx, cy), (gx, gy) in zip(crates, perm))
        min_cost = min(min_cost, cost)

    matching_cache[crates_key] = min_cost
    return min_cost

def strong_heuristic(problem: SokobanProblem, state: SokobanState) -> float:
    cache = problem.cache()
    if state in cache:
        return cache[state]

    if problem.is_goal(state):
        cache[state] = 0.0
        return 0.0

    layout = problem.layout

    # Cache walls
    if 'walls' not in cache:
        walkable = {(p.x, p.y) for p in layout.walkable}
        cache['walls'] = {(x, y) for x in range(layout.width)
                          for y in range(layout.height)
                          if (x, y) not in walkable}
    walls = cache['walls']

    # Cache goals
    if 'goals' not in cache:
        cache['goals'] = [(g.x, g.y) for g in layout.goals]
    goals = cache['goals']

    crates = state.crates

    # Deadlock detection
    for (cx, cy) in crates:
        if (cx, cy) not in goals and is_deadlocked(goals, cx, cy, walls):
            cache[state] = float('inf')
            return float('inf')

    # Player distance to nearest crate
    px, py = state.player.x, state.player.y
    h_player = min(abs(px - cx) + abs(py - cy) for (cx, cy) in crates)

    # One-to-one crate–goal matching
    h_crates = min_matching_cost(crates, goals)

    # Weighted combination
    h = h_crates + 0.49* h_player
    h = round(h)

    cache[state] = h
    return h
