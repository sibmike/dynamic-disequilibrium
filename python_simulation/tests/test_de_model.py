"""End-to-end smoke tests for the DE model.

These are not statistical assertions (those are too slow for unit tests);
they only confirm that:

    - the model constructs at the documented Run 1 equilibrium,
    - it runs N ticks without raising,
    - the agent population stays roughly bounded,
    - sales accumulate into the rolling-window price tracker.

Quantitative validation against Doc 1's published deviation bounds lives
in `experiments/run1_stable.py` (which writes Figure 1 to the paper).
"""

from __future__ import annotations

import pytest

from edem.agents import Buyer, Seller
from edem.de_model import DEModel


def test_initial_state_matches_doc1_run1():
    m = DEModel(seed=42)
    assert m.equi_price == pytest.approx(100.0)
    assert m.equi_qnty == 50
    assert m.count_sellers() == 50
    assert m.count_buyers() == 50
    assert m.market_price == pytest.approx(100.0)


def test_short_run_completes_and_records_sales():
    m = DEModel(seed=7)
    for _ in range(500):
        m.step()
    # at least one sale should have happened in 500 ticks
    assert m._price_tracker.n_sales_recorded >= 1
    df = m.datacollector.get_model_vars_dataframe()
    assert len(df) == 501  # initial collect + 500 ticks


def test_population_bounded_under_balancer():
    m = DEModel(seed=11)
    for _ in range(1000):
        m.step()
    # populations should stay within a reasonable factor of equilibrium qty
    assert 5 <= m.count_sellers() <= 200
    assert 5 <= m.count_buyers() <= 200


def test_seed_determinism():
    a = DEModel(seed=123)
    b = DEModel(seed=123)
    for _ in range(200):
        a.step()
        b.step()
    da = a.datacollector.get_model_vars_dataframe().market_price.tolist()
    db = b.datacollector.get_model_vars_dataframe().market_price.tolist()
    assert da == db


def test_agents_are_either_buyer_or_seller():
    m = DEModel(seed=5)
    for a in m.agents:
        assert isinstance(a, (Buyer, Seller))


def test_no_two_sellers_share_a_cell():
    m = DEModel(seed=99)
    cells: dict = {}
    for a in m.agents:
        if isinstance(a, Seller):
            cells.setdefault(a.pos, []).append(a)
    for pos, sellers in cells.items():
        assert len(sellers) == 1, f"two sellers at {pos}"


def test_run1_stable_within_doc1_envelope():
    """5000-tick run should keep market_price within a generous envelope of
    the equilibrium price. Doc 1 reports +/-6% over 100k ticks for Run 1;
    we use +/-12% as a soft envelope to stay robust to seed variation in a
    short run."""
    m = DEModel(seed=42)
    for _ in range(5000):
        m.step()
    df = m.datacollector.get_model_vars_dataframe()
    # ignore the warm-up period before the rolling window fills
    warm = df.iloc[200:].market_price
    assert (warm / 100.0 - 1).abs().max() < 0.12
