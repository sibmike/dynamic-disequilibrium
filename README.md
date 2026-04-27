# Dynamic Disequilibrium

**Bubbles don't need biased agents.**

This repository accompanies the paper *Estimated Dynamic Equilibrium
Model: Supply and Demand as a Sample Path of a Stochastic Process*
(forthcoming on arXiv). It contains the LaTeX source, a Python/Mesa
implementation that reproduces every figure from a clean checkout, a
30-cell parameter sweep showing the result is not a corner case, and
the original 2018 NetLogo prototype this work supersedes.

![Run 6 — an exponential bubble emerging from agents whose individual
estimation errors are exactly zero-mean.](paper/figures/fig6_bubble.png)

The figure above is a 3000-tick simulation of a real-estate market
with 20 buyers and 20 sellers. Every agent's home valuation has a
uniform random error with mean exactly zero. There is no behavioural
bias, no animal spirits, no irrational exuberance. After 150 epochs
of bidding, the realised market price is **421× the home's fair
value.** With the same parameters and a population balancer that
adds sellers when prices rise (textbook market discipline), the
bubble flattens but does not disappear: terminal value is still
~4×.

## The mechanism

Each seller picks the *maximum* bid received from the buyers who
visited them. The maximum of `n` zero-mean random draws is, in
expectation, strictly above their mean — by `σ(n−1)/(n+1)` for
uniform errors with dispersion `σ`, a closed-form bound derived in
[§3.7 of the paper](paper/sections/03_framework.tex). Each epoch's
clearing prices feed forward into the next epoch's anchor value.
Compound that across 150 epochs and you get exponential drift with
no behavioural assumption required.

We sweep the parameters: 5 balancer settings × 6 estimation-error
levels × 5 random seeds, 1500 ticks each. **Every single cell
produces price drift above the textbook equilibrium. 43% produce
10× growth or more.** The order-statistic bubble is not a corner
case.

![Sensitivity heatmap: terminal value/true ratio over a 5×6 (Cb,
σ) grid.](paper/figures/fig9_sensitivity.png)

## Why this matters for ML valuation

A machine-learning real-estate valuation algorithm trained on
historical clearing prices is not fitting fair value. By
construction, it is fitting the upper-order statistic of plausible
sale prices — the maximum of the relevant noisy estimates. Deployed
at scale, such an algorithm functions as a positively-biased point
estimator that provides the market with a coordinating signal
pulling realised winning bids further upward, feeding back into the
next training cycle. The [Zillow Offers wind-down
(2021)](https://investors.zillowgroup.com/investors/news-and-events/news/news-details/2021/Zillow-Group-Reports-Third-Quarter-2021-Financial-Results-Announces-Wind-Down-of-Zillow-Offers/default.aspx)
is the most prominent recent example of a clearing-price-anchored
valuation system at scale incurring substantial losses.

We do not advance the model as the explanation for that specific
event. We do advance the framework as a generative reason to build
selection-aware valuation procedures (predict the median, not the
mean of plausible sale prices; or use a censored-data likelihood
that accounts for the offer-acceptance threshold) rather than treat
historical sale prices as unbiased training data.

## See it for yourself

```bash
git clone https://github.com/sibmike/dynamic-disequilibrium
cd dynamic-disequilibrium/python_simulation
pip install -e .
python experiments/run6_bubble.py
```

About 30 seconds. The bubble figure lands at
`paper/figures/fig6_bubble.pdf`. For the full eight-experiment
regime survey plus the 30-cell sensitivity sweep (≈25 min total),
run every script in `experiments/`. Each writes a publication-grade
PDF figure and a Parquet dataset of every per-tick model reporter.

## What else is in this repository

| Path | Purpose |
|---|---|
| [`paper/`](paper/) | LaTeX source. 28 pages, 9 figures, CC-BY-4.0. Build with `cd paper && bash build.sh` (xelatex × 3 + bibtex). |
| [`arxiv/`](arxiv/) | Self-contained arXiv submission package — sources, figures, and the upload `.zip`, ready to upload. |
| [`python_simulation/`](python_simulation/) | Mesa implementation, MIT-licensed. 42 pytest unit tests. |
| [`drafts/`](drafts/) | Two 2018 SJSU markdown drafts plus the legacy NetLogo prototype that seeded this work, preserved as historical record. |

## The six regimes

The same agent ruleset, varied along three parameters (estimation-
error scale, seller patience, balancer coefficient), produces six
qualitatively distinct steady-state regimes:

| Regime | What you see | Where in the paper |
|---|---|---|
| Band-stable | Price hovers within ±10% of the textbook equilibrium | [Run 1](paper/figures/fig1_stable.png) |
| Business cycle | Endogenous oscillations from valuation noise alone | [Run 2](paper/figures/fig2_high_error.png) |
| Persistent overshoot | Price stable ~14% above equilibrium because sellers wait | [Run 3](paper/figures/fig3_patience.png) |
| Persistent undershoot | Price stable ~18% below equilibrium because buyers and sellers don't meet | [Run 4](paper/figures/fig4_low_density.png) |
| Constant transition | Repeated shocks; price never settles | [Run 5](paper/figures/fig5_shock.png) |
| Runaway bubble | Exponential drift from order-statistic feedback | [Runs 6–8](paper/figures/fig7_balancer_sweep.png) |

Every figure in the table above was regenerated from a clean
checkout by the corresponding script in
[`python_simulation/experiments/`](python_simulation/experiments/).

## Citation

```bibtex
@misc{arbuzov2026dynamic,
  author = {Arbuzov, Mikhail},
  title  = {{Estimated Dynamic Equilibrium Model:
            Supply and Demand as a Sample Path of a Stochastic Process}},
  year   = {2026},
  note   = {arXiv preprint, forthcoming.}
}
```

For citing the simulation code, see
[`python_simulation/CITATION.cff`](python_simulation/CITATION.cff).

## License

- Paper (`paper/`, `arxiv/`): CC-BY-4.0
- Code (`python_simulation/`): MIT (see [`python_simulation/LICENSE`](python_simulation/LICENSE))
- 2018 drafts (`drafts/`): preserved verbatim; original SJSU working papers

## Acknowledgements

Thanks to Justin Rietz for comments on the 2018 NetLogo prototype
that seeded the present framework.
