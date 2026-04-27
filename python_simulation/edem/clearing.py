"""Market clearing primitives shared by the DE and EDEM models.

Two responsibilities:

1. `MarketPriceTracker` maintains the rolling-window market price
   (Doc 1, Eq. 4): the average of the last `window` recorded sale prices.

2. `cond2_accepts` evaluates the buyer's bid-acceptance rule. Doc 1
   contains a discrepancy here: the prose Cond. 2 reads "accept iff
   `B_i < mean(buyer's bids)`" (commit to a relatively cheap offer),
   while the NetLogo source codes the opposite ("accept iff
   `B_i >= mean`"; commit to a relatively expensive offer). Empirically
   the prose rule produces a runaway price collapse — at every clearing
   step buyers sign with the seller who happened to receive the buyer's
   lowest bid, so realised sale prices are systematically below the
   ask-price floor. The NetLogo rule reproduces the stable equilibrium
   reported in Doc 1, Run 1 (deviations within +/- 6%).

   We therefore default to `accept_rule="netlogo"` and treat the prose
   rule as a documented alternative for sensitivity analysis. The
   companion paper (Section "Implementation in Mesa") describes the
   rule in economically transparent form: a buyer commits iff the
   offered bid is at or above the buyer's own benchmark over their
   currently outstanding bids.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Iterable


class MarketPriceTracker:
    """Rolling-window market price (Doc 1, Eq. 4).

    `market_price = mean(last `window` sale prices)`. Before the first
    `window` sales, falls back to `initial_price`.
    """

    def __init__(self, *, window: int = 25, initial_price: float = 100.0):
        if window <= 0:
            raise ValueError("window must be positive")
        self.window = window
        self.initial_price = float(initial_price)
        self._recent: deque[float] = deque(maxlen=window)

    @property
    def market_price(self) -> float:
        if not self._recent:
            return self.initial_price
        return sum(self._recent) / len(self._recent)

    @property
    def n_sales_recorded(self) -> int:
        return len(self._recent)

    def record_sale(self, price: float) -> None:
        self._recent.append(float(price))


def cond2_accepts(
    bid_price: float,
    all_buyer_bids: Iterable[float],
    *,
    accept_rule: str = "netlogo",
) -> bool:
    """Cond. 2 — should the offered buyer commit to this sale?

    The buyer is the holder of `bid_price` on the offering seller and has
    outstanding bids `all_buyer_bids` (which must include `bid_price`).

    Parameters
    ----------
    bid_price
        The bid currently being offered to the buyer to sign.
    all_buyer_bids
        All of the buyer's outstanding bids, including `bid_price`.
    accept_rule
        - `"netlogo"` (default): the rule actually coded in the 2018
          NetLogo source — accept iff `bid_price >= mean(bids)`. This
          reproduces the stable equilibrium reported in Doc 1, Run 1.
        - `"prose"`: the rule as written in Doc 1, Cond. 2 — accept iff
          `bid_price < mean(bids)`. Provided for sensitivity analysis;
          empirically produces a runaway price collapse.
    """
    bids = list(all_buyer_bids)
    if not bids:
        raise ValueError("all_buyer_bids must include at least the offered bid")
    mean_bid = sum(bids) / len(bids)
    if accept_rule == "netlogo":
        return bid_price >= mean_bid
    if accept_rule == "prose":
        return bid_price < mean_bid
    raise ValueError(f"unknown accept_rule: {accept_rule!r}")
