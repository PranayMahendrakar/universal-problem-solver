import re
from typing import List, Tuple
from .problem import ProblemType


class ProblemClassifier:
    """Rule-based classifier that detects problem types from natural language."""

    PATTERNS: List[Tuple[ProblemType, List[str]]] = [
        (ProblemType.CALCULUS, [
            r"\bderivative\b", r"\bintegral\b", r"\bdifferentiate\b",
            r"\bd/dx\b", r"\blimit\b", r"\bdy/dx\b", r"\bintegrate\b"
        ]),
        (ProblemType.LINEAR_PROGRAMMING, [
            r"\bmaximize\b", r"\bminimize\b", r"\bsubject to\b",
            r"\blinear program\b", r"\boptimal\b.*\bconstraint\b"
        ]),
        (ProblemType.GRAPH_THEORY, [
            r"\bshortest path\b", r"\bminimum spanning tree\b",
            r"\bmax flow\b", r"\bgraph\b.*\bnode\b", r"\bvertex\b",
            r"\bedge\b.*\bweight\b", r"\bdijkstra\b"
        ]),
        (ProblemType.ROUTING, [
            r"\btraveling salesman\b", r"\btsp\b", r"\broute\b.*\bcity\b",
            r"\bvisit.*\bcity\b", r"\bdelivery route\b"
        ]),
        (ProblemType.SCHEDULING, [
            r"\bschedule\b", r"\bjob\b.*\bmachine\b", r"\btask\b.*\bdeadline\b",
            r"\bshift\b.*\bworker\b", r"\bassign\b.*\btime slot\b"
        ]),
        (ProblemType.CONSTRAINT_SATISFACTION, [
            r"\bconstraint\b", r"\bsatisfy\b", r"\bcsp\b",
            r"\bn-queens\b", r"\bsudoku\b", r"\bcoloring\b"
        ]),
        (ProblemType.LOGIC, [
            r"\bif.*then\b", r"\ball.*are\b", r"\bsome.*are\b",
            r"\bpropositional\b", r"\bboolean\b", r"\btrue or false\b",
            r"\bimplies\b", r"\blogical\b"
        ]),
        (ProblemType.SET_THEORY, [
            r"\bunion\b", r"\bintersection\b", r"\bsubset\b",
            r"\bcomplement\b.*set\b", r"\bvenn\b"
        ]),
        (ProblemType.PROBABILITY, [
            r"\bprobability\b", r"\blikelihood\b", r"\brandom variable\b",
            r"\bbayes\b", r"\bexpected value\b", r"\bP\(\b"
        ]),
        (ProblemType.STATISTICS, [
            r"\bmean\b", r"\bmedian\b", r"\bstandard deviation\b",
            r"\bregression\b", r"\bcorrelation\b", r"\bvariance\b"
        ]),
        (ProblemType.ALGEBRA, [
            r"\bsolve for\b", r"\bequation\b", r"\bvariable\b",
            r"\bsimplify\b", r"\bfactor\b", r"\bquadratic\b",
            r"x\s*[+\-*/=]", r"\bpolynomial\b"
        ]),
        (ProblemType.ARITHMETIC, [
            r"\d+\s*[+\-*/]\s*\d+", r"\bsum\b", r"\bproduct\b",
            r"\bdivide\b", r"\bmultiply\b", r"\bsubtract\b", r"\badd\b"
        ]),
    ]

    def classify(self, problem_text: str) -> ProblemType:
        text = problem_text.lower()
        scores = {pt: 0 for pt in ProblemType}

        for prob_type, patterns in self.PATTERNS:
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    scores[prob_type] += 1

        best_type = max(scores, key=lambda k: scores[k])
        return best_type if scores[best_type] > 0 else ProblemType.UNKNOWN

    def classify_with_confidence(self, problem_text: str) -> Tuple[ProblemType, float]:
        text = problem_text.lower()
        scores = {pt: 0 for pt in ProblemType}
        total_patterns = sum(len(p) for _, p in self.PATTERNS)

        for prob_type, patterns in self.PATTERNS:
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    scores[prob_type] += 1

        best_type = max(scores, key=lambda k: scores[k])
        max_score = scores[best_type]

        if max_score == 0:
            return ProblemType.UNKNOWN, 0.0

        max_possible = max(len(p) for _, p in self.PATTERNS)
        confidence = min(1.0, max_score / max_possible)
        return best_type, confidence
