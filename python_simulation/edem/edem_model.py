"""Estimated Dynamic Equilibrium Model (EDEM) — speculative-market variant.

Mesa-3 translation of `speculative_market_simulation.nlogo` from
`sibmike/netlogo-realestate-simulations`. Where the DE model in
`de_model.py` clears markets via discrete sales, EDEM runs in epochs
of `init_patience` ticks during which sellers accumulate bids and never
actually transact. At the end of each epoch the model:

    1. updates every home's `value` by the *average* `lowest_bid_to_value`
       ratio of "yellow" buyers (those who placed at least one winning
       bid), so estimation errors compound multiplicatively across epochs
       (Doc 2, "MODEL DESIGN");
    2. applies a balancer parameterised by `Cb`:
            Cb > 0  — mean-reverting (rising prices add a seller, kill a
                      buyer; falling prices do the opposite);
            Cb = 0  — no balancer (Doc 2 bubble regime);
            Cb < 0  — trend-following (rising prices add a buyer, kill a
                      seller; Doc 2 "Silicon Valley real estate" regime);
    3. optionally inflates `current_epsilon` by `error_growth_per_epoch`,
       reproducing the Doc 2 bitcoin-style double-exponential scenario.

Order of operations within a tick mirrors the NetLogo `to go`: agents
step first, then the per-epoch hook fires when the cycle counter hits
zero. Patches' `cycle` counter is initialised to `init_patience - 1`
(one tick ahead of buyer/seller patience timers) so that the value
update sees the buyers' `is_yellow` state *before* their epoch reset.
"""

from __future__ import annotations

import math

from mesa import Agent, Model
from mesa.datacollection import DataCollector
from mesa.space import MultiGrid

from .home import Home


class EDEMSeller(Agent):
    """Speculative-market seller. Lives in epochs of `init_patience` ticks."""

    def __init__(self, model: "EDEMModel", *, init_patience: int) -> None:
        super().__init__(model)
        self.init_patience = init_patience
        self.patience = init_patience
        self.price = 0.0
        # bid stats over the current epoch
        self.bid = 0.0
        self.total_bids = 0.0
        self.number_of_bids = 0
        self.avg_bid_to_value = 0.0
        self.best_bid_to_value = 0.0
        self.best_bid_to_true_value = 0.0

    def step(self) -> None:
        if self.patience == self.init_patience:
            self._start_epoch()
        elif self.patience == 0:
            self._end_epoch_jump()
        else:
            self.patience -= 1
            if self.bid < self.price:
                self.price *= 0.9999

    def _start_epoch(self) -> None:
        home = self.model.homes[self.pos]
        eps = self.model.current_epsilon
        err_pct = (self.model.random.random() * eps * 2 - eps) / 100.0
        self.price = home.value * (1 + err_pct)
        self.patience -= 1

    def _end_epoch_jump(self) -> None:
        new_pos = self.model._free_seller_cell()
        self.model.grid.move_agent(self, new_pos)
        self.patience = self.init_patience
        self.bid = 0.0
        self.total_bids = 0.0
        self.number_of_bids = 0
        self.avg_bid_to_value = 0.0
        self.best_bid_to_value = 0.0


