"""Supply/demand rebalancing for the DE model.

Translates `to balance_supply` / `to balance_demand` from the Doc 1 NetLogo
source. Every `period` ticks, the balancer recomputes the linear supply
and demand quantities at the current market price and adds or removes one
agent of each type to nudge the population toward the target. The
single-agent-per-period nudge is intentional: it prevents large discrete
jumps in the agent population that would create artificial price shocks.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from .de_model import DEModel


class _LinearSchedule(Protocol):
    intercept: float
    slope: float


class LinearSchedule:
    """`Q(p) = intercept + slope * p` (Doc 1, Eqs. 1-2)."""

    __slots__ = ("intercept", "slope")

    def __init__(self, intercept: float, slope: float) -> None:
        self.intercept = float(intercept)
        self.slope = float(slope)

    def quantity(self, price: float) -> float:
        return self.intercept + self.slope * price


class LinearBalancer:
    """Restore population toward `Q_s(p)` and `Q_d(p)` by one agent per
    period. The model owns spawn/remove logic; the balancer only decides
    the direction.
    """

    def __init__(
        self,
        *,
        supply: LinearSchedule,
        demand: LinearSchedule,
        period: int = 100,
    ) -> None:
        if period <= 0:
            raise ValueError("period must be positive")
        self.supply = supply
        self.demand = demand
        self.period = period
        self._next_balance_in = period

    def equilibrium_price(self) -> float:
        # (demand_intercept - supply_intercept) / (supply_slope - demand_slope)
        denom = self.supply.slope - self.demand.slope
        if denom == 0:
            raise ValueError("supply and demand slopes are equal — no equilibrium")
        return (self.demand.intercept - self.supply.intercept) / denom

    def equilibrium_quantity(self) -> float:
        return self.supply.quantity(self.equilibrium_price())

    def step(self, model: "DEModel") -> None:
        self._next_balance_in -= 1
        if self._next_balance_in > 0:
            return
        self._next_balance_in = self.period

        market_price = model.market_price
        supply_target = round(self.supply.quantity(market_price))
        demand_target = round(self.demand.quantity(market_price))

        n_sellers = model.count_sellers()
        n_buyers = model.count_buyers()

        if supply_target - n_sellers > 0:
            model.add_seller_via_balancer()
        elif n_sellers > 1:
            model.remove_one_seller()

        if demand_target - n_buyers > 0:
            model.add_buyer_via_balancer()
        elif n_buyers > 1:
            model.remove_one_buyer()
