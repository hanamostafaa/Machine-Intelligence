from problem import HeuristicFunction, Problem, S, A, Solution
from collections import deque
from helpers.utils import NotImplemented

#TODO: Import any modules you want to use
import heapq
from itertools import count

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
                if problem.is_goal(successor): # if at goal return path (at enqueue)
                    return new_path
                q.append((successor, new_path)) # else add to queue and continue searching 
    return None # no path found return None 

def DepthFirstSearch(problem: Problem[S, A], initial_state: S) -> Solution:
    #TODO: ADD YOUR CODE HERE
    if problem.is_goal(initial_state): # check if already at goal no actions needed
        return []
    
    stack = [(initial_state, [])] # stack for DFS
    visited = set([initial_state]) # keeping track of visited nodes to avoid cycles

    while stack:
        state, path = stack.pop() # getting last state and path
        if problem.is_goal(state): # if at goal return path (at pop)
                    return path
        for action in problem.get_actions(state): # getting every action possible at current state
            successor = problem.get_successor(state, action) # getting new state from that action 
            if successor not in visited:  # if not visited
                visited.add(successor) # mark as visited
                new_path = path + [action] # add action to path
                stack.append((successor, new_path)) # else add to stack and continue searching 
    return None # no path found return None
    

def UniformCostSearch(problem: Problem[S, A], initial_state: S) -> Solution:
    #TODO: ADD YOUR CODE HERE
    if problem.is_goal(initial_state): # check if already at goal no actions needed
        return []
    
    counter = count() # to keep order for equal costs
    pq = [(0,next(counter) , initial_state, [])] # priority queue for UCS
    visited = {} # keeping track of visited nodes and their cost

    while pq:
        cost,_, state, path = heapq.heappop(pq)
        if state in visited and visited[state] <= cost: # if already visited and cost is higher ignore
            continue
        visited[state] = cost # else update/add cost to this state 

        if problem.is_goal(state): # if at goal return path (at dequeue)
            return path
        
        for action in problem.get_actions(state): # getting every action possible at current state
            successor = problem.get_successor(state, action) # getting new state from that action 
            new_path = path + [action] # add action to path
            new_cost = cost + problem.get_cost(state, action) # add cost to path
            heapq.heappush(pq, (new_cost, next(counter), successor, new_path)) # add to priority queue and continue searching 
    return None # no path found return None

def AStarSearch(problem: Problem[S, A], initial_state: S, heuristic: HeuristicFunction) -> Solution:
    #TODO: ADD YOUR CODE HERE
    if problem.is_goal(initial_state): # check if already at goal no actions needed
        return []
    
    counter = count() # to keep order for equal costs
    pq = [(0,next(counter),0 , initial_state, [])] # priority queue for A*
    visited = {} # keeping track of visited nodes and their cost

    while pq:
        cost_h,_,cost, state, path = heapq.heappop(pq)

        if state in visited and visited[state] <= cost_h: # if already visited and cost is higher ignore
            continue
        visited[state] = cost_h # else update/add cost to this state 

        if problem.is_goal(state): # if at goal return path (at dequeue)
            return path
        
        for action in problem.get_actions(state): # getting every action possible at current state
            successor = problem.get_successor(state, action) # getting new state from that action 
            new_path = path + [action] # add action to path
            new_cost = cost + problem.get_cost(state, action) # add cost to path
            cost_and_h = new_cost + heuristic(problem,successor) # calculate f(n) = g(n) + h(n)
            heapq.heappush(pq, (cost_and_h, next(counter),new_cost, successor, new_path)) # add to priority queue and continue searching 
    return None # no path found return None

def BestFirstSearch(problem: Problem[S, A], initial_state: S, heuristic: HeuristicFunction) -> Solution:
    #TODO: ADD YOUR CODE HERE
    if problem.is_goal(initial_state): # check if already at goal no actions needed
        return []
    
    counter = count() # to keep order for equal costs
    pq = [(0,next(counter), initial_state, [])] # priority queue for A*
    visited = {} # keeping track of visited nodes and their cost

    while pq:
        cost_h,_, state, path = heapq.heappop(pq)

        if state in visited and visited[state] <= cost_h: # if already visited and cost is higher ignore
            continue
        visited[state] = cost_h # else update/add cost to this state 

        if problem.is_goal(state): # if at goal return path (at dequeue)
            return path
        
        for action in problem.get_actions(state): # getting every action possible at current state
            successor = problem.get_successor(state, action) # getting new state from that action 
            new_path = path + [action] # add action to path
            heapq.heappush(pq, (heuristic(problem, successor), next(counter), successor, new_path))  # add to priority queue and continue searching 
    return None # no path found return None