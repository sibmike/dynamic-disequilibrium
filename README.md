# Estimated Dynamic Equilibrium Model

Repository for the paper

> Arbuzov, M. *Estimated Dynamic Equilibrium Model: Supply and Demand
> as a Sample Path of a Stochastic Process.* Department of Economics,
> San José State University, 2026.
> [arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) *(forthcoming)*.

This repository supersedes the 2018 NetLogo prototype at
[`sibmike/netlogo-realestate-simulations`](https://github.com/sibmike/netlogo-realestate-simulations),
which held only the original `.nlogo` file. The new name reflects
what the model actually shows: under heterogeneous, error-prone
valuations the textbook ``dynamic equilibrium'' is in fact a
non-generic state, and realised markets spend their time in one of
six identifiable disequilibrium regimes. This repository now holds
the EDEM theoretical framework, a Python/Mesa implementation that
replaces the NetLogo prototype, and the historical NetLogo source
preserved alongside the new code.

## Layout

| Path | Purpose |
|---|---|
| [`paper/`](paper/) | LaTeX source for the arXiv preprint (CC-BY-4.0). 28 pages, 9 figures. |
| [`arxiv/`](arxiv/) | Self-contained arXiv submission package — sources, figures, and the upload `.zip`. |
| [`python_simulation/`](python_simulation/) | Mesa implementation reproducing every figure (MIT). 42 pytest unit tests. |
| [`drafts/`](drafts/) | Two 2018 SJSU markdown drafts plus the legacy NetLogo prototype. |

## Reproduce the paper end-to-end

```bash
# 1. install the Python deps
cd python_simulation && pip install -e ".[dev]"

# 2. regenerate every figure (runs ~25 minutes; Run 9 alone is ~4 minutes)
for f in experiments/run*.py; do python "$f"; done
cd ..

# 3. build the PDF (xelatex + bibtex + xelatex + xelatex)
cd paper && bash build.sh

# 4. (optional) repackage the arXiv zip
cd ../arxiv/edem && bash build.sh && bash pack.sh
```

## Tests

```bash
cd python_simulation && pytest
```

## Citation

See [`python_simulation/CITATION.cff`](python_simulation/CITATION.cff)
once the arXiv ID is assigned. In the meantime, cite the SJSU
working-paper drafts in [`drafts/`](drafts/).

## Acknowledgements

Thanks to Justin Rietz for comments on the original 2018 NetLogo
prototype that seeded the present framework.
