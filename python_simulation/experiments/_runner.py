r"""Shared utilities for experiment scripts.

Each `run{N}_*.py` script:

    1. Builds a `DEModel` (or `EDEMModel`) with a specific parameter set.
    2. Runs N seeds for T ticks via :func:`run_seeds`.
    3. Concatenates the per-seed model-reporter dataframes.
    4. Hands the result to :func:`plot_market_price` for a publication-
       quality PDF figure plus a Parquet dump for downstream analysis.

The output paths default to `../paper/figures/` and `../paper/figures/data/`
relative to the script, matching the LaTeX `\graphicspath{{figures/}}`.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tqdm import tqdm


REPO_ROOT = Path(__file__).resolve().parents[2]
FIG_DIR = REPO_ROOT / "paper" / "figures"
DATA_DIR = FIG_DIR / "data"


@dataclass
class RunResult:
    """One seed's worth of model-reporter output plus the seed used."""

    seed: int
    df: pd.DataFrame


@dataclass
class Experiment:
    name: str
    model_factory: Callable[..., object]
    model_kwargs: dict
    n_ticks: int
    n_seeds: int = 30
    seeds: list[int] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.seeds:
            self.seeds = list(range(1, self.n_seeds + 1))


def run_seeds(exp: Experiment, *, progress: bool = True) -> list[RunResult]:
    """Run `exp` once per seed and return a list of `RunResult`."""
    results: list[RunResult] = []
    iterator = exp.seeds
    if progress:
        iterator = tqdm(iterator, desc=exp.name, unit="seed")
    for seed in iterator:
        model = exp.model_factory(seed=seed, **exp.model_kwargs)
        for _ in range(exp.n_ticks):
            model.step()
        df = model.datacollector.get_model_vars_dataframe().copy()
        df["seed"] = seed
        df["tick"] = np.arange(len(df))
        results.append(RunResult(seed=seed, df=df))
    return results


def stack_results(results: list[RunResult]) -> pd.DataFrame:
    return pd.concat([r.df for r in results], ignore_index=True)


def save_parquet(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)


def plot_market_price(
    results: list[RunResult],
    *,
    title: str,
    out_path: Path,
    equi_price: float,
    show_population: bool = True,
    band_quantiles: tuple[float, float] = (0.1, 0.9),
) -> None:
    """Two-panel figure: top = market price (median + IQR-style band),
    bottom = buyer/seller counts (median + band). Each per-seed trajectory
    is overlaid faintly. Saves PDF + 300-dpi PNG to `out_path`.
    """
    df = stack_results(results)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    fig_height = 6.0 if show_population else 3.5
    fig, axes = plt.subplots(
        2 if show_population else 1,
        1,
        figsize=(8.5, fig_height),
        sharex=True,
        gridspec_kw={"height_ratios": [3, 2]} if show_population else None,
    )
    if not show_population:
        axes = [axes]

    # ---- price panel
    ax = axes[0]
    pivot = df.pivot(index="tick", columns="seed", values="market_price")
    median = pivot.median(axis=1)
    lo = pivot.quantile(band_quantiles[0], axis=1)
    hi = pivot.quantile(band_quantiles[1], axis=1)

    for s in pivot.columns:
        ax.plot(pivot.index, pivot[s], color="black", alpha=0.06, linewidth=0.6)
    ax.fill_between(pivot.index, lo, hi, alpha=0.25, color="C0", linewidth=0)
    ax.plot(pivot.index, median, color="C0", linewidth=1.4, label="median across seeds")
    ax.axhline(equi_price, color="grey", linewidth=1.2, linestyle="--", label="equilibrium price")
    ax.set_ylabel("market price")
    ax.set_title(title)
    ax.legend(loc="upper right", framealpha=0.9, fontsize=9)
    ax.grid(True, alpha=0.3)

    # ---- population panel
    if show_population:
        ax2 = axes[1]
        for col, color, label in [("n_sellers", "C3", "sellers"), ("n_buyers", "C2", "buyers")]:
            piv = df.pivot(index="tick", columns="seed", values=col)
            med = piv.median(axis=1)
            l = piv.quantile(band_quantiles[0], axis=1)
            h = piv.quantile(band_quantiles[1], axis=1)
            ax2.fill_between(piv.index, l, h, alpha=0.25, color=color, linewidth=0)
            ax2.plot(piv.index, med, color=color, linewidth=1.4, label=label)
        ax2.set_ylabel("count")
        ax2.set_xlabel("tick")
        ax2.legend(loc="upper right", framealpha=0.9, fontsize=9)
        ax2.grid(True, alpha=0.3)
    else:
        axes[0].set_xlabel("tick")

    fig.tight_layout()
    fig.savefig(out_path.with_suffix(".pdf"))
    fig.savefig(out_path.with_suffix(".png"), dpi=300)
    plt.close(fig)


