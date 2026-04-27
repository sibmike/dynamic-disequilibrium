"""Run 7 — Balancer sign and magnitude shape, but cannot eliminate, the
bubble (Doc 2, ``random walk on a leash'' regime).

Three scenarios share an x-axis at fixed `init_epsilon=15`:

  * `Cb = +1`  mean-reverting balancer (rising prices -> add seller, kill
                buyer). Dampens but does not arrest the bubble.
  * `Cb =  0`  no balancer (same parameters as Run 6 for cross-reference).
  * `Cb = -1`  trend-following balancer ("Silicon Valley real estate"
                regime in Doc 2). Accelerates growth via increased buyer
                density and more competitive max-of-N bidding.

The figure makes Doc 2's central qualitative claim visible: the *sign*
of `Cb` controls whether the market hovers, deflates, or accelerates,
but in no scenario does the value return to the textbook
`value_over_true = 1` baseline. Bid-selection asymmetry (winning bids
are systematically above value) introduces a positive bias that even a
strong mean-reverting balancer cannot fully cancel.
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
    base_kwargs = dict(
        init_epsilon=15.0,
        init_patience=20,
        init_buyers=20,
        init_sellers=20,
    )
    n_ticks = 3_000
    n_seeds = 10

    scenarios: dict[str, list] = {}
    for label, Cb in [("Cb=+1 (mean-reverting)", 1.0), ("Cb= 0 (no balancer)", 0.0), ("Cb=-1 (trend-following)", -1.0)]:
        exp = Experiment(
            name=f"run7_Cb={Cb}",
            model_factory=EDEMModel,
            model_kwargs={**base_kwargs, "Cb": Cb},
            n_ticks=n_ticks,
            n_seeds=n_seeds,
        )
        print(f"Running {exp.name}")
        scenarios[label] = run_seeds(exp)

    plot_edem_value(
        scenarios,
        title="Run 7 — Balancer sign shapes (but cannot eliminate) the bubble (init_epsilon=15)",
        out_path=FIG_DIR / "fig7_balancer_sweep",
    )

    # Save a single combined parquet with a `scenario` column.
    import pandas as pd

    frames = []
    for label, runs in scenarios.items():
        df = stack_results(runs).copy()
        df["scenario"] = label
        frames.append(df)
    save_parquet(pd.concat(frames, ignore_index=True), DATA_DIR / "run7_balancer_sweep.parquet")

    summary = {}
    for label, runs in scenarios.items():
        df = stack_results(runs)
        final = df[df["tick"] == df["tick"].max()]
        summary[label] = {
            "median_final_vot": float(final["value_over_true"].median()),
            "iqr_final_vot": [
                float(final["value_over_true"].quantile(0.25)),
                float(final["value_over_true"].quantile(0.75)),
            ],
        }
    write_summary_md(
        {f"{k} :: {ik}": iv for k, v in summary.items() for ik, iv in v.items()},
        FIG_DIR / "run7_balancer_sweep_summary.md",
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
