"""Run 2 — Imprecise valuations cause business cycles (Doc 1, Fig. 2).

Same supply/demand and patience as Run 1 — the only difference is that
maximum valuation error (`init_epsilon`) is increased from 5 to 25,
allowing some agents to over- or under-value a home by up to ~50%.

Doc 1 reports Run 2 over 100,000 ticks: max +41.0% / min -25.8%
deviation. The qualitative signature is alternating periods of
oversupply and undersupply (apparent business cycles), driven by the
imprecise valuations rather than by any exogenous shock.
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
        name="run2_high_error",
        model_factory=DEModel,
        model_kwargs=dict(
            init_epsilon=25.0,
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
        title="Run 2 — Imprecise valuations cause business cycles (init_epsilon=25)",
        out_path=FIG_DIR / "fig2_high_error",
        equi_price=100.0,
    )

    save_parquet(stack_results(results), DATA_DIR / "run2_high_error.parquet")

    summary = deviation_summary(results, equi_price=100.0, warmup=500)
    write_summary_md(summary, FIG_DIR / "run2_high_error_summary.md")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
