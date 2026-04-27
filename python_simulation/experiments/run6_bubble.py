"""Run 6 — Speculative bubble: zero balancer + large error -> exponential
growth (Doc 2, ``MODEL DESIGN'').

When `Cb = 0` the model has no mechanism to add sellers in response to
rising prices, so winning bids -- systematically above the home value
because they are the maximum of multiple noisy draws -- compound into the
home valuations every epoch. The result is a clean exponential trajectory
on a log scale.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from edem.edem_model import EDEMModel  # noqa: E402

from experiments._runner import (  # noqa: E402
    DATA_DIR,
    Experiment,
    FIG_DIR,
    plot_edem_value,
    run_seeds,
    save_parquet,
    stack_results,
    write_summary_md,
)


def main() -> None:
    exp = Experiment(
        name="run6_bubble",
        model_factory=EDEMModel,
        model_kwargs=dict(
            init_epsilon=15.0,
            init_patience=20,
            Cb=0.0,
            init_buyers=20,
            init_sellers=20,
        ),
        n_ticks=3_000,
        n_seeds=10,
    )
    print(f"Running {exp.name}: n_ticks={exp.n_ticks}, n_seeds={exp.n_seeds}")
    results = run_seeds(exp)

    plot_edem_value(
        results,
        title="Run 6 — Speculative bubble (Cb=0, init_epsilon=15)",
        out_path=FIG_DIR / "fig6_bubble",
    )

    save_parquet(stack_results(results), DATA_DIR / "run6_bubble.parquet")

    df = stack_results(results)
    final = df[df["tick"] == df["tick"].max()]
    summary = {
        "n_seeds": int(final["seed"].nunique()),
        "median_final_value_over_true": float(final["value_over_true"].median()),
        "min_final_value_over_true": float(final["value_over_true"].min()),
        "max_final_value_over_true": float(final["value_over_true"].max()),
    }
    write_summary_md(summary, FIG_DIR / "run6_bubble_summary.md")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
