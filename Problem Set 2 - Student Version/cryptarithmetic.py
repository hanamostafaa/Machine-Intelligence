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
        pattern = r"\s*([a-zA-Z]+)\s*\+\s*([a-zA-Z]+)\s*=\s*([a-zA-Z]+)\s*"
        match = re.match(pattern, text)
        if not match:
            raise Exception("Failed to parse:" + text)
        LHS0, LHS1, RHS = [match.group(i+1).upper() for i in range(3)]

        problem = CryptArithmeticProblem()
        problem.LHS = (LHS0, LHS1)
        problem.RHS = RHS

        problem.variables = []
        problem.domains = {}
        problem.constraints = []

        letters = set(LHS0 + LHS1 + RHS) # all unique letters
        # letter variables and domains
        for L in letters:
            problem.variables.append(L)
            problem.domains[L] = set(range(10)) # each letter can be 0-9

        n = len(RHS)  # number of columns (based on RHS length) since len(RHS) >= len(LHS0), len(LHS1)

        # leading letters cannot be zero
        leading = {LHS0[0], LHS1[0], RHS[0]}
        for letter in leading:
            problem.constraints.append(UnaryConstraint(letter, lambda v: v != 0))

        # all letters must be different [pairwise] (binary constraints)
        letter_list = list(letters)
        for i in range(len(letter_list) - 1):
            for j in range(i + 1, len(letter_list)):
                A = letter_list[i]
                B = letter_list[j]
                problem.constraints.append(BinaryConstraint((A, B), lambda a, b: a != b))

        # create carry variables C0..C(n-1)
        for i in range(n):
            var = f"C{i}"
            problem.variables.append(var)
            problem.domains[var] = {0, 1} # each carry can be 0 or 1

        # traverse columns from right to left
        for i in range(n):
            # letters in this column
            L0 = LHS0[-1 - i] if i < len(LHS0) else None
            L1 = LHS1[-1 - i] if i < len(LHS1) else None
            R = RHS[-1 - i]

            # carry in and carry out
            Cin = f"C{i}" 
            Cout = f"C{i+1}" if L0 is not None or L1 is not None else None

            # Mega variables S_i and T_i (S=(x,y,cin), T=(r,cout))
            # x = L0, y = L1, r = R
            S = f"S_{i}"
            T = f"T_{i}"
            problem.variables.extend([S, T])

            # domain of S: if L0 is missing, x must be 0; if L1 missing, y must be 0
            S_domain = set()
            xs = [0] if L0 is None else range(10)
            ys = [0] if L1 is None else range(10)
            for x in xs:
                for y in ys:
                    for c in (0, 1):
                        S_domain.add((x, y, c))
            problem.domains[S] = S_domain

            # T domain (all possible combinations): r in 0..9, cout in {0,1}
            problem.domains[T] = {(r, c) for r in range(10) for c in (0, 1)}

            # map mega variable S to individual letters
            if L0 is not None:
                # S = (x, y, cin) → L0 = x
                problem.constraints.append(BinaryConstraint((L0, S), lambda x, s: s[0] == x))
            if L1 is not None:
                # S = (x, y, cin) → L1 = y
                problem.constraints.append(BinaryConstraint((L1, S), lambda y, s: s[1] == y))
            # S = (x, y, cin) → Cin = cin
            problem.constraints.append(BinaryConstraint((Cin, S), lambda c, s: s[2] == c))

            # map mega variable T to individual letters
            # T = (r, cout) → R = r
            problem.constraints.append(BinaryConstraint((R, T), lambda r, t: t[0] == r))

            # T = (r, cout) → Cout = cout (only if Cout exists)
            if Cout is not None:
                problem.constraints.append(BinaryConstraint((Cout, T), lambda c, t: t[1] == c))

            # column equation constraint S->T: (x + y + cin) == r + 10 * cout
            def col_rule(s, t):
                x, y, cin = s
                r, cout = t
                total = x + y + cin
                return total == r + 10 * cout
            problem.constraints.append(BinaryConstraint((S, T), col_rule))

            # if both L0 and L1 are None (both LHS don't have this column)
            # then the sum is 0 + 0 + Cin -> R must equal Cin and Cout must be 0.
            if L0 is None and L1 is None:
                # ensure R equals Cin and Cout == 0 (if Cout exists)
                problem.constraints.append(BinaryConstraint((R, Cin), lambda r, c: r == c))

        return problem

    # Read a cryptarithmetic puzzle from a file
    @staticmethod
    def from_file(path: str) -> "CryptArithmeticProblem":
        with open(path, 'r') as f:
            return CryptArithmeticProblem.from_text(f.read())