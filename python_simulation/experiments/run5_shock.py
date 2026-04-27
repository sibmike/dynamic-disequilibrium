"""Run 5 — Shock handling and transitional markets (Doc 1, Figs. 4-5).

Two scenarios share a 2-panel figure:

  Scenario A (single shock + patience recovery): the market begins at the
  Run 1 equilibrium (p*=100, q*=50), then at t=3000 demand drops by 50
  units (Run 4 parameters). The market re-stabilises *below* the new
  equilibrium of 50. At t=7000 we raise seller patience to 165 — Doc 1
  notes that this brings the market price back to the textbook equilibrium.

  Scenario B (transitional market): the demand intercept is shocked every
  `shock_period` ticks, alternating between two values. The market never
  reaches a stable state, mirroring Doc 1's "market in constant transition
  from one unknown state to another."
"""

from __future__ import annotations

import json
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from edem.de_model import DEModel  # noqa: E402

from experiments._runner import (  # noqa: E402
    DATA_DIR,
    FIG_DIR,
    deviation_summary,
    save_parquet,
    write_summary_md,
)


# ---- shock schedules ----------------------------------------------------


@dataclass
class ShockEvent:
    tick: int
    action: Callable[[DEModel], None]
    label: str


def schedule_single_shock_then_patience() -> list[ShockEvent]:
    """Scenario A schedule."""
    return [
        ShockEvent(
            tick=3000,
            action=lambda m: m.set_demand(intercept=50.0),
            label="demand shock: intercept 100→50",
        ),
        ShockEvent(
            tick=7000,
            action=lambda m: setattr(m, "init_patience", 165),
            label="seller patience raised to 165",
        ),
    ]


def schedule_transitional(shock_period: int, n_ticks: int) -> list[ShockEvent]:
    """Scenario B schedule: alternating demand intercepts every period."""
    schedule: list[ShockEvent] = []
    intercepts = [125.0, 75.0]
    for i, t in enumerate(range(shock_period, n_ticks, shock_period)):
        target = intercepts[i % 2]
        schedule.append(
            ShockEvent(
                tick=t,
                action=lambda m, v=target: m.set_demand(intercept=v),
                label=f"demand intercept → {target}",
            )
        )
    return schedule


# ---- driver -------------------------------------------------------------


def run_with_schedule(
    *,
    name: str,
    base_kwargs: dict,
    schedule: list[ShockEvent],
    n_ticks: int,
    n_seeds: int,
) -> list[pd.DataFrame]:
    schedule = sorted(schedule, key=lambda s: s.tick)
    out: list[pd.DataFrame] = []
    for seed in tqdm(range(1, n_seeds + 1), desc=name, unit="seed"):
        m = DEModel(seed=seed, **base_kwargs)
        idx = 0
        for t in range(n_ticks):
            while idx < len(schedule) and schedule[idx].tick == t:
                schedule[idx].action(m)
                idx += 1
            m.step()
        df = m.datacollector.get_model_vars_dataframe().copy()
        df["seed"] = seed
        df["tick"] = np.arange(len(df))
        df["scenario"] = name
        out.append(df)
    return out


# ---- plotting -----------------------------------------------------------


