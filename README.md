# NETWORK-MINDS
NETWORK MINDS
# Opinion Dynamics & Consensus in a Social Network
### Matrix Powers via the Cayley-Hamilton Theorem

A Google Colab notebook that models how opinions evolve in a small social network (5 people) using a row-stochastic influence matrix. It computes `A^n` with the **Cayley-Hamilton theorem**, simulates opinion convergence over discussion rounds, and finds each person's long-term influence using the left eigenvector of `A`.

---

## Table of Contents
1. [Overview](#overview)
2. [Mathematical Model](#mathematical-model)
3. [Notebook Structure](#notebook-structure)
4. [Requirements](#requirements)
5. [How to Run](#how-to-run)
6. [Configuration](#configuration)
7. [Outputs](#outputs)
8. [Assumptions & Limitations](#assumptions--limitations)
9. [Possible Extensions](#possible-extensions)

---

## Overview

Five individuals (Alice, Bob, Charlie, David, Eve) each hold a numerical opinion (0–100). In every round, each person updates their opinion to a weighted average of everyone's opinions, with weights given by how much they trust each other. This project answers:

- What does everyone think after `n` rounds? (computed via Cayley-Hamilton)
- Does the group reach consensus, and at what value?
- Who is the most influential person in the long run?

## Mathematical Model

**Graph & influence matrix.** The network is a directed graph `G = (V, E)` with a row-stochastic matrix `A ∈ R^{5×5}`:

- `A_ij ≥ 0` is the weight person *i* gives to person *j*'s opinion
- Each row sums to 1: `Σ_j A_ij = 1` for all `i`

**Opinion dynamics.**

```
x(n) = A x(n-1) = A^n x(0)
```

**Cayley-Hamilton.** Every matrix satisfies its own characteristic polynomial. For a 5×5 matrix:

```
A^5 + c4 A^4 + c3 A^3 + c2 A^2 + c1 A + c0 I = 0
```

so any power can be written as

```
A^n = α0 I + α1 A + α2 A^2 + α3 A^3 + α4 A^4
```

The coefficients `α_j` are found by solving, for each eigenvalue `λ_i` of `A`:

```
λ_i^n = Σ_{j=0}^{4} α_j λ_i^j
```

(For repeated eigenvalues, derivatives of both sides are used to get enough equations.)

**Consensus.** If `A` is irreducible and aperiodic (primitive), then

```
A^n → 1 vᵀ  as n → ∞
```

where `v` is the normalized left eigenvector for `λ = 1` (`vᵀA = vᵀ`, `Σ v_i = 1`). Then:

- `v` gives each person's steady-state influence (eigenvector centrality)
- Everyone's opinion converges to `x* = vᵀ x(0)`

## Notebook Structure

| Cell | Purpose |
|------|---------|
| **1. Imports & Setup** | Loads NumPy, SymPy, Matplotlib, Pandas; sets plot style |
| **2. Input Configuration** | Defines names, matrix `A`, initial opinions `x(0)`, target step `n`; validates that rows sum to 1 |
| **3. Mathematical Engine** | `matrix_power_cayley_hamilton()` computes `A^n` symbolically; simulates opinions for 30 rounds; computes the steady-state left eigenvector |
| **4. Output Display** | Prints C-H coefficients, `A^n`, opinions at step `n`, influence scores, and the consensus value |
| **5. Visual Charts** | Plots opinion trajectories and a bar chart of long-term influence |

## Requirements

- Python 3.8+
- `numpy`
- `sympy`
- `matplotlib`
- `pandas`

All are preinstalled in Google Colab. For a local setup:

```bash
pip install numpy sympy matplotlib pandas
```

> Note: Cell 2 uses `display()`, which is available in Jupyter/Colab. In a plain Python script, replace it with `print()`.

## How to Run

1. Open a new notebook at [colab.research.google.com](https://colab.research.google.com).
2. Copy each cell (1–5) into its own code cell, in order.
3. Run all cells (`Runtime → Run all`).

## Configuration

Edit these in **Cell 2**:

| Variable | Description | Default |
|----------|-------------|---------|
| `PERSON_NAMES` | Labels for the 5 individuals | Alice, Bob, Charlie, David, Eve |
| `A_MATRIX_DATA` | Row-stochastic influence matrix | Provided 5×5 example |
| `INITIAL_OPINIONS` | Starting opinions `x(0)` (0–100 scale) | `[85, 20, 60, 10, 95]` |
| `TARGET_STEPS_N` | Step `n` for the Cayley-Hamilton evaluation | `10` |

`max_rounds` (Cell 3, default `30`) controls the length of the simulation shown in the plot.

If you change `A`, keep every row summing to 1 (an assertion checks this). The consensus claim holds only if the new matrix is primitive; see below.

## Outputs

- **Cayley-Hamilton coefficients** `α0 … α4` for the chosen `n`
- **Matrix `A^n`** as a labeled table (the influence propagation matrix)
- **Opinions at step `n`** for each person
- **Steady-state influence scores** (percentages) and the most influential person
- **Theoretical consensus opinion** `vᵀ x(0)`
- **Two plots:**
  1. Opinion trajectories over discussion rounds, with the consensus line
  2. Bar chart of long-term influence per person

## Assumptions & Limitations

- **Primitivity.** The notebook states "Consensus Reached: YES" as a fixed message. This is valid for the default matrix (the trust graph is strongly connected and every person has positive self-weight, so it is irreducible and aperiodic). If you change `A`, verify this property yourself; the message does not check it.
- **Numerical precision.** The C-H routine passes floating-point entries to SymPy, so eigenvalues may be approximate and the symbolic solve can be slow or fragile, especially for larger `n` or matrices with repeated/complex eigenvalues. Converting entries to exact rationals (`sp.Rational`) is more robust.
- **Complex eigenvalues.** `A` is not symmetric, so eigenvalues can be complex. The code takes the real part of the `λ = 1` eigenvector, which is fine for that eigenvalue, but intermediate results may carry small imaginary residue.
- **Fixed model.** Weights are static and homogeneous over time (the classic DeGroot model); there is no stubbornness, noise, or changing trust.
- **Size.** The code is written for a 5×5 matrix, but the C-H function uses `A.shape[0]`, so it generalizes to other sizes.

## Possible Extensions

- Cross-check `A^n` from Cayley-Hamilton against `np.linalg.matrix_power`
- Add a primitivity check (e.g., `A^k > 0` for some `k`) before declaring consensus
- Visualize the trust network as a directed graph (e.g., with `networkx`)
- Measure the convergence rate using the second-largest eigenvalue modulus
- Explore stubborn agents or time-varying influence weights