def deviation_summary(
    results: list[RunResult] | pd.DataFrame,
    equi_price: float,
    *,
    warmup: int = 200,
) -> dict:
    """Min/max/std of (market_price / equi_price - 1) across all seeds, after
    discarding the first `warmup` ticks (the rolling-window fill period).

    Accepts either a list of `RunResult` (from `run_seeds`) or a stacked
    `DataFrame` already containing `tick`, `seed`, `market_price` columns.
    """
    df = stack_results(results) if isinstance(results, list) else results
    df = df[df["tick"] >= warmup]
    rel = df["market_price"] / equi_price - 1.0
    return {
        "n_seeds": int(df["seed"].nunique()),
        "mean_rel_dev": float(rel.mean()),
        "std_rel_dev": float(rel.std()),
        "min_rel_dev_pct": float(rel.min() * 100),
        "max_rel_dev_pct": float(rel.max() * 100),
    }


def write_summary_md(summary: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"- **{k}**: {v}" for k, v in summary.items()]
    path.write_text("# Run summary\n\n" + "\n".join(lines) + "\n", encoding="utf-8")


def plot_edem_value(
    results: list[RunResult] | dict[str, list[RunResult]],
    *,
    title: str,
    out_path: Path,
    band_quantiles: tuple[float, float] = (0.1, 0.9),
    log_scale: bool = True,
    show_epsilon: bool = False,
) -> None:
    """Plot `value_over_true` over time for one or more EDEM scenarios.

    `results` may be either a single list of `RunResult` or a dict mapping
    scenario label -> list of `RunResult`, in which case all scenarios are
    overlaid. The y-axis defaults to log scale, since the EDEM regimes
    are typically exponential.
    """
    if isinstance(results, list):
        results = {"": results}

    n_panels = 3 if show_epsilon else 2
    fig, axes = plt.subplots(
        n_panels,
        1,
        figsize=(9.0, 3.2 * n_panels),
        sharex=True,
    )

    colors = ["C0", "C3", "C2", "C4", "C1"]
    for (label, runs), color in zip(results.items(), colors, strict=False):
        df = stack_results(runs)
        piv = df.pivot(index="tick", columns="seed", values="value_over_true")
        med = piv.median(axis=1)
        lo = piv.quantile(band_quantiles[0], axis=1)
        hi = piv.quantile(band_quantiles[1], axis=1)
        axes[0].fill_between(piv.index, lo, hi, alpha=0.2, color=color, linewidth=0)
        axes[0].plot(piv.index, med, color=color, linewidth=1.4, label=label or None)
        for col, sub_color, sub_label in [
            ("n_sellers", color, f"{label} sellers" if label else "sellers"),
            ("n_buyers", color, f"{label} buyers" if label else "buyers"),
        ]:
            piv_c = df.pivot(index="tick", columns="seed", values=col)
            ls = "-" if "sellers" in sub_label else "--"
            axes[1].plot(piv_c.index, piv_c.median(axis=1), color=sub_color, linestyle=ls, linewidth=1.0, label=sub_label)
        if show_epsilon:
            piv_e = df.pivot(index="tick", columns="seed", values="current_epsilon")
            axes[2].plot(piv_e.index, piv_e.median(axis=1), color=color, linewidth=1.4, label=label or None)

    axes[0].axhline(1.0, color="grey", linewidth=1.0, linestyle="--")
    if log_scale:
        axes[0].set_yscale("log")
    axes[0].set_ylabel("value / true_value")
    axes[0].set_title(title)
    if any(label for label in results):
        axes[0].legend(loc="upper left", framealpha=0.9, fontsize=9)
    axes[0].grid(True, alpha=0.3, which="both")

    axes[1].set_ylabel("agent count")
    axes[1].legend(loc="upper right", framealpha=0.9, fontsize=8, ncol=2)
    axes[1].grid(True, alpha=0.3)

    if show_epsilon:
        axes[2].set_ylabel("current_epsilon (%)")
        axes[2].grid(True, alpha=0.3)
        axes[2].set_xlabel("tick")
    else:
        axes[1].set_xlabel("tick")

    fig.tight_layout()
    fig.savefig(out_path.with_suffix(".pdf"))
    fig.savefig(out_path.with_suffix(".png"), dpi=300)
    plt.close(fig)
