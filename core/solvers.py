from typing import Any, Dict, List, Optional
import sympy as sp
import networkx as nx
from scipy.optimize import linprog

from .problem import (
    Problem, Solution, ProblemType, RepresentationType,
    SymbolicRepresentation, GraphRepresentation,
    LinearProgramRepresentation, ConstraintRepresentation
)


class SymbolicMathSolver:
    """Solves algebra, arithmetic, and calculus problems using SymPy."""

    def solve(self, problem: Problem) -> Solution:
        rep = problem.symbolic
        steps = []
        result = None
        variables = {}

        if problem.problem_type == ProblemType.ARITHMETIC:
            try:
                result = float(sp.sympify(problem.raw_input))
                steps.append(f"Evaluated: {problem.raw_input} = {result}")
            except Exception as e:
                result = str(e)

        elif problem.problem_type == ProblemType.ALGEBRA:
            if rep and rep.equalities:
                sols = sp.solve(rep.equalities, rep.variables)
                result = str(sols)
                steps.append(f"Solving system: {rep.equalities}")
                steps.append(f"Solution: {sols}")
                if isinstance(sols, dict):
                    variables = {str(k): float(v) for k, v in sols.items() if v.is_number}

        elif problem.problem_type == ProblemType.CALCULUS:
            meta = problem.metadata
            if meta.get("operation") == "differentiate" and rep:
                expr = rep.expressions[0] if rep.expressions else None
                var = rep.variables[0] if rep.variables else sp.Symbol("x")
                if expr is not None:
                    deriv = sp.diff(expr, var)
                    result = str(deriv)
                    steps.append(f"d/d{var}({expr}) = {deriv}")
            elif meta.get("operation") == "integrate" and rep:
                expr = rep.expressions[0] if rep.expressions else None
                var = rep.variables[0] if rep.variables else sp.Symbol("x")
                if expr is not None:
                    integral = sp.integrate(expr, var)
                    result = str(integral)
                    steps.append(f"integral({expr}) d{var} = {integral} + C")

        if result is None:
            result = "Could not solve symbolically"

        return Solution(
            problem_type=problem.problem_type,
            representation_used=RepresentationType.SYMBOLIC_EQUATION,
            result=result,
            steps=steps,
            variables=variables
        )

class GraphSolver:
    """Solves graph theory problems using NetworkX."""

    def solve(self, problem: Problem) -> Solution:
        rep = problem.graph
        steps = []
        result = None

        if rep is None:
            return Solution(
                problem_type=problem.problem_type,
                representation_used=RepresentationType.GRAPH,
                result="No graph representation available",
                status="error"
            )

        G = nx.DiGraph() if rep.directed else nx.Graph()
        G.add_nodes_from(rep.nodes)
        for u, v, w in rep.edges:
            G.add_edge(u, v, weight=w)

        if problem.problem_type == ProblemType.ROUTING or (
            rep.source is not None and rep.sink is not None
        ):
            try:
                path = nx.shortest_path(G, rep.source, rep.sink, weight="weight")
                length = nx.shortest_path_length(G, rep.source, rep.sink, weight="weight")
                result = f"Path: {path}, Length: {length}"
                steps.append(f"Shortest path from {rep.source} to {rep.sink}")
                steps.append(f"Path: {path}")
                steps.append(f"Total weight: {length}")
            except nx.NetworkXNoPath:
                result = "No path exists"
        elif problem.problem_type == ProblemType.GRAPH_THEORY:
            try:
                mst_edges = list(nx.minimum_spanning_edges(G, weight="weight", data=True))
                total_weight = sum(d["weight"] for _, _, d in mst_edges)
                result = f"MST edges: {[(u, v) for u, v, _ in mst_edges]}, Total: {total_weight}"
                steps.append("Computed Minimum Spanning Tree")
                steps.append(f"Total weight: {total_weight}")
            except Exception as e:
                result = str(e)

        if result is None:
            result = f"Graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges"

        return Solution(
            problem_type=problem.problem_type,
            representation_used=RepresentationType.GRAPH,
            result=result,
            steps=steps
        )

