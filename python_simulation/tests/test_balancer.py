"""Tests for the linear supply/demand balancer."""

from __future__ import annotations

import pytest

from edem.balancer import LinearBalancer, LinearSchedule


class TestLinearSchedule:
    def test_quantity_at_intercept(self):
        s = LinearSchedule(intercept=100.0, slope=-0.5)
        assert s.quantity(0.0) == 100.0

    def test_quantity_at_price(self):
        s = LinearSchedule(intercept=100.0, slope=-0.5)
        assert s.quantity(100.0) == 50.0


class TestLinearBalancer:
    def _doc1_run1_balancer(self) -> LinearBalancer:
        # Doc 1, Run 1: Q_s = 0.5 p, Q_d = 100 - 0.5 p, period=100
        return LinearBalancer(
            supply=LinearSchedule(intercept=0.0, slope=0.5),
            demand=LinearSchedule(intercept=100.0, slope=-0.5),
            period=100,
        )

    def test_equilibrium_price_run1(self):
        b = self._doc1_run1_balancer()
        assert b.equilibrium_price() == pytest.approx(100.0)

    def test_equilibrium_quantity_run1(self):
        b = self._doc1_run1_balancer()
        assert b.equilibrium_quantity() == pytest.approx(50.0)

    def test_run4_low_density_equilibrium(self):
        # Doc 1, Run 4: demand intercept reduced by 50 -> equi at p=50, q=25
        b = LinearBalancer(
            supply=LinearSchedule(intercept=0.0, slope=0.5),
            demand=LinearSchedule(intercept=50.0, slope=-0.5),
            period=100,
        )
        assert b.equilibrium_price() == pytest.approx(50.0)
        assert b.equilibrium_quantity() == pytest.approx(25.0)

    def test_equal_slopes_have_no_equilibrium(self):
        b = LinearBalancer(
            supply=LinearSchedule(intercept=0.0, slope=0.5),
            demand=LinearSchedule(intercept=100.0, slope=0.5),
            period=100,
        )
        with pytest.raises(ValueError):
            b.equilibrium_price()

    def test_zero_period_rejected(self):
        with pytest.raises(ValueError):
            LinearBalancer(
                supply=LinearSchedule(intercept=0.0, slope=0.5),
                demand=LinearSchedule(intercept=100.0, slope=-0.5),
                period=0,
            )

    def test_step_only_acts_each_period(self):
        # Use a fake model that records balancer-driven actions
        class FakeModel:
            def __init__(self):
                self.market_price = 100.0
                self.calls = []

            def count_sellers(self):
                return 50

            def count_buyers(self):
                return 50

            def add_seller_via_balancer(self):
                self.calls.append("add_seller")

            def remove_one_seller(self):
                self.calls.append("remove_seller")

            def add_buyer_via_balancer(self):
                self.calls.append("add_buyer")

            def remove_one_buyer(self):
                self.calls.append("remove_buyer")

        b = self._doc1_run1_balancer()
        m = FakeModel()
        # Period is 100 — 99 ticks should be silent, 100th should act.
        for _ in range(99):
            b.step(m)
        assert m.calls == []
        b.step(m)
        # At p=100, supply target=50 sellers, demand target=50 buyers.
        # Since count_sellers==50 and count_buyers==50, neither needs adding,
        # so we go to the "else" (remove). 50 > 1 so remove fires.
        assert m.calls == ["remove_seller", "remove_buyer"]
