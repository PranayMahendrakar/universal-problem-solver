# 🧠 Universal Problem Solver Engine

> **Translate any problem into solvable representations, then solve with the best algorithm.**

A general reasoning system that accepts natural language problems across multiple domains — math, logic, optimization, graph theory, and planning — automatically classifies them, converts them to formal mathematical representations, and applies the most suitable solver.

---

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/PranayMahendrakar/universal-problem-solver.git
cd universal-problem-solver

# Install dependencies
pip install -r requirements.txt

# Run the Streamlit app
streamlit run app.py

# Or use the engine directly in Python
python engine.py
```

---

## 🏗 Architecture

```
Input (natural language)
        |
        v
  ProblemClassifier          <- regex pattern matching → ProblemType
        |
        v
  ProblemTranslator          <- converts text → formal representation
        |                       (SymbolicRepresentation | GraphRepresentation |
        |                        ConstraintRepresentation | LinearProgramRepresentation)
        v
  Solver Selection           <- route to best solver based on ProblemType
        |
    +---+---+---+
    |   |   |   |
  Sym Graph LP  CSP          <- SymPy | NetworkX | SciPy/HiGHS | SymPy Logic
    |   |   |   |
    +---+---+---+
        |
        v
  Solution (result + steps + variables)
```

---

## 📁 Project Structure

```
universal-problem-solver/
|-- app.py                  # Streamlit UI
|-- engine.py               # Orchestrator: classify -> translate -> solve
|-- requirements.txt
|-- core/
    |-- __init__.py         # Package exports
    |-- problem.py          # Data models: Problem, Solution, ProblemType, Representations
    |-- classifier.py       # Rule-based problem type detector (regex patterns)
    |-- translator.py       # Converts text to formal math representations
    |-- solvers.py          # 4 solver engines (Symbolic, Graph, LP, Logic/CSP)
```

---

## 🎯 Supported Problem Types

| Problem Type | Example | Solver Used |
|---|---|---|
| Arithmetic | `2 + 2 * 3` | SymPy |
| Algebra | `solve for x: 2x + 5 = 11` | SymPy |
| Calculus | `differentiate x^3 + 2x` | SymPy |
| Linear Programming | `maximize 3x + 2y s.t. x+y<=4` | SciPy HiGHS |
| Graph Theory | `find minimum spanning tree` | NetworkX |
| Routing | `shortest path from A to D` | NetworkX Dijkstra |
| Scheduling | `assign 3 jobs to 2 machines` | SciPy LP |
| Logic | `True AND (False OR True)` | SymPy Logic |
| Constraint Satisfaction | `n-queens, sudoku` | CSP Solver |
| Set Theory | `union and intersection of sets` | Logic Solver |
| Probability | `P(rolling 6 on fair die)` | Symbolic |
| Statistics | `mean, variance, regression` | Symbolic |

---

## 🔧 Tech Stack

| Library | Purpose |
|---|---|
| **SymPy** | Symbolic math: algebra, calculus, logic |
| **NetworkX** | Graph algorithms: shortest path, MST, flow |
| **SciPy** | Numerical optimization: linear programs |
| **PuLP** | Mixed-integer linear programming |
| **Streamlit** | Interactive web interface |
| **Plotly** | Visualization |

---

## 💡 Usage Examples

### Python API

```python
from engine import solve

# Arithmetic
sol = solve("2 + 2 * 3")
print(sol.result)  # 8

# Algebra
sol = solve("solve for x: 2x + 5 = 11")
print(sol.result)  # {x: 3}

# Calculus
sol = solve("differentiate x**3 + 2*x with respect to x")
print(sol.result)  # 3*x**2 + 2

# Linear Programming
sol = solve("maximize 3x + 2y subject to x+y<=4, x>=0, y>=0")
print(sol.result)  # 12.0  (x=4, y=0)
print(sol.steps)   # step-by-step explanation
```

---

## 🖥 Streamlit UI Features

- Free-text problem input
- One-click example gallery (8 problem types)
- Auto-detected problem type badge
- Result + variable values display
- Step-by-step solution walkthrough
- Solve time metric

---

## 📄 License

MIT License — see [LICENSE](LICENSE)
