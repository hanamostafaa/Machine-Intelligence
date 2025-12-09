from typing import Dict, Optional
from agents import Agent
from environment import Environment
from mdp import MarkovDecisionProcess, S, A
import json
from helpers.utils import NotImplemented

# This is a class for a generic Value Iteration agent
class ValueIterationAgent(Agent[S, A]):
    mdp: MarkovDecisionProcess[S, A] # The MDP used by this agent for training 
    utilities: Dict[S, float] # The computed utilities
                                # The key is the string representation of the state and the value is the utility
    discount_factor: float # The discount factor (gamma)

    def __init__(self, mdp: MarkovDecisionProcess[S, A], discount_factor: float = 0.99) -> None:
        super().__init__()
        self.mdp = mdp
        self.utilities = {state:0 for state in self.mdp.get_states()} # We initialize all the utilities to be 0
        self.discount_factor = discount_factor
    
    # Given a state, compute its utility using the bellman equation
    # if the state is terminal, return 0
    def compute_bellman(self, state: S) -> float:
        #TODO: Complete this function
        if self.mdp.is_terminal(state): # terminal state -> return 0
            return 0.0
        max_utility = float('-inf') # this will store the max utility possible
        for action in self.mdp.get_actions(state): # loop on all possible actions
            expected_utility = 0.0 # this will store the expected utility for this action
            successors = self.mdp.get_successor(state, action)
            for next_state, prob in successors.items(): # loop on all possible successor states
                reward = self.mdp.get_reward(state, action, next_state) # r(s,a,s')
                expected_utility += prob * (reward + self.discount_factor * self.utilities[next_state]) # sum over s' [ P(s'|s,a) * (r(s,a,s') + gamma * U(s')) ]
            if expected_utility > max_utility:
                max_utility = expected_utility # store the max utility
        return max_utility
    
    # Applies a single utility update
    # then returns True if the utilities has converged (the maximum utility change is less or equal the tolerance)
    # and False otherwise
    def update(self, tolerance: float = 0) -> bool:
        #TODO: Complete this function
        new_utilities = {} # to store the new utilities after update
        max_change = 0.0 # stop when max change <= tolerance
        for state in self.mdp.get_states():
            new_utility = self.compute_bellman(state) # compute new utility using bellman equation
            new_utilities[state] = new_utility # store new utility
            change = abs(new_utility - self.utilities[state]) # compute change
            if change > max_change: # update max change
                max_change = change
        self.utilities = new_utilities # update utilities
        return max_change <= tolerance

    # This function applies value iteration starting from the current utilities stored in the agent and stores the new utilities in the agent
    # NOTE: this function does incremental update and does not clear the utilities to 0 before running
    # In other words, calling train(M) followed by train(N) is equivalent to just calling train(N+M)
    def train(self, iterations: Optional[int] = None, tolerance: float = 0) -> int:
        #TODO: Complete this function to apply value iteration for the given number of iterations
        iters = 0
        if iterations is not None:
            for _ in range(iterations):
                iters += 1
                converged = self.update(tolerance) # perform update step for each iteration
                if converged:
                    break
        return iters
    
    # Given an environment and a state, return the best action as guided by the learned utilities and the MDP
    # If the state is terminal, return None
    def act(self, env: Environment[S, A], state: S) -> A:
        #TODO: Complete this function
        if self.mdp.is_terminal(state): # terminal state -> no action
            return None
        best_action = None # to store the best action
        max_utility = float('-inf') # to store the max utility
        for action in self.mdp.get_actions(state): # loop on all possible actions
            expected_utility = 0.0 # to store the expected utility for this action
            successors = self.mdp.get_successor(state, action) # get successor states
            for next_state, prob in successors.items(): 
                reward = self.mdp.get_reward(state, action, next_state) # r(s,a,s')
                expected_utility += prob * (reward + self.discount_factor * self.utilities[next_state])
            if expected_utility > max_utility: # update best action if this action has higher expected utility
                max_utility = expected_utility
                best_action = action
        return best_action 
    
    # Save the utilities to a json file
    def save(self, env: Environment[S, A], file_path: str):
        with open(file_path, 'w') as f:
            utilities = {self.mdp.format_state(state): value for state, value in self.utilities.items()}
            json.dump(utilities, f, indent=2, sort_keys=True)
    
    # loads the utilities from a json file
    def load(self, env: Environment[S, A], file_path: str):
        with open(file_path, 'r') as f:
            utilities = json.load(f)
            self.utilities = {self.mdp.parse_state(state): value for state, value in utilities.items()}