def plot_two_scenarios(
    scenario_a: pd.DataFrame,
    scenario_b: pd.DataFrame,
    schedule_a: list[ShockEvent],
    schedule_b: list[ShockEvent],
    *,
    out_path: Path,
) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(10.0, 7.0), sharex=False)

    for ax, df, schedule, title in [
        (
            axes[0],
            scenario_a,
            schedule_a,
            "Scenario A — single demand shock at t=3000, patience recovery at t=7000",
        ),
        (
            axes[1],
            scenario_b,
            schedule_b,
            "Scenario B — transitional market (demand intercept toggled every 2000 ticks)",
        ),
    ]:
        piv_p = df.pivot(index="tick", columns="seed", values="market_price")
        piv_e = df.pivot(index="tick", columns="seed", values="equi_price")

        med_p = piv_p.median(axis=1)
        lo_p = piv_p.quantile(0.1, axis=1)
        hi_p = piv_p.quantile(0.9, axis=1)
        med_e = piv_e.median(axis=1)

        for s in piv_p.columns:
            ax.plot(piv_p.index, piv_p[s], color="black", alpha=0.06, linewidth=0.6)
        ax.fill_between(piv_p.index, lo_p, hi_p, alpha=0.25, color="C0", linewidth=0)
        ax.plot(piv_p.index, med_p, color="C0", linewidth=1.4, label="market price (median)")
        ax.plot(
            piv_e.index,
            med_e,
            color="grey",
            linestyle="--",
            linewidth=1.2,
            label="textbook equilibrium price",
        )

        ymin, ymax = ax.get_ylim()
        for ev in schedule:
            ax.axvline(ev.tick, color="C3", linewidth=0.8, alpha=0.5)
            ax.text(
                ev.tick + 50,
                ymin + (ymax - ymin) * 0.92,
                ev.label,
                color="C3",
                fontsize=7,
                rotation=90,
                va="top",
                ha="left",
            )
        ax.set_ylabel("price")
        ax.set_title(title, fontsize=10)
        ax.legend(loc="upper right", framealpha=0.9, fontsize=9)
        ax.grid(True, alpha=0.3)
    axes[1].set_xlabel("tick")

    fig.tight_layout()
    fig.savefig(out_path.with_suffix(".pdf"))
    fig.savefig(out_path.with_suffix(".png"), dpi=300)
    plt.close(fig)


# ---- main ---------------------------------------------------------------


def main() -> None:
    base_kwargs = dict(
        init_epsilon=5.0,
        init_patience=50,
        balance_period=100,
    )

    n_ticks_a = 12_000
    schedule_a = schedule_single_shock_then_patience()
    print(f"Scenario A: {n_ticks_a} ticks with shocks @ {[ev.tick for ev in schedule_a]}")
    dfs_a = run_with_schedule(
        name="scenarioA_shock",
        base_kwargs=base_kwargs,
        schedule=schedule_a,
        n_ticks=n_ticks_a,
        n_seeds=8,
    )
    df_a = pd.concat(dfs_a, ignore_index=True)
    save_parquet(df_a, DATA_DIR / "run5_scenarioA.parquet")

    n_ticks_b = 12_000
    shock_period = 2000
    schedule_b = schedule_transitional(shock_period=shock_period, n_ticks=n_ticks_b)
    print(f"Scenario B: {n_ticks_b} ticks, {len(schedule_b)} alternating shocks")
    dfs_b = run_with_schedule(
        name="scenarioB_transitional",
        base_kwargs=base_kwargs,
        schedule=schedule_b,
        n_ticks=n_ticks_b,
        n_seeds=8,
    )
    df_b = pd.concat(dfs_b, ignore_index=True)
    save_parquet(df_b, DATA_DIR / "run5_scenarioB.parquet")

    plot_two_scenarios(df_a, df_b, schedule_a, schedule_b, out_path=FIG_DIR / "fig5_shock")

    summaries = {
        "A_pre_shock": deviation_summary(
            df_a[df_a["tick"] < 3000], equi_price=100.0, warmup=500
        ),
        "A_post_shock_pre_patience": deviation_summary(
            df_a[(df_a["tick"] >= 4000) & (df_a["tick"] < 7000)], equi_price=50.0, warmup=0
        ),
        "A_post_patience": deviation_summary(
            df_a[df_a["tick"] >= 8000], equi_price=50.0, warmup=0
        ),
        "B_overall_track_error": {
            "rms_dev_pct": float(
                ((df_b["market_price"] / df_b["equi_price"] - 1) ** 2).mean() ** 0.5 * 100
            ),
        },
    }
    write_summary_md(
        {f"{k} :: {ik}": iv for k, v in summaries.items() for ik, iv in v.items()},
        FIG_DIR / "run5_shock_summary.md",
    )
    print(json.dumps(summaries, indent=2))


if __name__ == "__main__":
    main()