class EDEMBuyer(Agent):
    """Speculative-market buyer. Walks the torus, posts a bid on every
    seller it lands with, and tracks `lowest_bid_to_value` across the
    sellers on which it currently holds the winning bid.
    """

    def __init__(self, model: "EDEMModel", *, init_patience: int) -> None:
        super().__init__(model)
        self.init_patience = init_patience
        self.patience = init_patience
        self.my_bid = 0.0
        self.lowest_bid_to_value = 2.0  # sentinel: no winning bid yet
        self.lowest_bid_to_true_value = 2.0
        self.is_yellow = False
        self.heading = model.random.uniform(0.0, 360.0)

    def step(self) -> None:
        self.patience -= 1
        if self.patience == 0:
            self._reset_epoch()

        sellers_here = [
            a for a in self.model.grid.get_cell_list_contents([self.pos]) if isinstance(a, EDEMSeller)
        ]
        if sellers_here:
            self._post_bid_on(self.model.random.choice(sellers_here))

        self._wiggle_and_move()

    def _reset_epoch(self) -> None:
        self.patience = self.init_patience
        self.my_bid = 0.0
        self.lowest_bid_to_value = 2.0
        self.lowest_bid_to_true_value = 2.0
        self.is_yellow = False

    def _post_bid_on(self, seller: EDEMSeller) -> None:
        rng = self.model.random
        eps = self.model.current_epsilon
        err_pct = (rng.random() * eps * 2 - eps) / 100.0
        home = self.model.homes[seller.pos]
        self.my_bid = home.value * (1 + err_pct)

        seller.number_of_bids += 1
        seller.total_bids += self.my_bid
        seller.avg_bid_to_value = seller.total_bids / (seller.number_of_bids * home.value)

        # I'm winning if my bid beats the current best AND the ask price.
        if self.my_bid > seller.bid and self.my_bid > seller.price:
            seller.bid = self.my_bid
            seller.best_bid_to_value = self.my_bid / home.value
            seller.best_bid_to_true_value = self.my_bid / home.true_value
            ratio = self.my_bid / home.value
            if ratio < self.lowest_bid_to_value:
                self.lowest_bid_to_value = ratio
                self.lowest_bid_to_true_value = self.my_bid / home.true_value
                self.is_yellow = True

    def _wiggle_and_move(self) -> None:
        rng = self.model.random
        self.heading = (self.heading + rng.uniform(-90.0, 90.0)) % 360.0
        rad = math.radians(self.heading)
        dx = round(math.sin(rad))
        dy = round(math.cos(rad))
        if dx == 0 and dy == 0:
            dx = 1
        new_x = (self.pos[0] + dx) % self.model.grid.width
        new_y = (self.pos[1] + dy) % self.model.grid.height
        self.model.grid.move_agent(self, (new_x, new_y))


