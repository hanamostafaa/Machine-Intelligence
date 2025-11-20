from typing import Tuple
import re
from CSP import Assignment, Problem, UnaryConstraint, BinaryConstraint

#TODO (Optional): Import any builtin library or define any helper function you want to use

# This is a class to define for cryptarithmetic puzzles as CSPs
class CryptArithmeticProblem(Problem):
    LHS: Tuple[str, str]
    RHS: str

    # Convert an assignment into a string (so that is can be printed).
    def format_assignment(self, assignment: Assignment) -> str:
        LHS0, LHS1 = self.LHS
        RHS = self.RHS
        letters = set(LHS0 + LHS1 + RHS)
        formula = f"{LHS0} + {LHS1} = {RHS}"
        postfix = []
        valid_values = list(range(10))
        for letter in letters:
            value = assignment.get(letter)
            if value is None: continue
            if value not in valid_values:
                postfix.append(f"{letter}={value}")
            else:
                formula = formula.replace(letter, str(value))
        if postfix:
            formula = formula + " (" + ", ".join(postfix) +  ")" 
        return formula

    @staticmethod
    def from_text(text: str) -> 'CryptArithmeticProblem':
        # Given a text in the format "LHS0 + LHS1 = RHS", the following regex
        # matches and extracts LHS0, LHS1 & RHS
        # For example, it would parse "SEND + MORE = MONEY" and extract the
        # terms such that LHS0 = "SEND", LHS1 = "MORE" and RHS = "MONEY"
        pattern = r"\s*([a-zA-Z]+)\s*\+\s*([a-zA-Z]+)\s*=\s*([a-zA-Z]+)\s*"
        match = re.match(pattern, text)
        if not match: raise Exception("Failed to parse:" + text)
        LHS0, LHS1, RHS = [match.group(i+1).upper() for i in range(3)]

        problem = CryptArithmeticProblem()
        problem.LHS = (LHS0, LHS1)
        problem.RHS = RHS

        #TODO Edit and complete the rest of this function
        # problem.variables:    should contain a list of variables where each variable is string (the variable name)
        # problem.domains:      should be dictionary that maps each variable (str) to its domain (set of values)
        #                       For the letters, the domain can only contain integers in the range [0,9].
        # problem.constaints:   should contain a list of constraint (either unary or binary constraints).

        problem.variables = []
        problem.domains = {}
        problem.constraints = []
        letters = set(LHS0 + LHS1 + RHS)
        problem.variables.extend(letters)
        n = len(RHS)
        carry_vars = [f"C{i}" for i in range(0, n)] 
        problem.variables.extend(carry_vars)
        for L in letters:
            problem.domains[L] = set(range(10))
        
        leading = {LHS0[0], LHS1[0], RHS[0]}
        # add unary constraints (leading != 0)
        for letter in leading:
            problem.constraints.append(UnaryConstraint(letter, lambda v: v != 0))
        # add uniqueness constraints binary
        letter_list = list(letters)
        for i in range(len(letter_list) - 1):
            for j in range(i + 1, len(letter_list)):
                A = letter_list[i]
                B = letter_list[j]
                problem.constraints.append(
                    BinaryConstraint((A, B),
                                    lambda a, b: a != b)
                )

        n = len(RHS)
        # i can only add binary constraints
        # binary constraint takes a tuple of 2 strings (variable names) and a function that takes 2 values
        for i in range(n):
            # column index (from right)
            L0 = LHS0[-1-i] if i < len(LHS0) else None
            L1 = LHS1[-1-i] if i < len(LHS1) else None
            R = RHS[-1-i]

            Cin = f"C{i}"  
            Cout = f"C{i+1}" if i < n - 1 else None

            # mega variables
            S = f"S_{i}"    # (x, y, cin)
            T = f"T_{i}"    # (r, cout)

            # Add variables
            problem.variables.extend([Cin, Cout, S, T])

            # Domains of carries
            problem.domains[Cin] = {0, 1}
            problem.domains[Cout] = {0, 1}

            # Domain of S mega-variable: all (x,y,cin)
            S_domain = set()
            for x in range(10):
                for y in range(10):
                    for c in [0, 1]:
                        S_domain.add((x, y, c))
            problem.domains[S] = S_domain

            # Domain of T mega-variable: all (r,cout)
            T_domain = set()
            for r in range(10):
                for c in [0, 1]:
                    T_domain.add((r, c))
            problem.domains[T] = T_domain

            # -------- Linking letter → S constraints --------
            if L0 is not None:
                problem.constraints.append(
                    BinaryConstraint((L0, S), lambda x, s: s[0] == x)
                )

            if L1 is not None:
                problem.constraints.append(
                    BinaryConstraint((L1, S), lambda y, s: s[1] == y)
                )

            problem.constraints.append(
                BinaryConstraint((Cin, S), lambda c, s: s[2] == c)
            )

            # -------- Linking result letters → T constraints --------
            problem.constraints.append(
                BinaryConstraint((R, T), lambda r, t: t[0] == r)
            )

            problem.constraints.append(
                BinaryConstraint((Cout, T), lambda c, t: t[1] == c)
            )

            # -------- Arithmetic Check: S → T --------
            def col_rule(s, t):
                x, y, cin = s
                r, cout = t
                total = x + y + cin
                return (total % 10 == r) and (total // 10 == cout)

            problem.constraints.append(
                BinaryConstraint((S, T), col_rule)
            )


        return problem
    # Read a cryptarithmetic puzzle from a file
    @staticmethod
    def from_file(path: str) -> "CryptArithmeticProblem":
        with open(path, 'r') as f:
            return CryptArithmeticProblem.from_text(f.read())