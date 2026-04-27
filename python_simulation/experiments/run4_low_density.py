"""Run 4 — Low agent density pushes price below equilibrium (Doc 1, Fig. 4).

Demand intercept is reduced by 50 (`Q_d = 50 - 0.5 p`), so the textbook
equilibrium is `(p*, q*) = (50, 25)`. With only ~25 sellers and ~25 buyers
on a 32x32 grid, buyers do not meet sellers often enough to drive enough
bidding pressure; sellers run out of patience and lower ask prices, so the
realised market price settles *below* the textbook equilibrium.

Doc 1 notes that increasing seller patience to 165 cancels this effect —
patience and density are partial substitutes, both proxying for time-on-
market. Run 5 illustrates the patience-recovery scenario.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

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
        name="run4_low_density",
        model_factory=DEModel,
        model_kwargs=dict(
            demand_intercept=50.0,  # shifted down by 50 from Run 1
            demand_slope=-0.5,
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
        title="Run 4 — Low agent density: market price settles below equilibrium",
        out_path=FIG_DIR / "fig4_low_density",
        equi_price=50.0,
    )

    save_parquet(stack_results(results), DATA_DIR / "run4_low_density.parquet")

    summary = deviation_summary(results, equi_price=50.0, warmup=500)
    write_summary_md(summary, FIG_DIR / "run4_low_density_summary.md")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
