"""Dynamic Equilibrium (DE) model.

Mesa-3 implementation of the agent-based model described in Doc 1
(`SJSU - Disequilibria in markets.md`). The 32x32 toroidal grid is
populated by `equi_qnty` sellers (immobile, one per home) and `equi_qnty`
buyers (mobile, walking the grid and posting bids on sellers they meet).
"""

from __future__ import annotations

from collections.abc import Iterable

from mesa import Model
from mesa.datacollection import DataCollector
from mesa.space import MultiGrid

from .agents import Buyer, Seller
from .balancer import LinearBalancer, LinearSchedule
from .clearing import MarketPriceTracker
from .home import Home


class DEModel(Model):
    """Doc 1 Dynamic Equilibrium model."""

    def __init__(
        self,
        *,
        width: int = 32,
        height: int = 32,
        supply_intercept: float = 0.0,
        supply_slope: float = 0.5,
        demand_intercept: float = 100.0,
        demand_slope: float = -0.5,
        init_epsilon: float = 5.0,
        init_patience: int = 50,
        init_seller_time: int = 1,
        init_buyer_time: int = 1,
        balance_period: int = 100,
        sale_window: int = 25,
        accept_rule: str = "netlogo",
        seed: int | None = None,
        rng=None,
    ) -> None:
        if rng is None and seed is not None:
            rng = seed
        super().__init__(rng=rng)
        self.grid = MultiGrid(width, height, torus=True)

        self.init_epsilon = init_epsilon
        self.init_patience = init_patience
        self.init_seller_time = init_seller_time
        self.init_buyer_time = init_buyer_time
        self.accept_rule = accept_rule

        self.balancer = LinearBalancer(
            supply=LinearSchedule(supply_intercept, supply_slope),
            demand=LinearSchedule(demand_intercept, demand_slope),
            period=balance_period,
        )
        equi_price = self.balancer.equilibrium_price()
        equi_qnty = int(round(self.balancer.equilibrium_quantity()))

        self._price_tracker = MarketPriceTracker(window=sale_window, initial_price=equi_price)
        self.equi_price = equi_price
        self.equi_qnty = equi_qnty

        # Per-cell state — one Home per grid cell
        self.homes: dict[tuple[int, int], Home] = {
            (x, y): Home(pos=(x, y), mkt_price=equi_price)
            for x in range(width)
            for y in range(height)
        }

        self._spawn_initial_sellers(equi_qnty)
        self._spawn_initial_buyers(equi_qnty)

        self.datacollector = DataCollector(
            model_reporters={
                "market_price": lambda m: m.market_price,
                "equi_price": lambda m: m.balancer.equilibrium_price(),
                "n_sellers": lambda m: m.count_sellers(),
                "n_buyers": lambda m: m.count_buyers(),
                "n_sales_recorded": lambda m: m._price_tracker.n_sales_recorded,
                "init_patience": lambda m: m.init_patience,
            }
        )
        self.datacollector.collect(self)

    # ----- shock injection hooks (Run 5) ---------------------------------
    def set_demand(self, *, intercept: float | None = None, slope: float | None = None) -> None:
        """Update the demand schedule mid-run. Used by shock experiments."""
        if intercept is not None:
            self.balancer.demand.intercept = float(intercept)
        if slope is not None:
            self.balancer.demand.slope = float(slope)
        # Keep `equi_price` field (used by initial spawn helpers) in sync.
        self.equi_price = self.balancer.equilibrium_price()

    def set_supply(self, *, intercept: float | None = None, slope: float | None = None) -> None:
        if intercept is not None:
            self.balancer.supply.intercept = float(intercept)
        if slope is not None:
            self.balancer.supply.slope = float(slope)
        self.equi_price = self.balancer.equilibrium_price()

    # ----- public properties --------------------------------------------
    @property
    def market_price(self) -> float:
        return self._price_tracker.market_price

    def count_sellers(self) -> int:
        return len([a for a in self.agents if isinstance(a, Seller)])

    def count_buyers(self) -> int:
        return len([a for a in self.agents if isinstance(a, Buyer)])

    def avg_ask_price(self) -> float:
        sellers = [a for a in self.agents if isinstance(a, Seller)]
        if not sellers:
            return self.market_price
        return sum(s.ask_price for s in sellers) / len(sellers)

    # ----- spawn helpers ------------------------------------------------
    def _free_seller_cell(self) -> tuple[int, int]:
        for _ in range(64):
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            cell = self.grid.get_cell_list_contents([(x, y)])
            if not any(isinstance(a, Seller) for a in cell):
                return (x, y)
        # rare worst-case: scan
        for x in range(self.grid.width):
            for y in range(self.grid.height):
                cell = self.grid.get_cell_list_contents([(x, y)])
                if not any(isinstance(a, Seller) for a in cell):
                    return (x, y)
        raise RuntimeError("no free cell for seller — grid saturated")

    def _spawn_initial_sellers(self, n: int) -> None:
        for _ in range(n):
            err = (self.random.random() * self.init_epsilon * 2 - self.init_epsilon) / 100.0
            ask = self.equi_price + self.equi_price * err
            seller = Seller(
                self,
                epsilon=self.random.uniform(0.0, self.init_epsilon),
                patience=self.random.randrange(self.init_patience),
                ask_price=ask,
                delay=0,
            )
            self.grid.place_agent(seller, self._free_seller_cell())

    def _spawn_initial_buyers(self, n: int) -> None:
        for _ in range(n):
            buyer = Buyer(
                self,
                epsilon=self.random.uniform(0.0, self.init_epsilon),
                delay=0,
            )
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(buyer, (x, y))

    def add_seller_via_balancer(self) -> None:
        # NetLogo `add_seller` — uses recent average sale price
        recent = self.market_price
        err = (self.random.random() * self.init_epsilon * 2 - self.init_epsilon) / 100.0
        ask = recent + recent * err
        # patience: 50 + random(init_patience - 50) — guarded
        lo = min(50, max(0, self.init_patience - 1))
        span = max(1, self.init_patience - lo)
        seller = Seller(
            self,
            epsilon=self.random.uniform(0.0, self.init_epsilon),
            patience=lo + self.random.randrange(span),
            ask_price=ask,
            delay=self.random.randrange(max(1, self.init_seller_time)),
        )
        self.grid.place_agent(seller, self._free_seller_cell())

    def add_buyer_via_balancer(self) -> None:
        buyer = Buyer(
            self,
            epsilon=self.random.uniform(0.0, self.init_epsilon),
            delay=self.random.randrange(max(1, self.init_buyer_time)),
        )
        x = self.random.randrange(self.grid.width)
        y = self.random.randrange(self.grid.height)
        self.grid.place_agent(buyer, (x, y))

    # ----- removal helpers ----------------------------------------------
    def remove_one_seller(self) -> None:
        sellers = [a for a in self.agents if isinstance(a, Seller)]
        if not sellers:
            return
        victim = self.random.choice(sellers)
        self._remove_seller(victim)

    def remove_one_buyer(self) -> None:
        buyers = [a for a in self.agents if isinstance(a, Buyer)]
        if not buyers:
            return
        victim = self.random.choice(buyers)
        self._remove_buyer(victim)

    def _remove_seller(self, seller: Seller) -> None:
        seller._drop_all_bids()
        if seller.pos is not None:
            self.grid.remove_agent(seller)
        seller.remove()

    def _remove_buyer(self, buyer: Buyer) -> None:
        buyer._drop_all_bids()
        if buyer.pos is not None:
            self.grid.remove_agent(buyer)
        buyer.remove()

    # ----- sale completion ----------------------------------------------
    def complete_sale(self, *, seller: Seller, buyer: Buyer, price: float) -> None:
        home = self.homes[seller.pos]
        home.record_sale(price=price, tick=self.steps)
        self._price_tracker.record_sale(price)

        # NetLogo: spawn a new seller and a new buyer to replace the pair
        self.add_seller_via_balancer()
        self.add_buyer_via_balancer()

        self._remove_seller(seller)
        self._remove_buyer(buyer)

    # ----- step ---------------------------------------------------------
    def step(self) -> None:
        self.agents.shuffle_do("step")
        self.balancer.step(self)
        self.datacollector.collect(self)

    # ----- driver -------------------------------------------------------
    def run(self, n_ticks: int, *, progress: bool = False) -> None:
        iterator: Iterable[int] = range(n_ticks)
        if progress:
            try:
                from tqdm import tqdm

                iterator = tqdm(iterator, total=n_ticks, desc="DE", unit="tick")
            except ImportError:  # pragma: no cover
                pass
        for _ in iterator:
            self.step()
