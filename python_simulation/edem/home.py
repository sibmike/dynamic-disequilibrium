"""Per-cell home state.

A `Home` is the Mesa equivalent of a NetLogo "patch" in the Arbuzov 2018
real-estate model. Homes are not Mesa Agents — they are per-cell records
attached to grid coordinates. Treating them as Agents would multiply scheduler
overhead by 1024 (32x32 grid) for state that never schedules behaviour.

The DE model uses `mkt_price`, `date_sold`, `price_sold`. The EDEM /
speculative-market variant additionally uses `true_value` and `value`
(see `edem_model.py`).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Home:
    pos: tuple[int, int]

    # DE fields (Doc 1)
    mkt_price: float = 0.0
    date_sold: int = 0
    price_sold: float = 0.0

    # EDEM fields (Doc 2 / speculative_market_simulation.nlogo)
    true_value: float = 0.0
    value: float = 0.0

    def record_sale(self, price: float, tick: int) -> None:
        self.price_sold = price
        self.date_sold = tick
