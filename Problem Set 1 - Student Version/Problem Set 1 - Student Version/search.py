from problem import HeuristicFunction, Problem, S, A, Solution
from collections import deque
from helpers.utils import NotImplemented

#TODO: Import any modules you want to use
import heapq

# All search functions take a problem and a state
# If it is an informed search function, it will also receive a heuristic function
# S and A are used for generic typing where S represents the state type and A represents the action type

# All the search functions should return one of two possible type:
# 1. A list of actions which represent the path from the initial state to the final state
# 2. None if there is no solution

def BreadthFirstSearch(problem: Problem[S, A], initial_state: S) -> Solution:
    #TODO: ADD YOUR CODE HERE
    if problem.is_goal(initial_state): # check if already at goal no actions needed
        return []
    
    q = deque([(initial_state, [])]) # queue for BFS
    visited = set([initial_state]) # keeping track of visited nodes to avoid cycles

    while q:
        state, path = q.popleft()
        for action in problem.get_actions(state): # getting every action possible at current state
            successor = problem.get_successor(state, action) # getting new state from that action 
            if successor not in visited:  # if not visited
                visited.add(successor) # mark as visited
                new_path = path + [action] # add action to path
                if problem.is_goal(successor): # if at goal return path 
                    return new_path
                q.append((successor, new_path)) # else add to queue and continue searching 
    return None # no path found return None 

def DepthFirstSearch(problem: Problem[S, A], initial_state: S) -> Solution:
    #TODO: ADD YOUR CODE HERE
    NotImplemented()
    

def UniformCostSearch(problem: Problem[S, A], initial_state: S) -> Solution:
    #TODO: ADD YOUR CODE HERE
    NotImplemented()

def AStarSearch(problem: Problem[S, A], initial_state: S, heuristic: HeuristicFunction) -> Solution:
    #TODO: ADD YOUR CODE HERE
    NotImplemented()

def BestFirstSearch(problem: Problem[S, A], initial_state: S, heuristic: HeuristicFunction) -> Solution:
    #TODO: ADD YOUR CODE HERE
    NotImplemented()