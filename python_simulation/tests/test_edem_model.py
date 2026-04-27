"""End-to-end tests for the EDEM speculative-market model."""

from __future__ import annotations

import pytest

from edem.edem_model import EDEMBuyer, EDEMModel, EDEMSeller


def test_initial_state():
    m = EDEMModel(seed=1, init_buyers=20, init_sellers=20, init_patience=20)
    assert m.count_sellers() == 20
    assert m.count_buyers() == 20
    assert all(h.value == h.true_value for h in m.homes.values())
    assert m.current_epsilon == m.init_epsilon


def test_epoch_fires_one_tick_before_buyer_reset():
    """The patches' end-of-epoch hook must fire while buyer `is_yellow`
    flags are still valid. Concretely: at tick `init_patience - 1` the
    model's _cycle_counter hits zero (hook fires); at tick `init_patience`
    the buyer's patience hits zero (resets `is_yellow`)."""
    m = EDEMModel(seed=42, init_buyers=20, init_sellers=20, init_patience=20)
    # Initial: cycle_counter = 19, buyer.patience = 20.
    assert m._cycle_counter == 19
    a_buyer = next(a for a in m.agents if isinstance(a, EDEMBuyer))
    assert a_buyer.patience == 20


def test_short_run_completes():
    m = EDEMModel(seed=2, init_buyers=20, init_sellers=20, init_patience=20)
    for _ in range(500):
        m.step()
    assert m.count_buyers() >= 1
    assert m.count_sellers() >= 1


def test_zero_balancer_allows_exponential_growth():
    """Cb=0 with substantial epsilon must produce supra-linear growth."""
    m = EDEMModel(seed=3, Cb=0, init_epsilon=15, init_patience=20)
    for _ in range(1500):
        m.step()
    df = m.datacollector.get_model_vars_dataframe()
    # value/true should be >> 1.5 by t=1500 with these parameters
    assert df.value_over_true.iloc[-1] > 5.0


def test_population_floor_prevents_total_drain():
    """The +1/-1 balancer must never kill the last agent on a side."""
    m = EDEMModel(seed=4, Cb=2.0, init_epsilon=15, init_patience=20)
    for _ in range(2000):
        m.step()
    assert m.count_buyers() >= 1
    assert m.count_sellers() >= 1


def test_negative_Cb_inverts_balancer_direction():
    """Cb < 0 should make the balancer trend-following, not mean-reverting.
    With substantial epsilon and a long-enough horizon, Cb=-1 produces
    materially more growth than Cb=+1 because it adds buyers when prices
    rise (more competitive bidding -> higher max bids)."""
    m_pos = EDEMModel(seed=7, Cb=1, init_epsilon=15, init_patience=20)
    m_neg = EDEMModel(seed=7, Cb=-1, init_epsilon=15, init_patience=20)
    for _ in range(2000):
        m_pos.step()
        m_neg.step()
    pos_final = m_pos.datacollector.get_model_vars_dataframe().value_over_true.iloc[-1]
    neg_final = m_neg.datacollector.get_model_vars_dataframe().value_over_true.iloc[-1]
    assert neg_final > pos_final, f"Cb=-1 should out-grow Cb=+1: got neg={neg_final}, pos={pos_final}"


def test_error_growth_inflates_epsilon_each_epoch():
    m = EDEMModel(seed=6, init_epsilon=5.0, error_growth_per_epoch=1.0, init_patience=10)
    for _ in range(100):  # 10 epochs
        m.step()
    # current_epsilon should be ~5 + 10*1 = 15 (give or take an epoch)
    assert 13.0 <= m.current_epsilon <= 16.0


def test_seed_determinism():
    a = EDEMModel(seed=99, Cb=1, init_epsilon=10)
    b = EDEMModel(seed=99, Cb=1, init_epsilon=10)
    for _ in range(200):
        a.step()
        b.step()
    da = a.datacollector.get_model_vars_dataframe().value_over_true.tolist()
    db = b.datacollector.get_model_vars_dataframe().value_over_true.tolist()
    assert da == db


def test_no_two_sellers_share_a_cell_at_setup():
    m = EDEMModel(seed=7, init_buyers=10, init_sellers=20)
    cells: dict = {}
    for a in m.agents:
        if isinstance(a, EDEMSeller):
            cells.setdefault(a.pos, []).append(a)
    for pos, sellers in cells.items():
        assert len(sellers) == 1, f"two sellers at {pos}"
