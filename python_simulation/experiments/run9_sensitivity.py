"""Run 9 -- Parameter-grid sensitivity sweep over (C_b, sigma).

Provides empirical armor for the central claim of the paper: that the
order-statistic drift derived in Section "framework-asymmetry"
survives broad changes in the EDEM parameters, not just the
specific Run-6/7/8 settings.

We sweep `C_b` across mean-reverting (+1), weakly-mean-reverting
(+0.5), no-balancer (0), weakly-trend-following (-0.5), and
trend-following (-1), and `sigma` across {5, 10, 15, 20, 25, 30}%.
Five seeds per cell. The reported metric is the median terminal
`value_over_true` across seeds.

Output: a single heatmap with `sigma` on the x-axis, `C_b` on the
y-axis, and log10-scaled colour. Markers overlay the cells covered
by Runs 6 (Cb=0, sigma=15) and 7 (the three Cb values at sigma=15).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from edem.edem_model import EDEMModel  # noqa: E402

from experiments._runner import (  # noqa: E402
    DATA_DIR,
    FIG_DIR,
    save_parquet,
    write_summary_md,
)


C_B_VALUES = [-1.0, -0.5, 0.0, 0.5, 1.0]
SIGMA_VALUES = [5.0, 10.0, 15.0, 20.0, 25.0, 30.0]
N_TICKS = 1_500
N_SEEDS = 5


def run_cell(*, Cb: float, sigma: float, seed: int) -> float:
    m = EDEMModel(
        seed=seed,
        Cb=Cb,
        init_epsilon=sigma,
        init_patience=20,
        init_buyers=20,
        init_sellers=20,
    )
    for _ in range(N_TICKS):
        m.step()
    df = m.datacollector.get_model_vars_dataframe()
    return float(df["value_over_true"].iloc[-1])


def main() -> None:
    rows: list[dict] = []
    total = len(C_B_VALUES) * len(SIGMA_VALUES) * N_SEEDS
    with tqdm(total=total, desc="run9_sweep", unit="cell-seed") as bar:
        for Cb in C_B_VALUES:
            for sigma in SIGMA_VALUES:
                for seed in range(1, N_SEEDS + 1):
                    vot = run_cell(Cb=Cb, sigma=sigma, seed=seed)
                    rows.append({"Cb": Cb, "sigma": sigma, "seed": seed, "vot": vot})
                    bar.update(1)
    df = pd.DataFrame(rows)
    save_parquet(df, DATA_DIR / "run9_sensitivity.parquet")

    # Pivot to median terminal value_over_true
    pivot = df.groupby(["Cb", "sigma"])["vot"].median().unstack("sigma")

    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    log_pivot = np.log10(pivot.values)
    im = ax.imshow(
        log_pivot,
        cmap="viridis",
        origin="lower",
        aspect="auto",
        extent=[
            min(SIGMA_VALUES) - 2.5,
            max(SIGMA_VALUES) + 2.5,
            min(C_B_VALUES) - 0.25,
            max(C_B_VALUES) + 0.25,
        ],
    )
    cbar = fig.colorbar(im, ax=ax, label=r"$\log_{10}$ median terminal $v_t / v^*$")

    # cell text overlay
    for i, Cb in enumerate(C_B_VALUES):
        for j, sigma in enumerate(SIGMA_VALUES):
            v = pivot.values[i, j]
            color = "white" if log_pivot[i, j] < 1.0 else "black"
            ax.text(sigma, Cb, f"{v:.1f}", ha="center", va="center", color=color, fontsize=8)

    # Reference markers for Runs 6 and 7 (Cb in {-1, 0, +1} at sigma=15).
    for ref_Cb, label in [(0.0, "R6/R7"), (1.0, "R7"), (-1.0, "R7")]:
        ax.scatter([15.0], [ref_Cb], marker="s", facecolor="none", edgecolor="red", s=180, linewidth=1.5)

    ax.set_xticks(SIGMA_VALUES)
    ax.set_yticks(C_B_VALUES)
    ax.set_xlabel(r"divergence of opinion $\bar\sigma$ (%)")
    ax.set_ylabel(r"balancer coefficient $C_b$")
    ax.set_title(
        f"Run 9 — Terminal $v_t / v^*$ over a 5×6 (C$_b$, $\\bar\\sigma$) grid "
        f"(t={N_TICKS}, {N_SEEDS} seeds/cell)"
    )

    fig.tight_layout()
    fig.savefig(FIG_DIR / "fig9_sensitivity.pdf")
    fig.savefig(FIG_DIR / "fig9_sensitivity.png", dpi=300)
    plt.close(fig)

    summary = {
        "n_cells": int(len(C_B_VALUES) * len(SIGMA_VALUES)),
        "n_seeds_per_cell": N_SEEDS,
        "n_ticks": N_TICKS,
        "median_terminal_vot_overall": float(df["vot"].median()),
        "min_median_per_cell": float(pivot.values.min()),
        "max_median_per_cell": float(pivot.values.max()),
        "fraction_cells_above_1.5x": float((pivot.values > 1.5).mean()),
        "fraction_cells_above_10x": float((pivot.values > 10.0).mean()),
    }
    write_summary_md(summary, FIG_DIR / "run9_sensitivity_summary.md")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
