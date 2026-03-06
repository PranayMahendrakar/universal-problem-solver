"""
core/translator.py
Translates raw problem inputs into structured representations.
Each translator handles one problem domain and populates the corresponding
representation in the Problem object.
"""

from __future__ import annotations
import re
import ast
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
from typing import Any, Dict, List, Optional, Tuple

from core.problem import (
    Problem, ProblemType,
    SymbolicRepresentation, ConstraintRepresentation,
    GraphRepresentation, LinearProgramRepresentation,
)

_TRANSFORMS = standard_transformations + (implicit_multiplication_application,)


# ─── Base class ───────────────────────────────────────────────────────────────

class BaseTranslator:
    """All translators inherit from this."""
    problem_types: List[ProblemType] = []

    def can_translate(self, problem: Problem) -> bool:
        return problem.problem_type in self.problem_types

    def translate(self, problem: Problem) -> Problem:
        raise NotImplementedError


# ─── Math Translator ──────────────────────────────────────────────────────────

class MathTranslator(BaseTranslator):
    """
    Handles: arithmetic, algebra, linear systems, calculus.
    Parses expressions via SymPy and builds SymbolicRepresentation.
    """
    problem_types = [
        ProblemType.MATH_ARITHMETIC,
        ProblemType.MATH_ALGEBRA,
        ProblemType.MATH_CALCULUS,
        ProblemType.MATH_LINEAR_SYSTEM,
    ]

    def translate(self, problem: Problem) -> Problem:
        text = problem.raw_input.strip()
        variables: List[sp.Symbol] = []
        expressions: List[Any] = []
        equalities: List[Any] = []
        inequalities: List[Any] = []

        # Detect and parse equations like "2x + 3 = 7" or "x**2 - 5x + 6 = 0"
        eq_parts = re.split(r'(=)', text)
        if '=' in text and len(eq_parts) >= 3:
            lhs_str = ''.join(eq_parts[:eq_parts.index('=')])
            rhs_str = ''.join(eq_parts[eq_parts.index('=')+1:])
            try:
                lhs = parse_expr(lhs_str.strip(), transformations=_TRANSFORMS)
                rhs = parse_expr(rhs_str.strip(), transformations=_TRANSFORMS)
                variables = sorted(lhs.free_symbols | rhs.free_symbols, key=str)
                equalities.append(sp.Eq(lhs, rhs))
                expressions.extend([lhs, rhs])
            except Exception:
                pass
        else:
            # Pure expression (evaluate / simplify)
            try:
                expr = parse_expr(text, transformations=_TRANSFORMS)
                variables = sorted(expr.free_symbols, key=str)
                expressions.append(expr)
            except Exception:
                pass

        # Multi-equation system: detect "\n" or ";" separated lines
        if not equalities and (';' in text or '\n' in text):
            lines = re.split(r'[;\n]+', text)
            for line in lines:
                line = line.strip()
                if '=' in line:
                    parts = line.split('=', 1)
                    try:
                        lhs = parse_expr(parts[0].strip(), transformations=_TRANSFORMS)
                        rhs = parse_expr(parts[1].strip(), transformations=_TRANSFORMS)
                        equalities.append(sp.Eq(lhs, rhs))
                        variables += list(lhs.free_symbols | rhs.free_symbols)
                    except Exception:
                        pass
            variables = sorted(set(variables), key=str)

        problem.symbolic = SymbolicRepresentation(
            expressions=expressions,
            variables=variables,
            equalities=equalities,
            inequalities=inequalities,
        )
        return problem


# ─── Logic / CSP Translator ───────────────────────────────────────────────────

