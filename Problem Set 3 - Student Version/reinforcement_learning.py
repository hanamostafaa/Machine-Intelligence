from typing import Callable, DefaultDict, Dict, Generic, List, Optional, Union
from agents import Agent
from environment import Environment, S, A
from helpers.mt19937 import RandomGenerator
from helpers.utils import NotImplemented

import json
from collections import defaultdict

# The base class for all Reinforcement Learning Agents required for this problem set


class RLAgent(Agent[S, A]):
    rng: RandomGenerator  # A random number generator used for exploration
    actions: List[A]  # A list of all actions that the environment accepts
    discount_factor: float  # The discount factor "gamma"
    epsilon: float  # The exploration probability for epsilon-greedy
    learning_rate: float  # The learning rate "alpha"

    def __init__(self,
                 actions: List[A],
                 discount_factor: float = 0.99,
                 epsilon: float = 0.5,
                 learning_rate: float = 0.01,
                 seed: Optional[int] = None) -> None:
        super().__init__()
        # initialize the random generator with a seed for reproducability
        self.rng = RandomGenerator(seed)
        self.actions = actions
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.learning_rate = learning_rate

    # A virtual function that returns the Q-value for a specific state and action
    # This should be overriden by the derived RL agents
    def compute_q(self, env: Environment[S, A], state: S, action: A) -> float:
        return 0

    # Returns true if we should explore (rather than exploit)
    def should_explore(self) -> bool:
        return self.rng.float() < self.epsilon

    def act(self, env: Environment[S, A], observation: S, training: bool = False) -> A:
        actions = env.actions()
        if training and self.should_explore():
            # TODO: Return a random action whose index is "self.rng.int(0, len(actions)-1)"
            action_index = self.rng.int(0, len(actions) - 1)
            return actions[action_index]
        else:
            # TODO: return the action with the maximum q-value as calculated by "compute_q" above
            # if more than one action has the maximum q-value, return the one that appears first in the "actions" list
            max_q = float('-inf')
            best_action = actions[0]
            for action in actions:
                q_value = self.compute_q(env, observation, action)
                if q_value > max_q:
                    max_q = q_value
                    best_action = action
            return best_action
#############################
#######     SARSA      ######
#############################

# This is a class for a generic SARSA agent


class SARSALearningAgent(RLAgent[S, A]):
    Q: DefaultDict[S, DefaultDict[A, float]]  # The table of the Q values
    # The first key is the string representation of the state
    # The second key is the string representation of the action
    # The value is the Q-value of the given state and action

    def __init__(self,
                 actions: List[A],
                 discount_factor: float = 0.99,
                 epsilon: float = 0.5,
                 learning_rate: float = 0.01,
                 seed: Optional[int] = None) -> None:
        super().__init__(actions, discount_factor, epsilon, learning_rate, seed)
        self.Q = defaultdict(lambda: defaultdict(
            lambda: 0))  # The default Q value is 0

    def compute_q(self, env: Environment[S, A], state: S, action: A) -> float:
        # Return the Q-value of the given state and action
        return self.Q[state][action]
        # NOTE: we cast the state and the action to a string before querying the dictionaries

    # Update the value of Q(state, action) using this transition via the SARSA update rule
    def update(self, env: Environment[S, A], state: S, action: A, reward: float, next_state: S, next_action: Optional[A]):
        # TODO: Complete this function to update Q-table using the SARSA update rule
        # If next_action is None, then next_state is a terminal state in which case, we consider the Q-value of next_state to be 0
        # Q(s,a) = Q(s,a) + alpha * [ r + gamma * Q(s',a') - Q(s,a) ]
        current_q = self.Q[state][action] # get stored Q(s,a)
        next_q = 0 if next_action is None else self.Q[next_state][next_action]
        td_target = reward + self.discount_factor * next_q # r + gamma * Q(s',a')
        td_delta = td_target - current_q # temporal difference
        self.Q[state][action] = current_q + self.learning_rate * td_delta # update Q-value

    # Save the Q-table to a json file
    def save(self, env: Environment[S, A], file_path: str):
        with open(file_path, 'w') as f:
            Q = {
                env.format_state(state): {
                    env.format_action(action): value for action, value in state_q.items()
                } for state, state_q in self.Q.items()
            }
            json.dump(Q, f, indent=2, sort_keys=True)

    # load the Q-table from a json file
    def load(self, env: Environment[S, A], file_path: str):
        with open(file_path, 'r') as f:
            Q = json.load(f)
            self.Q = {
                env.parse_state(state): {
                    env.parse_action(action): value for action, value in state_q.items()
                } for state, state_q in Q.items()
            }

