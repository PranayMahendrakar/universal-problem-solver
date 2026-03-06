import streamlit as st
import time
from engine import UniversalProblemSolverEngine
from core.problem import ProblemType

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Universal Problem Solver",
    page_icon="🧠",
    layout="wide",
)

# ── Singleton engine ─────────────────────────────────────────────────────────
@st.cache_resource
def get_engine():
    return UniversalProblemSolverEngine()


engine = get_engine()

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🧠 Problem Solver")
    st.markdown("---")
    st.subheader("How it works")
    st.markdown(
        "1. **Classify** — detect the problem type\n"
        "2. **Translate** — convert to math representation\n"
        "3. **Solve** — apply the best algorithm\n"
        "4. **Explain** — show step-by-step solution"
    )
    st.markdown("---")
    st.subheader("Supported Types")
    types = [
        ("Arithmetic", "2 + 2 * 3"),
        ("Algebra", "solve for x: 2x + 5 = 11"),
        ("Calculus", "differentiate x^3 + 2x with respect to x"),
        ("Linear Programming", "maximize 3x + 2y subject to x+y<=4, x>=0, y>=0"),
        ("Graph / Routing", "shortest path from A to D in graph"),
        ("Logic", "p AND (q OR NOT p)"),
        ("Statistics", "mean of 1,2,3,4,5"),
    ]
    for name, _ in types:
        st.markdown(f"- {name}")
# ── Main area ────────────────────────────────────────────────────────────────
st.title("🧠 Universal Problem Solver Engine")
st.markdown(
    "**Translate any problem into solvable representations, then solve with the best algorithm.**"
)

# ── Example gallery ──────────────────────────────────────────────────────────
with st.expander("💡 Example Problems (click to load)", expanded=False):
    examples = [
        ("Arithmetic", "2 + 2 * 3"),
        ("Algebra", "solve for x: 2x + 5 = 11"),
        ("Calculus (derivative)", "differentiate x**3 + 2*x with respect to x"),
        ("Calculus (integral)", "integrate x**2 with respect to x"),
        ("Linear Programming", "maximize 3x + 2y subject to x+y<=4, x>=0, y>=0"),
        ("Graph Theory", "find shortest path in weighted graph"),
        ("Logic", "True AND (False OR True)"),
        ("Probability", "probability of rolling a 6 on a fair die"),
    ]
    cols = st.columns(4)
    for i, (name, ex) in enumerate(examples):
        if cols[i % 4].button(name, key=f"ex_{i}"):
            st.session_state["problem_input"] = ex

# ── Input ────────────────────────────────────────────────────────────────────
problem_text = st.text_area(
    "Enter your problem:",
    value=st.session_state.get("problem_input", ""),
    height=120,
    placeholder="e.g. solve for x: 3x - 7 = 14",
    key="problem_input",
)

col1, col2 = st.columns([1, 6])
solve_btn = col1.button("🚀 Solve", type="primary")
col2.button("🗑 Clear", on_click=lambda: st.session_state.update(problem_input=""))

# ── Solve ────────────────────────────────────────────────────────────────────
if solve_btn and problem_text.strip():
    with st.spinner("Thinking..."):
        t0 = time.time()
        try:
            solution = engine.solve(problem_text.strip())
            elapsed = time.time() - t0

            # ── Result card ──
            st.success(f"Solved in {elapsed:.2f}s")

            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Problem Type", solution.problem_type.value.replace("_", " ").title())
            with col_b:
                st.metric("Status", solution.status.upper())

            st.subheader("Result")
            st.code(str(solution.result), language="text")

            if solution.variables:
                st.subheader("Variables")
                st.json(solution.variables)

            if solution.steps:
                st.subheader("Step-by-Step Solution")
                for i, step in enumerate(solution.steps, 1):
                    st.markdown(f"**Step {i}:** {step}")

        except Exception as e:
            st.error(f"Error solving problem: {e}")

elif solve_btn:
    st.warning("Please enter a problem first.")

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "Built with Streamlit | SymPy | NetworkX | SciPy | PuLP"
)
