from sokoban import SokobanProblem, SokobanState
from mathutils import Direction, Point, manhattan_distance
from helpers.utils import NotImplemented

# This heuristic returns the distance between the player and the nearest crate as an estimate for the path cost
# While it is consistent, it does a bad job at estimating the actual cost thus the search will explore a lot of nodes before finding a goal
def weak_heuristic(problem: SokobanProblem, state: SokobanState):
    return min(manhattan_distance(state.player, crate) for crate in state.crates) - 1

import math

def is_deadlocked(goals, cx, cy, walls):
    # Corner check 
    if ((cx-1, cy) in walls and (cx, cy-1) in walls) or \
       ((cx+1, cy) in walls and (cx, cy-1) in walls) or \
       ((cx-1, cy) in walls and (cx, cy+1) in walls) or \
       ((cx+1, cy) in walls and (cx, cy+1) in walls):
        return True

    # If the crate is directly against a wall, check if the entire line is blocked
    # Case 1: wall on the left or right → scan vertically
    if (cx-1, cy) in walls or (cx+1, cy) in walls:
        return is_stuck_along_wall(cx, cy, walls, goals, vertical=True)

    # Case 2: wall above or below → scan horizontally
    if (cx, cy-1) in walls or (cx, cy+1) in walls:
        return is_stuck_along_wall(cx, cy, walls, goals, vertical=False)

    return False


def is_stuck_along_wall(cx, cy, walls, goals, vertical=True):
    """
    Scan along the wall direction (up-down if vertical, left-right if horizontal)
    and check if there is any goal or opening (no wall) along that line.
    If every tile along the wall is also 'boxed in', return True.
    """
    if vertical:
        # Move upward
        y = cy - 1
        while (cx, y) not in walls:
            if (cx, y) in goals:
                return False  # reachable goal on this wall line
            # If space next to the wall opens (no wall beside crate)
            if ((cx-1, y) not in walls) and ((cx+1, y) not in walls):
                return False
            y -= 1

        # Move downward
        y = cy + 1
        while (cx, y) not in walls:
            if (cx, y) in goals:
                return False
            if ((cx-1, y) not in walls) and ((cx+1, y) not in walls):
                return False
            y += 1

    else:
        # Move left
        x = cx - 1
        while (x, cy) not in walls:
            if (x, cy) in goals:
                return False
            if ((x, cy-1) not in walls) and ((x, cy+1) not in walls):
                return False
            x -= 1

        # Move right
        x = cx + 1
        while (x, cy) not in walls:
            if (x, cy) in goals:
                return False
            if ((x, cy-1) not in walls) and ((x, cy+1) not in walls):
                return False
            x += 1

    return True  # whole line blocked — deadlock


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

    crates = state.crates
    h_crates = 0
    for (cx, cy) in crates:
        if (cx, cy) not in goals:
            if (is_deadlocked(goals,cx,cy,walls)):
                cache[state] = float('inf')
                return float('inf')

    px, py = state.player.x, state.player.y
    h_player = min(abs(px - cx) + abs(py - cy) for (cx, cy) in crates)
    h_crates = sum(goal_dists[(cx, cy)] for (cx, cy) in crates)

    h = h_crates + 0.4 * h_player

    h = round(h)  

    cache[state] = h
    return h