#############################
#####   Q-Learning     ######
#############################

# This is a class for a generic Q-learning agent


class QLearningAgent(RLAgent[S, A]):
    Q: DefaultDict[str, DefaultDict[str, float]]  # The table of the Q values
    # The first key is the string representation of the state
    # The second key is the string representation of the action
    # The value is the Q-value of the given state and action

    def __init__(self,
                 actions: List[A],
                 discount_factor: float = 0.99,
                 epsilon: float = 0.5,
                 learning_rate: float = 0.01,
                 seed: Optional[int] = None) -> None:
        super().__init__(actions, discount_factor, epsilon, learning_rate, seed)
        self.Q = defaultdict(lambda: defaultdict(
            lambda: 0))  # The default Q value is 0

    def compute_q(self, env: Environment[S, A], state: S, action: A) -> float:
        # Return the Q-value of the given state and action
        return self.Q[state][action] 
        # NOTE: we cast the state and the action to a string before querying the dictionaries

    # Given a state, compute and return the utility of the state using the function "compute_q"
    def compute_utility(self, env: Environment[S, A], state: S) -> float:
        # TODO: Complete this function.
        # The utility of a state is the maximum Q-value over all possible actions in that state
        max_q = float('-inf')
        for action in env.actions(): # loop on all possible actions
            q_value = self.compute_q(env, state, action) # compute Q-value for this action
            if q_value > max_q:
                max_q = q_value
        return max_q # max Q-value is the utility of the state

    # Update the value of Q(state, action) using this transition via the Q-Learning update rule
    def update(self, env: Environment[S, A], state: S, action: A, reward: float, next_state: S, done: bool):
        # TODO: Complete this function to update Q-table using the Q-Learning update rule
        # If done is True, then next_state is a terminal state in which case, we consider the Q-value of next_state to be 0
        # Q = Q + alpha * (reward + gamma * max_a' Q(s', a') - Q)
        current_q = self.compute_q(env, state, action) # Q(s,a)
        if done: # terminal state
            target = reward
        else:
            max_next_q = float('-inf')
            for next_action in env.actions(): # loop on all possible next actions 
                next_q = self.compute_q(env, next_state, next_action) # Q(s',a')
                if next_q > max_next_q:
                    max_next_q = next_q # max_a' Q(s',a')
            target = reward + self.discount_factor * max_next_q # update rule

        self.Q[state][action] = current_q + self.learning_rate * (target - current_q) # store updated Q-value

    # Save the Q-table to a json file
    def save(self, env: Environment[S, A], file_path: str):
        with open(file_path, 'w') as f:
            Q = {
                env.format_state(state): {
                    env.format_action(action): value for action, value in state_q.items()
                } for state, state_q in self.Q.items()
            }
            json.dump(Q, f, indent=2, sort_keys=True)

    # load the Q-table from a json file
    def load(self, env: Environment[S, A], file_path: str):
        with open(file_path, 'r') as f:
            Q = json.load(f)
            self.Q = {
                env.parse_state(state): {
                    env.parse_action(action): value for action, value in state_q.items()
                } for state, state_q in Q.items()
            }

#########################################
#####   Approximate Q-Learning     ######
#########################################
# The type definition for a set of features representing a state
# The key is the feature name and the value is the feature value
Features = Dict[str, float]

# This class takes a state and returns the a set of features


