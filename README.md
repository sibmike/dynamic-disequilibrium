# Estimated Dynamic Equilibrium Model — Paper & Simulation

Workspace for a publishable paper on agent-based modelling of real-estate
markets with heterogeneous, error-prone agent valuations. Replaces the earlier
NetLogo work in
[sibmike/netlogo-realestate-simulations](https://github.com/sibmike/netlogo-realestate-simulations).

## Layout

| Path                  | Purpose |
|-----------------------|---------|
| `paper/`              | LaTeX source for the arXiv preprint |
| `python_simulation/`  | Mesa implementation reproducing every figure in the paper |
| `drafts/`             | Original 2018 SJSU markdown drafts and the EDEM contest PDF (archival) |

## Build the paper

```bash
cd paper && bash build.sh   # xelatex + bibtex + xelatex + xelatex
```

Outputs `paper/main.pdf`.

## Reproduce the simulations

```bash
cd python_simulation
pip install -e ".[dev]"
pytest
for f in experiments/run*.py; do python "$f"; done   # writes PDFs to ../paper/figures/
```

## Status

Session 1 ✓ — directory layout, drafts archived, LaTeX skeleton with
Introduction and Background sections drafted, Python package scaffolding.

Subsequent sessions per the build plan in
`~/.claude/plans/we-need-to-create-serene-lark.md`.
