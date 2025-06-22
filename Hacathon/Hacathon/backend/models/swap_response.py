"""
Response models for swap operations.
"""

from dataclasses import dataclass
from typing import List, Optional
from .route_analysis import RouteAnalysis

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