class EDEMModel(Model):
    """Speculative-market EDEM model.

    Parameters
    ----------
    Cb
        Balancer coefficient. Magnitude is the number of agent swaps per
        epoch; sign controls direction (see module docstring).
    error_growth_per_epoch
        Additive increment to `current_epsilon` at the end of every epoch.
        Used by Run 8 (double-exponential) to recreate Doc 2's
        bitcoin-like scenario where divergence of opinion grows with the
        bull market.
    """

    def __init__(
        self,
        *,
        width: int = 32,
        height: int = 32,
        init_epsilon: float = 10.0,
        init_patience: int = 20,
        Cb: float = 1.0,
        error_growth_per_epoch: float = 0.0,
        init_buyers: int = 20,
        init_sellers: int = 20,
        true_value: float = 100.0,
        seed: int | None = None,
        rng=None,
    ) -> None:
        if rng is None and seed is not None:
            rng = seed
        super().__init__(rng=rng)
        self.grid = MultiGrid(width, height, torus=True)

        self.init_epsilon = init_epsilon
        self.current_epsilon = init_epsilon
        self.init_patience = init_patience
        self.Cb = Cb
        self.error_growth_per_epoch = error_growth_per_epoch

        # patches: tick ahead of agents by 1 so end-of-epoch fires while
        # buyer is_yellow flags are still valid (NetLogo `init_patience - 1`).
        self._cycle_counter = init_patience - 1

        self.homes: dict[tuple[int, int], Home] = {
            (x, y): Home(pos=(x, y), true_value=true_value, value=true_value)
            for x in range(width)
            for y in range(height)
        }

        for _ in range(init_sellers):
            seller = EDEMSeller(self, init_patience=init_patience)
            self.grid.place_agent(seller, self._free_seller_cell())

        for _ in range(init_buyers):
            buyer = EDEMBuyer(self, init_patience=init_patience)
            x = self.random.randrange(width)
            y = self.random.randrange(height)
            self.grid.place_agent(buyer, (x, y))

        self.datacollector = DataCollector(
            model_reporters={
                "value_over_true": lambda m: (
                    sum(h.value for h in m.homes.values())
                    / sum(h.true_value for h in m.homes.values())
                ),
                "mean_value": lambda m: sum(h.value for h in m.homes.values()) / len(m.homes),
                "n_sellers": lambda m: m.count_sellers(),
                "n_buyers": lambda m: m.count_buyers(),
                "current_epsilon": lambda m: m.current_epsilon,
            }
        )
        self.datacollector.collect(self)

    # ----- counts and helpers -------------------------------------------
    def count_sellers(self) -> int:
        return len([a for a in self.agents if isinstance(a, EDEMSeller)])

    def count_buyers(self) -> int:
        return len([a for a in self.agents if isinstance(a, EDEMBuyer)])

    def _free_seller_cell(self) -> tuple[int, int]:
        for _ in range(64):
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            cell = self.grid.get_cell_list_contents([(x, y)])
            if not any(isinstance(a, EDEMSeller) for a in cell):
                return (x, y)
        # fallback: scan
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                cell = self.grid.get_cell_list_contents([(x, y)])
                if not any(isinstance(a, EDEMSeller) for a in cell):
                    return (x, y)
        # last resort
        return (
            self.random.randrange(self.grid.width),
            self.random.randrange(self.grid.height),
        )

    # ----- step + epoch -------------------------------------------------
    def step(self) -> None:
        self.agents.shuffle_do("step")
        self._cycle_counter -= 1
        if self._cycle_counter == 0:
            self._end_epoch()
            self._cycle_counter = self.init_patience
        self.datacollector.collect(self)

    def _end_epoch(self) -> None:
        # 1. Price-level update: scale all home values by the average
        #    `lowest_bid_to_value` of yellow buyers.
        yellow = [a for a in self.agents if isinstance(a, EDEMBuyer) and a.is_yellow]
        if yellow:
            avg_ratio = sum(a.lowest_bid_to_value for a in yellow) / len(yellow)
            for home in self.homes.values():
                home.value *= avg_ratio
        else:
            avg_ratio = 1.0  # no winners this epoch -> no change

        # 2. Balancer. |Cb| controls swap intensity per epoch as a
        #    real-valued count: integer part is fired deterministically,
        #    fractional part as a Bernoulli draw. Sign controls direction
        #    (mean-reverting vs trend-following).
        if self.Cb != 0 and yellow:
            mag = abs(self.Cb)
            n_swaps = int(mag)
            if self.random.random() < (mag - n_swaps):
                n_swaps += 1
            if n_swaps > 0:
                standard = self.Cb > 0
                rising = avg_ratio >= 1.0
                if rising == standard:
                    self._add_sellers_remove_buyers(n_swaps)
                else:
                    self._add_buyers_remove_sellers(n_swaps)

        # 3. Error growth (Doc 2 double-exponential scenario).
        self.current_epsilon += self.error_growth_per_epoch
        if self.current_epsilon < 0:
            self.current_epsilon = 0.0

    def _add_sellers_remove_buyers(self, n: int) -> None:
        for _ in range(n):
            seller = EDEMSeller(self, init_patience=self.init_patience)
            self.grid.place_agent(seller, self._free_seller_cell())
            buyers = [a for a in self.agents if isinstance(a, EDEMBuyer)]
            # NetLogo guard: never kill the last agent on a side.
            if len(buyers) > 1:
                victim = self.random.choice(buyers)
                self.grid.remove_agent(victim)
                victim.remove()

    def _add_buyers_remove_sellers(self, n: int) -> None:
        for _ in range(n):
            buyer = EDEMBuyer(self, init_patience=self.init_patience)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(buyer, (x, y))
            sellers = [a for a in self.agents if isinstance(a, EDEMSeller)]
            if len(sellers) > 1:
                victim = self.random.choice(sellers)
                self.grid.remove_agent(victim)
                victim.remove()

    # ----- driver -------------------------------------------------------
    def run(self, n_ticks: int) -> None:
        for _ in range(n_ticks):
            self.step()