class LogicTranslator(BaseTranslator):
    """
    Translates propositional logic and constraint satisfaction problems.
    Builds a ConstraintRepresentation.

    Supported input formats:
    - Propositional: "A AND B OR NOT C"
    - CSP block:
        variables: x(0,10), y(0,10)
        constraints: x + y == 10; x > 3; y < 8
    """
    problem_types = [
        ProblemType.LOGIC_PROPOSITIONAL,
        ProblemType.LOGIC_CONSTRAINT,
    ]

    def translate(self, problem: Problem) -> Problem:
        text = problem.raw_input.strip()

        if 'variables:' in text.lower():
            # CSP format
            var_dict: Dict[str, Tuple[Any, Any]] = {}
            constraint_strs: List[str] = []

            var_match = re.search(r'variables:\s*([^\n]+)', text, re.IGNORECASE)
            if var_match:
                for token in var_match.group(1).split(','):
                    token = token.strip()
                    m = re.match(r'(\w+)\s*\(([-\d.]+)\s*,\s*([-\d.]+)\)', token)
                    if m:
                        var_dict[m.group(1)] = (float(m.group(2)), float(m.group(3)))

            con_match = re.search(r'constraints:\s*(.+)', text, re.IGNORECASE | re.DOTALL)
            if con_match:
                constraint_strs = [c.strip() for c in re.split(r'[;\n]+', con_match.group(1)) if c.strip()]

            problem.constraints = ConstraintRepresentation(
                variables=var_dict,
                constraints=constraint_strs,
            )
        else:
            # Propositional logic — build truth-table style representation
            symbols_found = sorted(set(re.findall(r'\b([A-Z])\b', text)))
            var_dict = {s: (0, 1) for s in symbols_found}
            problem.constraints = ConstraintRepresentation(
                variables=var_dict,
                constraints=[text],
            )
            problem.metadata['propositional_formula'] = text

        return problem


# ─── Optimization Translator ──────────────────────────────────────────────────

class OptimizationTranslator(BaseTranslator):
    """
    Builds LinearProgramRepresentation from natural LP descriptions.

    Example input (LP):
        minimize: 2x + 3y
        subject to:
          x + y <= 10
          x >= 2
          y >= 1
    """
    problem_types = [
        ProblemType.OPTIMIZATION_LP,
        ProblemType.OPTIMIZATION_ILP,
        ProblemType.OPTIMIZATION_NLP,
    ]

    def translate(self, problem: Problem) -> Problem:
        text = problem.raw_input.strip()
        sense = "minimize" if re.search(r'minimiz', text, re.I) else "maximize"

        # Extract objective
        obj_match = re.search(r'(?:minimize|maximize|min|max):\s*([^\n]+)', text, re.I)
        obj_str = obj_match.group(1).strip() if obj_match else ""

        # Extract constraints
        constraints_section = re.split(r'subject\s+to[:\s]*|s\.t\.[:\s]*|constraints?[:\s]*', text, flags=re.I)
        constraint_lines = []
        if len(constraints_section) > 1:
            for line in re.split(r'[\n;]', constraints_section[1]):
                line = line.strip()
                if line and re.search(r'[<>=]', line):
                    constraint_lines.append(line)

        # Parse via SymPy to get coefficients
        all_vars: List[str] = []
        obj_expr = None
        if obj_str:
            try:
                obj_expr = parse_expr(obj_str, transformations=_TRANSFORMS)
                all_vars = sorted([str(s) for s in obj_expr.free_symbols])
            except Exception:
                pass

        sym_vars = {v: sp.Symbol(v) for v in all_vars}

        def _coeffs(expr_str: str) -> List[float]:
            try:
                e = parse_expr(expr_str, local_dict=sym_vars, transformations=_TRANSFORMS)
                return [float(e.coeff(sym_vars[v])) for v in all_vars]
            except Exception:
                return [0.0] * len(all_vars)

        obj_coeffs = _coeffs(obj_str) if obj_str else []

        ineq_lhs: List[List[float]] = []
        ineq_rhs: List[float] = []
        eq_lhs: List[List[float]] = []
        eq_rhs: List[float] = []

        for line in constraint_lines:
            if '<=' in line:
                lhs_s, rhs_s = line.split('<=', 1)
                ineq_lhs.append(_coeffs(lhs_s.strip()))
                try:
                    ineq_rhs.append(float(rhs_s.strip()))
                except ValueError:
                    ineq_rhs.append(0.0)
            elif '>=' in line:
                lhs_s, rhs_s = line.split('>=', 1)
                ineq_lhs.append([-c for c in _coeffs(lhs_s.strip())])
                try:
                    ineq_rhs.append(-float(rhs_s.strip()))
                except ValueError:
                    ineq_rhs.append(0.0)
            elif '==' in line or (line.count('=') == 1 and '<' not in line and '>' not in line):
                sep = '==' if '==' in line else '='
                lhs_s, rhs_s = line.split(sep, 1)
                eq_lhs.append(_coeffs(lhs_s.strip()))
                try:
                    eq_rhs.append(float(rhs_s.strip()))
                except ValueError:
                    eq_rhs.append(0.0)

        bounds = [(0.0, None) for _ in all_vars]

        problem.lp = LinearProgramRepresentation(
            objective_coeffs=obj_coeffs,
            objective_sense=sense,
            variable_names=all_vars,
            ineq_lhs=ineq_lhs,
            ineq_rhs=ineq_rhs,
            eq_lhs=eq_lhs,
            eq_rhs=eq_rhs,
            bounds=bounds,
            integer_vars=all_vars if problem.problem_type == ProblemType.OPTIMIZATION_ILP else [],
        )
        return problem


