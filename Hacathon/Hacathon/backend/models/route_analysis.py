"""
Route analysis data model.
"""

from dataclasses import dataclass
from typing import List

@dataclass
class RouteAnalysis:
    """Detailed route analysis with efficiency metrics."""
    route_id: str
    out_amount: int
    hops: int
    platforms: List[str]
    price_impact: float
    efficiency_score: float
    compute_units: int
    time_to_route: int
    gas_estimate: float
    total_fee: float 