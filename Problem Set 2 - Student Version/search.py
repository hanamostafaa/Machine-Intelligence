from typing import Tuple
from game import HeuristicFunction, Game, S, A
from helpers.utils import NotImplemented

#TODO: Import any modules you want to use

# All search functions take a problem, a state, a heuristic function and the maximum search depth.
# If the maximum search depth is -1, then there should be no depth cutoff (The expansion should not stop before reaching a terminal state) 

# All the search functions should return the expected tree value and the best action to take based on the search results

# This is a simple search function that looks 1-step ahead and returns the action that lead to highest heuristic value.
# This algorithm is bad if the heuristic function is weak. That is why we use minimax search to look ahead for many steps.
def greedy(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    agent = game.get_turn(state)
    
    terminal, values = game.is_terminal(state)
    if terminal: return values[agent], None

    actions_states = [(action, game.get_successor(state, action)) for action in game.get_actions(state)]
    value, _, action = max((heuristic(game, state, agent), -index, action) for index, (action , state) in enumerate(actions_states))
    return value, action

# Apply Minimax search and return the game tree value and the best action
# Hint: There may be more than one player, and in all the testcases, it is guaranteed that 
# game.get_turn(state) will return 0 (which means it is the turn of the player). All the other players
# (turn > 0) will be enemies. So for any state "s", if the game.get_turn(s) == 0, it should a max node,
# and if it is > 0, it should be a min node. Also remember that game.is_terminal(s), returns the values
# for all the agents. So to get the value for the player (which acts at the max nodes), you need to
# get values[0].
def minimax(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    #TODO: Complete this function
    terminal, values = game.is_terminal(state)
    if terminal: return values[0], None
    if max_depth == 0: return heuristic(game, state, 0), None

    turn = game.get_turn(state)
    actions_states = [(action, game.get_successor(state, action)) for action in game.get_actions(state)]

    if turn == 0:
        value, _, action = max((minimax(game, state, heuristic, max_depth - 1)[0], -index, action) for index, (action , state) in enumerate(actions_states))
        return value,action
    else:
        value, _, action = min((minimax(game, state, heuristic, max_depth - 1)[0], -index, action) for index, (action , state) in enumerate(actions_states))
        return value,action
    

# Apply Alpha Beta pruning and return the tree value and the best action
# Hint: Read the hint for minimax.
def alphabeta(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:

    def alpha_beta_pruning(state, depth, alpha, beta):
        terminal, values = game.is_terminal(state)
        if terminal:
            return values[0], None # return none as action in case of terminal state

        if depth == 0:
            return heuristic(game, state, 0), None # in case of depth limit reached -> apply heuristic

        turn = game.get_turn(state) # get current turn (min or max)
        actions = game.get_actions(state)

        best_action = None # this will hold the best action found


        if turn == 0: # max node
            value = float("-inf")

            for action in actions: # for every possible action
                child = game.get_successor(state, action)
                child_val, _ = alpha_beta_pruning(child, depth - 1, alpha, beta) # call minimax with alpha beta pruning recursively

                if child_val > value: # if found better value
                    value = child_val # update value 
                    best_action = action # store action that lead to this value

                if value >= beta:
                    break  # prune

                alpha = max(alpha, value) # update alpha (best value for max node so far)

            return value, best_action

    
        else: # min node
            value = float("inf")

            for action in actions:
                child = game.get_successor(state, action)
                child_val, _ = alpha_beta_pruning(child, depth - 1, alpha, beta)

                if child_val < value:
                    value = child_val
                    best_action = action

                if value <= alpha:
                    break  # prune

                beta = min(beta, value) # update beta (best value for min node so far)

            return value, best_action

    return alpha_beta_pruning(state, max_depth, float("-inf"), float("inf")) # alpha, beta starting with -inf, inf

# Apply Alpha Beta pruning with move ordering and return the tree value and the best action
# Hint: Read the hint for minimax.
def alphabeta_with_move_ordering(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    #TODO: Complete this function
    NotImplemented()

# Apply Expectimax search and return the tree value and the best action
# Hint: Read the hint for minimax, but note that the monsters (turn > 0) do not act as min nodes anymore,
# they now act as chance nodes (they act randomly).
def expectimax(game: Game[S, A], state: S, heuristic: HeuristicFunction, max_depth: int = -1) -> Tuple[float, A]:
    #TODO: Complete this function
    NotImplemented()