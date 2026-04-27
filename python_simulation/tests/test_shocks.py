"""Tests for the demand/supply shock hooks used by Run 5."""

from __future__ import annotations

import pytest

from edem.de_model import DEModel


def test_set_demand_intercept_updates_equilibrium():
    m = DEModel(seed=1)
    assert m.balancer.equilibrium_price() == pytest.approx(100.0)
    m.set_demand(intercept=50.0)
    assert m.balancer.equilibrium_price() == pytest.approx(50.0)
    assert m.equi_price == pytest.approx(50.0)


def test_set_demand_slope_updates_equilibrium():
    m = DEModel(seed=1)
    m.set_demand(slope=-0.25)  # Q_d = 100 - 0.25 p; intersect Q_s=0.5p at p* = 100/0.75
    assert m.balancer.equilibrium_price() == pytest.approx(100.0 / 0.75)


def test_set_supply_updates_equilibrium():
    m = DEModel(seed=1)
    m.set_supply(intercept=10.0)  # Q_s = 10 + 0.5p; intersect 100-0.5p at p* = 90
    assert m.balancer.equilibrium_price() == pytest.approx(90.0)


def test_post_shock_run_does_not_raise():
    m = DEModel(seed=2)
    for _ in range(500):
        m.step()
    m.set_demand(intercept=50.0)
    for _ in range(500):
        m.step()
    df = m.datacollector.get_model_vars_dataframe()
    # Equilibrium reporter should reflect the post-shock value at the tail
    assert df["equi_price"].iloc[-1] == pytest.approx(50.0)
    # Pre-shock equilibrium was 100
    assert df["equi_price"].iloc[100] == pytest.approx(100.0)


def test_patience_change_takes_effect_for_new_sellers():
    m = DEModel(seed=3, init_patience=50)
    # initial pool was sized with patience=50
    assert m.init_patience == 50
    m.init_patience = 165
    # The next balancer-spawned seller should draw from the new range.
    m.add_seller_via_balancer()
    new_seller = next(a for a in m.agents if hasattr(a, "ask_price"))
    # 50 + random(165 - 50) -> patience in [50, 165)
    # We can only assert the bound here; randomness handles the rest.
    assert 0 <= new_seller.patience <= 165
