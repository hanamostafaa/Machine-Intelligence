# This file contains the options that you should modify to solve Question 2

def question2_1():
    #TODO: Choose options that would lead to the desired results 
    return {
        "noise": 0, 
        "discount_factor": 0.9, # slight discount to prefer earlier rewards
        "living_reward": -5 # negative to encourage reaching the goal quickly
    }

def question2_2():
    #TODO: Choose options that would lead to the desired results
    return {
        "noise": 0.2, # small noise so it would take the safe path
        "discount_factor": 0.3, # heavy discount to prefer +1 over +10
        "living_reward": -0.1 # small negative to encourage reaching a terminal state
    }

def question2_3():
    #TODO: Choose options that would lead to the desired results
    return {
        "noise": 0, # no noise to take the risky path
        "discount_factor": 1, # no discount to prefer +10 over +1
        "living_reward": -3 # negative to encourage reaching a terminal state
    }

def question2_4():
    #TODO: Choose options that would lead to the desired results
        return {
        "noise": 0.2, # noise to take the long safe path
        "discount_factor": 1, # no discount to prefer +10 over +1
        "living_reward": -0.1 # small negative to encourage reaching a terminal state
    }

def question2_5():
    #TODO: Choose options that would lead to the desired results
    return {
        "noise": 0,
        "discount_factor": 1,
        "living_reward": 100 # high living reward to avoid both terminal states
    }

def question2_6():
    #TODO: Choose options that would lead to the desired results
    return {
        "noise": 0,
        "discount_factor": 1,
        "living_reward": -100 # low living reward to prefer any terminal state quickly
    }