"""NETWORK MINDS - Flask backend (Network Influence Propagation, C8).
Run:  pip install flask numpy sympy  &&  python app.py   ->  http://127.0.0.1:5000
All numerical results shown by the frontend come from this file.
"""
from flask import Flask, jsonify, request, send_from_directory
import numpy as np
import sympy as sp

app = Flask(__name__, static_folder="static")
NAMES = ["Alice", "Bob", "Charlie", "David", "Eve"]


@app.get("/")
def home():
    return send_from_directory("static", "index.html")


@app.post("/api/simulate")
def simulate():
    data = request.get_json(force=True)
    try:
        A = np.array(data["matrix"], dtype=float)
        x0 = np.array(data["opinions"], dtype=float)
        rounds = int(data["rounds"])
    except (KeyError, ValueError, TypeError):
        return jsonify(error="Invalid request body"), 400

    # Server-side validation (mirrors the frontend checks)
    if A.shape != (5, 5) or x0.shape != (5,):
        return jsonify(error="Matrix must be 5x5 and opinions must have 5 values"), 400
    if (A < 0).any():
        return jsonify(error="Matrix values must be non-negative"), 400
    bad = np.where(~np.isclose(A.sum(axis=1), 1.0, atol=0.01))[0]
    if bad.size:
        return jsonify(error=f"Row {bad[0] + 1} must sum to 1"), 400
    if rounds < 1 or rounds > 500:
        return jsonify(error="Rounds must be between 1 and 500"), 400

    # x(n+1) = A x(n)
    history = [x0.tolist()]
    x = x0.copy()
    for _ in range(rounds):
        x = A @ x
        history.append(x.tolist())

    # Long-term influence = left eigenvector of A for eigenvalue 1 (v^T A = v^T, sum v = 1)
    w, V = np.linalg.eig(A.T)
    v = np.abs(V[:, np.argmin(np.abs(w - 1))].real)
    v = v / v.sum()
    consensus = float(v @ x0)

    # Cayley-Hamilton: p(lambda) = det(lambda I - A); p(A) = 0
    coeffs = np.poly(A).tolist()  # [1, c1, ..., c5]
    p_of_A = sum(c * np.linalg.matrix_power(A, 5 - k) for k, c in enumerate(coeffs))
    lam = sp.symbols("lambda")
    poly_text = str(sp.Poly([round(c, 6) for c in coeffs], lam).as_expr())

    # Aⁿ itself (computed directly) and its distance from the rank-one limit 1 v^T
    An = np.linalg.matrix_power(A, rounds)
    gap = float(np.abs(An - np.outer(np.ones(5), v)).max())
    eig_mod = sorted(np.abs(w).tolist(), reverse=True)

    return jsonify(
        names=NAMES,
        final_opinions=history[-1],
        history=history,
        influence=v.tolist(),
        most_influential=NAMES[int(np.argmax(v))],
        consensus=consensus,
        spread=float(max(history[-1]) - min(history[-1])),
        converging=bool(eig_mod[1] < 1 - 1e-9),
        char_poly=coeffs,
        char_poly_text=poly_text,
        cayley_hamilton_residual=float(np.abs(p_of_A).max()),
        A_power=An.tolist(),
        limit_gap=gap,
        second_eigenvalue_modulus=float(eig_mod[1]),
    )


if __name__ == "__main__":
    app.run(debug=True)
