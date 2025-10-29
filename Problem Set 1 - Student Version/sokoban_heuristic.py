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

    if pos in goals_set:
        return False
    x,y = pos
    up = (x,y-1)
    down = (x,y+1)
    left = (x-1,y)
    right = (x+1,y)
    width, height = layout.width, layout.height

    if up in walls or down in walls:
        lx = x
        while (lx-1, y) not in walls and lx-1 >= 0:
            lx -= 1
        rx = x
        while (rx+1, y) not in walls and rx+1 < width:
            rx += 1
        for gx in range(lx, rx+1):
            if (gx, y) in goals_set:
                return False
        return True

    if left in walls or right in walls:
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

    for (cx, cy) in crates:
        if (cx, cy) not in goals:
            if (((cx + 1, cy) in walls or (cx - 1, cy) in walls) and \
               ((cx, cy + 1) in walls or (cx, cy - 1) in walls)) or is_edge_deadlock((cx, cy), walls, goals, layout):
                cache[state] = float('inf')
                return float('inf')

    px, py = state.player.x, state.player.y
    h_player = min(abs(px - cx) + abs(py - cy) for (cx, cy) in crates)
    h_crates = sum(goal_dists[(cx, cy)] for (cx, cy) in crates)

    h = h_crates + 0.45 * h_player 

    h = round(h)  

    cache[state] = h
    return h


