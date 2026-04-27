# EDEM — Estimated Dynamic Equilibrium Model

Python/[Mesa](https://github.com/projectmesa/mesa) implementation of the
agent-based real-estate market model in:

> Arbuzov, M. *Estimated Dynamic Equilibrium Model: Supply and Demand
> as a Sample Path of a Stochastic Process.* Department of Economics,
> San José State University, 2026.
> [arXiv:XXXX.XXXXX](https://arxiv.org/abs/XXXX.XXXXX) *(forthcoming)*.

The package replaces the earlier NetLogo prototypes archived at
[sibmike/netlogo-realestate-simulations](https://github.com/sibmike/netlogo-realestate-simulations).
It reproduces every figure in the paper from a clean checkout in
about 25 minutes on a 2024-era laptop.

## What's in here

```
edem/                 # the model
  agents.py           # Buyer, Seller (mesa.Agent subclasses)
  home.py             # per-cell dataclass for home state
  clearing.py         # rolling market price + Cond. 2 acceptance rule
  balancer.py         # linear supply/demand rebalancer (DE)
  de_model.py         # Dynamic Equilibrium model
  edem_model.py       # speculative-market / EDEM model

experiments/          # one script per paper figure
  run1_stable.py            # Fig 1
  run2_high_error.py        # Fig 2
  run3_patience.py          # Fig 3
  run4_low_density.py       # Fig 4
  run5_shock.py             # Fig 5
  run6_bubble.py            # Fig 6
  run7_balancer_sweep.py    # Fig 7
  run8_double_exp.py        # Fig 8
  run9_sensitivity.py       # Fig 9 (parameter-grid heatmap)

tests/                # pytest unit tests for clearing, balancer,
                      # market price, shock hooks, and EDEM dynamics

notebooks/            # narrated walkthrough (forthcoming)
```

## Install

```bash
git clone https://github.com/sibmike/realestate-edem-python
cd realestate-edem-python/python_simulation
pip install -e ".[dev]"
```

Tested on Python 3.11+ with Mesa 3.5.

## Reproduce all paper figures

```bash
for f in experiments/run*.py; do python "$f"; done
```

Each script writes its figure as both PDF and PNG to `../paper/figures/`,
plus a Parquet dataset of all per-tick model reporters to
`../paper/figures/data/`. Total run time ~25 minutes; Run 9 (the
30-cell sensitivity grid) is the longest single script at ~4 minutes.

## Tests

```bash
pytest
```

42 unit tests cover the rolling market price, both Cond. 2 acceptance
rules, the linear and fractional balancers, the EDEM epoch-timing
trick, the $C_{b}$-sign inversion, and the population floor.

## Citing

If this code helps your research, please cite the paper (and, if
useful, the software via [`CITATION.cff`](CITATION.cff)).

## License

MIT (code; [`LICENSE`](LICENSE)). The accompanying paper is licensed
CC-BY-4.0.

## Acknowledgements

Thanks to Justin Rietz for comments on the original 2018 NetLogo
prototype (`SJSU - Disequilibria in markets`), which seeded the
present framework.
