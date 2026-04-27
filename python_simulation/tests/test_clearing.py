"""Tests for the rolling market price and Cond. 2 acceptance rule."""

from __future__ import annotations

import pytest

from edem.clearing import MarketPriceTracker, cond2_accepts


class TestMarketPriceTracker:
    def test_initial_price_before_any_sale(self):
        t = MarketPriceTracker(window=25, initial_price=100.0)
        assert t.market_price == 100.0
        assert t.n_sales_recorded == 0

    def test_partial_window_uses_mean_of_recorded_sales(self):
        t = MarketPriceTracker(window=25, initial_price=100.0)
        for p in [80.0, 120.0, 100.0]:
            t.record_sale(p)
        assert t.market_price == pytest.approx(100.0)
        assert t.n_sales_recorded == 3

    def test_full_window_drops_oldest(self):
        t = MarketPriceTracker(window=3, initial_price=100.0)
        for p in [100.0, 200.0, 300.0, 400.0]:
            t.record_sale(p)
        # oldest (100.0) dropped, mean of [200, 300, 400] = 300
        assert t.market_price == pytest.approx(300.0)
        assert t.n_sales_recorded == 3

    def test_zero_window_rejected(self):
        with pytest.raises(ValueError):
            MarketPriceTracker(window=0)


class TestCond2Acceptance:
    def test_netlogo_rule_accepts_when_bid_above_mean(self):
        # buyer's bids: [90, 100, 110]; mean = 100; offered bid = 110 (max)
        assert cond2_accepts(110.0, [90.0, 100.0, 110.0], accept_rule="netlogo") is True

    def test_netlogo_rule_rejects_when_bid_below_mean(self):
        assert cond2_accepts(90.0, [90.0, 100.0, 110.0], accept_rule="netlogo") is False

    def test_netlogo_rule_accepts_at_mean(self):
        assert cond2_accepts(100.0, [90.0, 100.0, 110.0], accept_rule="netlogo") is True

    def test_prose_rule_accepts_when_bid_below_mean(self):
        assert cond2_accepts(90.0, [90.0, 100.0, 110.0], accept_rule="prose") is True

    def test_prose_rule_rejects_when_bid_at_or_above_mean(self):
        assert cond2_accepts(100.0, [90.0, 100.0, 110.0], accept_rule="prose") is False
        assert cond2_accepts(110.0, [90.0, 100.0, 110.0], accept_rule="prose") is False

    def test_prose_and_netlogo_disagree_on_strict_below(self):
        bid, bids = 80.0, [80.0, 100.0, 120.0]
        assert cond2_accepts(bid, bids, accept_rule="prose") is True
        assert cond2_accepts(bid, bids, accept_rule="netlogo") is False

    def test_single_bid_always_at_mean(self):
        # one outstanding bid -> mean equals it -> netlogo accepts, prose rejects
        assert cond2_accepts(100.0, [100.0], accept_rule="netlogo") is True
        assert cond2_accepts(100.0, [100.0], accept_rule="prose") is False

    def test_empty_bids_raises(self):
        with pytest.raises(ValueError):
            cond2_accepts(100.0, [], accept_rule="netlogo")

    def test_unknown_rule_raises(self):
        with pytest.raises(ValueError):
            cond2_accepts(100.0, [100.0], accept_rule="random-walk")
