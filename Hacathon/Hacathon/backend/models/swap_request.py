"""
Data models for Jupiter Smart Swap backend services.
"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class SwapMode(Enum):
    """Available swap modes."""
    ANALYZE_ONLY = "analyze_only"
    AUTO_SWAP = "auto_swap"
    MANUAL_MODE = "manual_mode"

class SelectionCriteria(Enum):
    """Criteria for auto-selecting routes."""
    EFFICIENCY = "efficiency"
    SPEED = "speed"
    COST = "cost"

@dataclass
class SwapRequest:
    """Complete swap request with user preferences."""
    input_mint: str
    output_mint: str
    amount: int
    slippage_bps: int = 50
    user_public_key: Optional[str] = None
    wrap_unwrap_sol: bool = True
    mode: SwapMode = SwapMode.ANALYZE_ONLY
    auto_select_criteria: SelectionCriteria = SelectionCriteria.EFFICIENCY

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

@dataclass
class SwapResponse:
    """Response from swap processing."""
    success: bool
    message: str
    mode: str
    total_routes_found: int
    best_route: Optional[RouteAnalysis] = None
    all_routes: Optional[List[RouteAnalysis]] = None
    selected_route: Optional[RouteAnalysis] = None
    swap_result: Optional[dict] = None
    error: Optional[str] = None
    demo_mode: bool = False

@dataclass
class HealthResponse:
    """Health check response."""
    status: str
    timestamp: float
    version: str
    jupiter_api_status: str 