class LinearProgramSolver:
    """Solves linear programming problems using SciPy."""

    def solve(self, problem: Problem) -> Solution:
        rep = problem.lp
        steps = []

        if rep is None:
            return Solution(
                problem_type=problem.problem_type,
                representation_used=RepresentationType.LINEAR_PROGRAM,
                result="No LP representation available",
                status="error"
            )

        c = rep.objective_coeffs
        if rep.objective_sense == "maximize":
            c = [-x for x in c]
            steps.append("Converted maximization to minimization (negating objective)")

        A_ub = rep.ineq_lhs if rep.ineq_lhs else None
        b_ub = rep.ineq_rhs if rep.ineq_rhs else None
        A_eq = rep.eq_lhs if rep.eq_lhs else None
        b_eq = rep.eq_rhs if rep.eq_rhs else None
        bounds = rep.bounds if rep.bounds else [(0, None)] * len(c)

        steps.append(f"Objective ({rep.objective_sense}): {rep.objective_coeffs}")
        if rep.variable_names:
            steps.append(f"Variables: {rep.variable_names}")

        try:
            res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                         bounds=bounds, method="highs")

            if res.success:
                obj_val = -res.fun if rep.objective_sense == "maximize" else res.fun
                var_dict = {}
                if rep.variable_names:
                    var_dict = dict(zip(rep.variable_names, res.x))
                steps.append(f"Optimal value: {obj_val}")
                steps.append(f"Solution: {var_dict or res.x.tolist()}")
                return Solution(
                    problem_type=problem.problem_type,
                    representation_used=RepresentationType.LINEAR_PROGRAM,
                    result=obj_val,
                    steps=steps,
                    numeric_value=float(obj_val),
                    variables=var_dict,
                    status="solved"
                )
            else:
                return Solution(
                    problem_type=problem.problem_type,
                    representation_used=RepresentationType.LINEAR_PROGRAM,
                    result=f"LP infeasible: {res.message}",
                    steps=steps,
                    status="infeasible"
                )
        except Exception as e:
            return Solution(
                problem_type=problem.problem_type,
                representation_used=RepresentationType.LINEAR_PROGRAM,
                result=f"Error: {e}",
                steps=steps,
                status="error"
            )


class LogicCSPSolver:
    """Solves logic and constraint satisfaction problems."""

    def solve(self, problem: Problem) -> Solution:
        steps = []
        result = None

        if problem.problem_type == ProblemType.LOGIC:
            try:
                expr = sp.sympify(problem.raw_input)
                simplified = sp.simplify_logic(expr)
                result = str(simplified)
                steps.append(f"Simplified: {simplified}")
                if simplified == sp.true:
                    steps.append("Expression is a tautology (always true)")
                elif simplified == sp.false:
                    steps.append("Expression is a contradiction (always false)")
            except Exception:
                result = f"Logic evaluation of: {problem.raw_input}"
                steps.append("Could not parse as symbolic logic")

        elif problem.problem_type == ProblemType.CONSTRAINT_SATISFACTION:
            rep = problem.constraints
            if rep:
                result = self._solve_csp(rep, steps)
            else:
                result = "No constraint representation"

        if result is None:
            result = f"Processed: {problem.raw_input[:100]}"

        return Solution(
            problem_type=problem.problem_type,
            representation_used=RepresentationType.CONSTRAINT_SYSTEM,
            result=result,
            steps=steps
        )

    def _solve_csp(self, rep: ConstraintRepresentation, steps: List[str]) -> str:
        steps.append(f"Variables: {list(rep.variables.keys())}")
        steps.append(f"Constraints: {rep.constraints}")
        return f"CSP with {len(rep.variables)} variables and {len(rep.constraints)} constraints"
