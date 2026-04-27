"""Run 8 — Bitcoin / Silicon-Valley regime: trend-following balancer +
rising divergence of opinion -> super-linear (``double-exponential'')
growth (Doc 2).

Combines two destabilising mechanisms:

  * `Cb = -1` -- the balancer pushes into the trend (when prices rise it
                 *adds* buyers and kills sellers, increasing bidding
                 pressure on remaining inventory);
  * `error_growth_per_epoch > 0` -- the cross-population estimation error
                                    grows with each epoch, mimicking the
                                    historically-observed expansion of
                                    divergence of opinion in late-stage
                                    bull markets.

Doc 2 cites the bitcoin price chart and Silicon Valley real-estate as
empirical referents.
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
        name="run8_double_exp",
        model_factory=EDEMModel,
        model_kwargs=dict(
            init_epsilon=5.0,
            error_growth_per_epoch=0.5,
            init_patience=20,
            Cb=-1.0,
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
        title="Run 8 — Trend-following balancer + rising error (Cb=-1, eps growth=+0.5/epoch)",
        out_path=FIG_DIR / "fig8_double_exp",
        show_epsilon=True,
    )

    save_parquet(stack_results(results), DATA_DIR / "run8_double_exp.parquet")

    df = stack_results(results)
    final = df[df["tick"] == df["tick"].max()]
    summary = {
        "n_seeds": int(final["seed"].nunique()),
        "median_final_value_over_true": float(final["value_over_true"].median()),
        "median_final_epsilon": float(final["current_epsilon"].median()),
    }
    write_summary_md(summary, FIG_DIR / "run8_double_exp_summary.md")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
