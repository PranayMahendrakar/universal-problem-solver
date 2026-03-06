from typing import Optional

from core.problem import Problem, Solution, ProblemType
from core.classifier import ProblemClassifier
from core.translator import ProblemTranslator
from core.solvers import SymbolicMathSolver, GraphSolver, LinearProgramSolver, LogicCSPSolver


class UniversalProblemSolverEngine:
    """
    Orchestrates the full pipeline:
    1. Classify the problem type
    2. Translate to best representation(s)
    3. Select and run the appropriate solver
    4. Return a Solution with steps and result
    """

    def __init__(self):
        self.classifier = ProblemClassifier()
        self.translator = ProblemTranslator()
        self.solvers = {
            "symbolic": SymbolicMathSolver(),
            "graph": GraphSolver(),
            "lp": LinearProgramSolver(),
            "logic": LogicCSPSolver(),
        }

    def solve(self, problem_text: str) -> Solution:
        """Full pipeline: classify -> translate -> solve."""
        # Step 1: Classify
        problem_type, confidence = self.classifier.classify_with_confidence(problem_text)
        problem = Problem(raw_input=problem_text, problem_type=problem_type)
        problem.metadata["confidence"] = confidence

        # Step 2: Translate
        problem = self.translator.translate(problem)

        # Step 3: Select solver
        solver = self._select_solver(problem_type)

        # Step 4: Solve
        solution = solver.solve(problem)
        problem.solution = solution
        return solution

    def _select_solver(self, problem_type: ProblemType):
        """Route to the best solver based on problem type."""
        if problem_type in (
            ProblemType.LINEAR_PROGRAMMING,
            ProblemType.SCHEDULING,
        ):
            return self.solvers["lp"]

        elif problem_type in (
            ProblemType.GRAPH_THEORY,
            ProblemType.ROUTING,
        ):
            return self.solvers["graph"]

        elif problem_type in (
            ProblemType.LOGIC,
            ProblemType.CONSTRAINT_SATISFACTION,
            ProblemType.SET_THEORY,
        ):
            return self.solvers["logic"]

        else:
            # Default: symbolic math (arithmetic, algebra, calculus, etc.)
            return self.solvers["symbolic"]


def solve(problem_text: str) -> Solution:
    """Convenience function — create engine and solve in one call."""
    engine = UniversalProblemSolverEngine()
    return engine.solve(problem_text)


if __name__ == "__main__":
    examples = [
        "2 + 2 * 3",
        "solve for x: 2x + 5 = 11",
        "maximize: 3x + 2y subject to x + y <= 4, x >= 0, y >= 0",
    ]
    engine = UniversalProblemSolverEngine()
    for ex in examples:
        sol = engine.solve(ex)
        print(f"Problem: {ex}")
        print(f"Result: {sol.result}")
        print("-" * 50)
