from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum


class ProblemType(Enum):
    UNKNOWN = "unknown"
    ARITHMETIC = "arithmetic"
    ALGEBRA = "algebra"
    CALCULUS = "calculus"
    LINEAR_PROGRAMMING = "linear_programming"
    GRAPH_THEORY = "graph_theory"
    LOGIC = "logic"
    CONSTRAINT_SATISFACTION = "constraint_satisfaction"
    SCHEDULING = "scheduling"
    ROUTING = "routing"
    SET_THEORY = "set_theory"
    PROBABILITY = "probability"
    STATISTICS = "statistics"


class RepresentationType(Enum):
    SYMBOLIC_EQUATION = "symbolic_equation"
    CONSTRAINT_SYSTEM = "constraint_system"
    GRAPH = "graph"
    LINEAR_PROGRAM = "linear_program"


@dataclass
class SymbolicRepresentation:
    expressions: List[Any]
    variables: List[Any]
    equalities: List[Any] = field(default_factory=list)
    inequalities: List[Any] = field(default_factory=list)
    objective: Optional[Any] = None


@dataclass
class ConstraintRepresentation:
    variables: Dict[str, Tuple[Any, Any]]
    constraints: List[str]
    raw_constraints: List[Any] = field(default_factory=list)
    domains: Dict[str, List[Any]] = field(default_factory=dict)


@dataclass
class GraphRepresentation:
    nodes: List[Any]
    edges: List[Tuple[Any, Any, float]]
    directed: bool = False
    source: Optional[Any] = None
    sink: Optional[Any] = None
    node_labels: Dict[Any, str] = field(default_factory=dict)


@dataclass
class LinearProgramRepresentation:
    objective_coeffs: List[float]
    objective_sense: str = "minimize"
    variable_names: List[str] = field(default_factory=list)
    ineq_lhs: List[List[float]] = field(default_factory=list)
    ineq_rhs: List[float] = field(default_factory=list)
    eq_lhs: List[List[float]] = field(default_factory=list)
    eq_rhs: List[float] = field(default_factory=list)
    bounds: List[Tuple[Optional[float], Optional[float]]] = field(default_factory=list)
    integer_vars: List[str] = field(default_factory=list)


@dataclass
class Problem:
    raw_input: str
    problem_type: ProblemType = ProblemType.UNKNOWN
    metadata: Dict[str, Any] = field(default_factory=dict)
    symbolic: Optional[SymbolicRepresentation] = None
    constraints: Optional[ConstraintRepresentation] = None
    graph: Optional[GraphRepresentation] = None
    lp: Optional[LinearProgramRepresentation] = None
    solution: Optional["Solution"] = None

    def has_representation(self, rep: RepresentationType) -> bool:
        return {
            RepresentationType.SYMBOLIC_EQUATION: self.symbolic is not None,
            RepresentationType.CONSTRAINT_SYSTEM: self.constraints is not None,
            RepresentationType.GRAPH:             self.graph is not None,
            RepresentationType.LINEAR_PROGRAM:    self.lp is not None,
        }[rep]


@dataclass
class Solution:
    problem_type: ProblemType
    representation_used: RepresentationType
    result: Any
    steps: List[str] = field(default_factory=list)
    numeric_value: Optional[float] = None
    variables: Dict[str, Any] = field(default_factory=dict)
    status: str = "solved"
    confidence: float = 1.0

    def __str__(self) -> str:
        lines = [f"Result: {self.result}"]
        if self.variables:
            lines.append(f"Variables: {self.variables}")
        if self.steps:
            lines.append("Steps:")
            for i, step in enumerate(self.steps, 1):
                lines.append(f"  {i}. {step}")
        return "\n".join(lines)
