from typing import Any, Dict, List, Optional
from CSP import Assignment, BinaryConstraint, Problem, UnaryConstraint
from helpers.utils import NotImplemented

# This function applies 1-Consistency to the problem.
# In other words, it modifies the domains to only include values that satisfy their variables' unary constraints.
# Then all unary constraints are removed from the problem (they are no longer needed).
# The function returns False if any domain becomes empty. Otherwise, it returns True.
def one_consistency(problem: Problem) -> bool:
    remaining_constraints = []
    solvable = True
    for constraint in problem.constraints:
        if not isinstance(constraint, UnaryConstraint):
            remaining_constraints.append(constraint)
            continue
        variable = constraint.variable
        new_domain = {value for value in problem.domains[variable] if constraint.condition(value)}
        if not new_domain:
            solvable = False
        problem.domains[variable] = new_domain
    problem.constraints = remaining_constraints
    return solvable

# This function returns the variable that should be picked based on the MRV heuristic.
# NOTE: We don't use the domains inside the problem, we use the ones given by the "domains" argument 
#       since they contain the current domains of unassigned variables only.
# NOTE: If multiple variables have the same priority given the MRV heuristic, 
#       we order them in the same order in which they appear in "problem.variables".
def minimum_remaining_values(problem: Problem, domains: Dict[str, set]) -> str:
    _, _, variable = min((len(domains[variable]), index, variable) for index, variable in enumerate(problem.variables) if variable in domains)
    return variable

# This function should implement forward checking
# The function is given the problem, the variable that has been assigned and its assigned value and the domains of the unassigned values
# The function should return False if it is impossible to solve the problem after the given assignment, and True otherwise.
# In general, the function should do the following:
#   - For each binary constraints that involve the assigned variable:
#       - Get the other involved variable.
#       - If the other variable has no domain (in other words, it is already assigned), skip this constraint.
#       - Update the other variable's domain to only include the values that satisfy the binary constraint with the assigned variable.
#   - If any variable's domain becomes empty, return False. Otherwise, return True.
# IMPORTANT: Don't use the domains inside the problem, use and modify the ones given by the "domains" argument 
#            since they contain the current domains of unassigned variables only.
def forward_checking(problem: Problem, assigned_variable: str, assigned_value: Any, domains: Dict[str, set]) -> bool:
    #TODO: Write this function
    for constraint in problem.constraints:
        if not isinstance(constraint, BinaryConstraint): #not a binary constraint
            continue
        if assigned_variable not in constraint.variables: # constraint not related to the assigned variable
            continue
        other_var = constraint.variables[1] if constraint.variables[0] == assigned_variable else constraint.variables[0]
        if other_var not in domains:  # variable is already assigned
            continue
        for domain_val in list(domains[other_var]): #loop over possible domain values
            new_assignment: Assignment = {assigned_variable: assigned_value, other_var: domain_val} #new assignment with assigned value for the assigned var and potential domain val for the other one
            if not constraint.is_satisfied(new_assignment): #if the new assignment is not ok ( violates the constraint)
                domains[other_var].remove(domain_val) #remove the value from the other variable's domain
                if len(domains[other_var]) == 0: #if no domain values left: illegal assignment -> return false
                    return False

    return True


# This function should return the domain of the given variable order based on the "least restraining value" heuristic.
# IMPORTANT: This function should not modify any of the given arguments.
# Generally, this function is very similar to the forward checking function, but it differs as follows:
#   - You are not given a value for the given variable, since you should do the process for every value in the variable's
#     domain to see how much it will restrain the neigbors domain
#   - Here, you do not modify the given domains. But you can create and modify a copy.
# IMPORTANT: If multiple values have the same priority given the "least restraining value" heuristic, 
#            order them in ascending order (from the lowest to the highest value).
# IMPORTANT: Don't use the domains inside the problem, use and modify the ones given by the "domains" argument 
#            since they contain the current domains of unassigned variables only.
def least_restraining_values(problem: Problem, variable_to_assign: str, domains: Dict[str, set]) -> List[Any]:
    #TODO: Write this function
    #returns ordered list (domain) according to restraining values
    removed_vals_count = []
    for val in domains[variable_to_assign]: # loop on all domain values for the variable to be assigned
        removed_counts = 0
        for constraint in problem.constraints:
            if not isinstance(constraint, BinaryConstraint): #not a binary constraint
                continue
            if variable_to_assign not in constraint.variables: # constraint not related to the assigned variable
                continue
            other_var = constraint.variables[1] if constraint.variables[0] == variable_to_assign else constraint.variables[0]
            if other_var not in domains:  # variable is already assigned
                continue
            for domain_val in list(domains[other_var]): #loop over possible domain values
                new_assignment: Assignment = {variable_to_assign: val, other_var: domain_val} #new assignment with assigned value for the assigned var and potential domain val for the other one
                if not constraint.is_satisfied(new_assignment): #if the new assignment is not ok ( violates the constraint)
                    removed_counts+= 1 
        removed_vals_count.append((removed_counts, val)) # add corresponding removed values (from other vars) for each domain value

    removed_vals_count.sort(key=lambda x: (x[0], x[1]))   # sort on removed counts (least restraining) , then on values (for tie break)

    sorted_domain = [val for _, val in removed_vals_count]

    return sorted_domain


# This function should solve CSP problems using backtracking search with forward checking.
# The variable ordering should be decided by the MRV heuristic.
# The value ordering should be decided by the "least restraining value" heurisitc.
# Unary constraints should be handled using 1-Consistency before starting the backtracking search.
# This function should return the first solution it finds (a complete assignment that satisfies the problem constraints).
# If no solution was found, it should return None.
# IMPORTANT: To get the correct result for the explored nodes, you should check if the assignment is complete only once using "problem.is_complete"
#            for every assignment including the initial empty assignment, EXCEPT for the assignments pruned by the forward checking.
#            Also, if 1-Consistency deems the whole problem unsolvable, you shouldn't call "problem.is_complete" at all.
def solve(problem: Problem) -> Optional[Assignment]:
    if not one_consistency(problem):
        return None
    # starting with empty assignment
    return backtrack({}, problem, {var: vals.copy() for var, vals in problem.domains.items()})

def backtrack(assignment: Assignment, problem: Problem, domains: Dict[str, set]) -> Optional[Assignment]:
    # if assignment is complete, return it
    if problem.is_complete(assignment):
        return assignment

    # select unassigned variable using MRV
    unassigned_domains = {v: d for v, d in domains.items() if v not in assignment}
    var = minimum_remaining_values(problem, unassigned_domains) # MRV chooses from unassigned

    # ordered domain values based on least restraining values
    ordered_values = least_restraining_values(problem, var, unassigned_domains)

    for val in ordered_values:
        # copy of domains to be modified by forward checking and passed in recursive call
        new_domains = {v: d.copy() for v, d in unassigned_domains.items()}

        # forward checking (checking that there is new violation and updating domains)
        if forward_checking(problem, var, val, new_domains):
            # assign variable
            assignment[var] = val
            # recursive call with updated domains
            result = backtrack(assignment, problem, new_domains)
            if result is not None:
                return result
            # backtrack
            del assignment[var]

    # no valid assignment found 
    return None


    