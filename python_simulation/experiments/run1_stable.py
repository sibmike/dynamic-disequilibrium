"""Run 1 — Stable equilibrium under favorable conditions (Doc 1, Fig. 1).

Q_s = 0.5 * p, Q_d = 100 - 0.5 * p, equilibrium p* = 100, q* = 50.
Precision epsilon ~ U[0, 5], patience ~ U[0, 50], balance period 100.

Doc 1 reports max +6.2% / min -4.9% deviation over 100,000 ticks.
We run a shorter-but-replicated experiment (multiple seeds, fewer ticks)
that supports the same qualitative claim with quantified seed variance.
"""

from __future__ import annotations

import json
from pathlib import Path

# bootstrap the package without an editable install
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from edem.de_model import DEModel  # noqa: E402

from experiments._runner import (  # noqa: E402
    DATA_DIR,
    Experiment,
    FIG_DIR,
    deviation_summary,
    plot_market_price,
    run_seeds,
    save_parquet,
    stack_results,
    write_summary_md,
)


def main() -> None:
    exp = Experiment(
        name="run1_stable",
        model_factory=DEModel,
        model_kwargs=dict(
            init_epsilon=5.0,
            init_patience=50,
            balance_period=100,
        ),
        n_ticks=20_000,
        n_seeds=10,
    )
    print(f"Running {exp.name}: n_ticks={exp.n_ticks}, n_seeds={exp.n_seeds}")
    results = run_seeds(exp)

    plot_market_price(
        results,
        title="Run 1 — Stable equilibrium (low valuation error, moderate patience)",
        out_path=FIG_DIR / "fig1_stable",
        equi_price=100.0,
    )

    save_parquet(stack_results(results), DATA_DIR / "run1_stable.parquet")

    summary = deviation_summary(results, equi_price=100.0, warmup=500)
    write_summary_md(summary, FIG_DIR / "run1_stable_summary.md")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
