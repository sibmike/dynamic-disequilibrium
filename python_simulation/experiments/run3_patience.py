"""Run 3 — Patience pushes price above equilibrium (Doc 1, Fig. 3).

All Run 1 parameters except `init_patience`, which is doubled from 50 to 100.
Sellers stay on the market longer before lowering ask prices, so realised
sale prices drift upward; the higher price drives buyers away.

Doc 1 reports a stable state with market price ~10% above equilibrium and
demand ~20% below it.
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
        name="run3_patience",
        model_factory=DEModel,
        model_kwargs=dict(
            init_epsilon=5.0,
            init_patience=100,  # doubled from Run 1
            balance_period=100,
        ),
        n_ticks=20_000,
        n_seeds=10,
    )
    print(f"Running {exp.name}: n_ticks={exp.n_ticks}, n_seeds={exp.n_seeds}")
    results = run_seeds(exp)

    plot_market_price(
        results,
        title="Run 3 — Higher seller patience pushes price above equilibrium (init_patience=100)",
        out_path=FIG_DIR / "fig3_patience",
        equi_price=100.0,
    )

    save_parquet(stack_results(results), DATA_DIR / "run3_patience.parquet")

    summary = deviation_summary(results, equi_price=100.0, warmup=500)
    write_summary_md(summary, FIG_DIR / "run3_patience_summary.md")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
