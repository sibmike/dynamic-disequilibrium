"""Buyer and Seller agents for the DE / EDEM models.

Faithful translation of the `to sell` / `to buy` / `wiggle` / `move`
procedures in `Doc 1` (lines 278-387) and the corresponding procedures in
`speculative_market_simulation.nlogo`.

Bids in NetLogo are undirected links between a buyer and a seller. Here we
store them as mirrored entries on each side: `seller.bids[buyer] = price`
and `buyer.bids[seller] = price` always agree. The mirror is maintained by
`Buyer._place_bid` and broken only by `Seller._drop_bid` / on agent removal.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from mesa import Agent

from .clearing import cond2_accepts

if TYPE_CHECKING:
    from .de_model import DEModel


def _signed_uniform_pct(rng, epsilon: float) -> float:
    """NetLogo: `((random-float epsilon * 2) - epsilon) / 100`.

    Returns a uniform draw on `[-epsilon/100, +epsilon/100)`.
    """
    return (rng.random() * epsilon * 2 - epsilon) / 100.0


class Seller(Agent):
    """Immobile seller. Accumulates bids from passing buyers; on patience
    runout, either lowers the ask price or attempts to sign the highest
    bidder.
    """

    def __init__(
        self,
        model: "DEModel",
        *,
        epsilon: float,
        patience: int,
        ask_price: float,
        delay: int = 0,
    ) -> None:
        super().__init__(model)
        self.epsilon = epsilon
        self.patience = patience
        self.ask_price = ask_price
        self.delay = delay
        self.bids: dict[Buyer, float] = {}

    # ----- bid bookkeeping -----------------------------------------------
    def _drop_bid(self, buyer: "Buyer") -> None:
        self.bids.pop(buyer, None)
        buyer.bids.pop(self, None)

    def _drop_all_bids(self) -> None:
        for buyer in list(self.bids):
            self._drop_bid(buyer)

    # ----- step logic ----------------------------------------------------
    def step(self) -> None:
        if self.delay > 0:
            self.delay -= 1
            return
        self._sell()

    def _sell(self) -> None:
        rng = self.model.random
        if self.bids:
            winner, win_bid = max(self.bids.items(), key=lambda kv: kv[1])
            if self.patience != 0:
                self.patience -= 1
                return

            # patience exhausted
            if win_bid < self.ask_price:
                # Cond1: no bid above ask, lower ask price
                self.ask_price -= self.ask_price * (rng.random() * self.epsilon / 100.0)
                # NetLogo leaves patience at 0 here; the seller will keep
                # lowering on subsequent ticks until a high bid appears.
                return

            # win_bid >= ask_price: offer to sign
            buyer_bids = list(winner.bids.values())
            if cond2_accepts(win_bid, buyer_bids, accept_rule=self.model.accept_rule):
                # SALE
                self.model.complete_sale(seller=self, buyer=winner, price=win_bid)
            else:
                # buyer declines this bid; drop it and continue
                self._drop_bid(winner)
            return

        # no bids at all
        if self.patience != 0:
            self.patience -= 1
            return
        # patience exhausted with no bids: lower ask, replenish patience
        self.ask_price -= self.ask_price * (rng.random() * self.epsilon / 100.0)
        init_pat = self.model.init_patience
        # NetLogo: `50 + random (init_patience - 50)` — guarded for small init_patience
        lo = min(50, max(0, init_pat - 1))
        span = max(1, init_pat - lo)
        self.patience = lo + rng.randrange(span)


class Buyer(Agent):
    """Mobile buyer. Walks the torus, dropping a bid on each seller it lands
    with. Has no patience timer in DE — relies on Cond2 acceptance to leave
    the market.
    """

    def __init__(
        self,
        model: "DEModel",
        *,
        epsilon: float,
        delay: int = 0,
    ) -> None:
        super().__init__(model)
        self.epsilon = epsilon
        self.delay = delay
        self.bids: dict[Seller, float] = {}
        self.heading = model.random.uniform(0.0, 360.0)

    # ----- bid bookkeeping -----------------------------------------------
    def _place_bid(self, seller: Seller, price: float) -> None:
        self.bids[seller] = price
        seller.bids[self] = price

    def _drop_all_bids(self) -> None:
        for seller in list(self.bids):
            seller.bids.pop(self, None)
        self.bids.clear()

    # ----- step logic ----------------------------------------------------
    def step(self) -> None:
        if self.delay > 0:
            self.delay -= 1
            return
        self._buy()
        self._wiggle()
        self._move()

    def _buy(self) -> None:
        rng = self.model.random
        sellers_here = [
            a for a in self.model.grid.get_cell_list_contents([self.pos]) if isinstance(a, Seller)
        ]
        if not sellers_here:
            return
        seller = rng.choice(sellers_here)
        # NetLogo: my_bid = avg_ask_price + avg_ask_price * err
        avg_ask = self.model.avg_ask_price()
        err = _signed_uniform_pct(rng, self.epsilon)
        my_bid = avg_ask + avg_ask * err
        self._place_bid(seller, my_bid)

    def _wiggle(self) -> None:
        rng = self.model.random
        # rt random 90, lt random 90 -> net heading change in [-90, +90)
        self.heading = (self.heading + rng.uniform(-90.0, 90.0)) % 360.0

    def _move(self) -> None:
        rad = math.radians(self.heading)
        # NetLogo y-axis convention: heading 0 = north (positive y),
        # heading 90 = east (positive x). dx = sin(theta), dy = cos(theta).
        dx = round(math.sin(rad))
        dy = round(math.cos(rad))
        if dx == 0 and dy == 0:
            # forces a unit step in a cardinal direction
            dx, dy = 1, 0
        new_x = (self.pos[0] + dx) % self.model.grid.width
        new_y = (self.pos[1] + dy) % self.model.grid.height
        self.model.grid.move_agent(self, (new_x, new_y))