class FeatureExtractor(Generic[S, A]):

    # Returns a list of feature names.
    # This will be used by the Approximate Q-Learning agent to initialize its weights dictionary.
    @property
    def feature_names(self) -> List[str]:
        return []

    # Given an enviroment and an observation (a state), return a set of features that represent the given state
    def extract_features(self, env: Environment[S, A], state: S) -> Features:
        return {}

# This is a class for a generic Q-learning agent


class ApproximateQLearningAgent(RLAgent[S, A]):
    weights: Dict[A, Features]    # The weights dictionary for this agent.
    # The first key is action and the second key is the feature name
    # The value is the weight
    # The feature extractor used to extract the features corresponding to a state
    feature_extractor: FeatureExtractor[S, A]

    def __init__(self,
                 feature_extractor: FeatureExtractor[S, A],
                 actions: List[A],
                 discount_factor: float = 0.99,
                 epsilon: float = 0.5,
                 learning_rate: float = 0.01,
                 seed: Optional[int] = None) -> None:
        super().__init__(actions, discount_factor, epsilon, learning_rate, seed)
        feature_names = feature_extractor.feature_names
        self.weights = {action: {feature: 0 for feature in feature_names}
                        for action in actions}  # we initialize the weights to 0
        self.feature_extractor = feature_extractor

    # Given the features of state and an action, compute and return the Q value
    def __compute_q_from_features(self, features: Dict[str, float], action: A) -> float:
        # TODO: Complete this function
        # NOTE: Remember to cast the action to string before quering self.weights
        # Q(s,a) = sum over f [ weight(a,f) * feature(f) ]
        q_value = 0.0
        for feature, value in features.items():
            q_value += self.weights[action][feature] * value # sum of weight * feature value
        return q_value

    # Given the features of a state, compute and return the utility of the state using the function "__compute_q_from_features"
    def __compute_utility_from_features(self, features: Dict[str, float]) -> float:
        # TODO: Complete this function
        # U(s) = max over a [ Q(s,a) ]
        max_q = float('-inf')
        for action in self.actions: # loop on all possible actions
            q_value = self.__compute_q_from_features(features, action) # compute Q-value for this action
            if q_value > max_q:
                max_q = q_value
        return max_q # max Q-value is the utility of the state

    def compute_q(self, env: Environment[S, A], state: S, action: A) -> float:
        features = self.feature_extractor.extract_features(env, state)
        return self.__compute_q_from_features(features, action)

    # Update the value of Q(state, action) using this transition via the Q-Learning update rule
    def update(self, env: Environment[S, A], state: S, action: A, reward: float, next_state: S, done: bool):
        # TODO: Complete this function to update weights using the Q-Learning update rule
        # If done is True, then next_state is a terminal state in which case, we consider the Q-value of next_state to be 0
        # Q = Q + alpha * (reward + gamma * max_a' Q(s', a') - Q)
        features = self.feature_extractor.extract_features(env, state) # extract features for current state
        current_q = self.__compute_q_from_features(features, action) # Q(s,a)
        if done: # terminal state
            target = reward
        else:
            next_features = self.feature_extractor.extract_features(
                env, next_state) # features for next state
            max_next_q = self.__compute_utility_from_features(next_features) # max_a' Q(s',a')
            target = reward + self.discount_factor * max_next_q # update rule
        for feature, value in features.items():
            # update weight for each feature
            # weight(a,f) = weight(a,f) + alpha * (target - Q(s,a)) * feature(f)
            self.weights[action][feature] += self.learning_rate * (target - current_q) * value  
        

    # Save the weights to a json file
    def save(self, env: Environment[S, A], file_path: str):
        with open(file_path, 'w') as f:
            weights = {env.format_action(
                action): w for action, w in self.weights.items()}
            json.dump(weights, f, indent=2, sort_keys=True)

    # load the weights from a json file
    def load(self, env: Environment[S, A], file_path: str):
        with open(file_path, 'r') as f:
            weights = json.load(f)
            self.weights = {env.parse_action(
                action): w for action, w in weights.items()}