# ─── Graph / Planning Translator ─────────────────────────────────────────────

class GraphTranslator(BaseTranslator):
    """
    Builds GraphRepresentation from adjacency descriptions or edge lists.

    Supported formats:
    - Edge list: "A-B:5, B-C:3, A-C:10"
    - Adjacency dict: "A: B(5) C(10); B: C(3)"
    - TSP cities: "cities: A B C D  distances: A-B:10 B-C:15 ..."
    """
    problem_types = [
        ProblemType.PLANNING_SHORTEST_PATH,
        ProblemType.PLANNING_TSP,
        ProblemType.PLANNING_SCHEDULING,
        ProblemType.GRAPH_ANALYSIS,
    ]

    def translate(self, problem: Problem) -> Problem:
        text = problem.raw_input.strip()
        nodes: List[Any] = []
        edges: List[Tuple[Any, Any, float]] = []
        source: Optional[Any] = None
        sink: Optional[Any] = None

        # Parse source/sink hints
        src_m = re.search(r'from\s+(\w+)\s+to\s+(\w+)', text, re.I)
        if src_m:
            source, sink = src_m.group(1), src_m.group(2)

        # Parse edge list "A-B:5" or "A->B:5" or "A B 5"
        edge_pattern = re.compile(
            r'(\w+)\s*[->=]+\s*(\w+)\s*[:\s]\s*([\d.]+)'
        )
        for m in edge_pattern.finditer(text):
            u, v, w = m.group(1), m.group(2), float(m.group(3))
            edges.append((u, v, w))
            nodes.extend([u, v])

        # Deduplicate
        nodes = list(dict.fromkeys(nodes))
        if not source and nodes:
            source = nodes[0]
        if not sink and len(nodes) > 1:
            sink = nodes[-1]

        directed = '->' in text or 'directed' in text.lower()

        problem.graph = GraphRepresentation(
            nodes=nodes,
            edges=edges,
            directed=directed,
            source=source,
            sink=sink,
        )
        return problem


# ─── Registry ─────────────────────────────────────────────────────────────────

TRANSLATORS: List[BaseTranslator] = [
    MathTranslator(),
    LogicTranslator(),
    OptimizationTranslator(),
    GraphTranslator(),
]


def translate_problem(problem: Problem) -> Problem:
    """Apply all applicable translators to a problem."""
    for translator in TRANSLATORS:
        if translator.can_translate(problem):
            problem = translator.translate(problem)
    return problem

