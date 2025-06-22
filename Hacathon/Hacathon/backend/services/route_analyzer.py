"""
Core route analyzer service that fetches and analyzes swap routes.
"""

import asyncio
from typing import List, Optional
from backend.models.swap_request import SwapRequest, SwapMode, SelectionCriteria
from backend.models.route_analysis import RouteAnalysis
from backend.models.swap_response import SwapResponse
from backend.utils.scoring import get_score_by_criteria
from backend.services.jupiter_api import JupiterAPIClient, get_mock_quote_response

class RouteAnalyzer:
    """Main service for analyzing swap routes."""
    
    def __init__(self, use_demo_mode: bool = False):
        self.use_demo_mode = use_demo_mode
        self.jupiter_client = JupiterAPIClient()
    
    async def analyze_routes(self, request: SwapRequest) -> SwapResponse:
        """
        Analyze routes based on the swap request.
        
        Args:
            request: Complete swap request with user preferences
            
        Returns:
            SwapResponse with analysis results
        """
        try:
            # Get routes from Jupiter API or demo data
            if self.use_demo_mode:
                quote_response = get_mock_quote_response()
                demo_mode = True
            else:
                async with self.jupiter_client as client:
                    quote_response = await client.get_quote(request)
                demo_mode = False
            
            if not quote_response:
                return SwapResponse(
                    success=False,
                    message="No routes found or API error",
                    mode=request.mode.value,
                    total_routes_found=0,
                    error="Failed to fetch routes from Jupiter API"
                )
            
            # Parse routes into RouteAnalysis objects
            routes = self.jupiter_client.parse_routes(quote_response)
            
            if not routes:
                return SwapResponse(
                    success=False,
                    message="No valid routes found",
                    mode=request.mode.value,
                    total_routes_found=0,
                    error="No routes available for this swap"
                )
            
            # Calculate efficiency scores for each route
            for route in routes:
                route.efficiency_score = get_score_by_criteria(
                    request.auto_select_criteria.value,
                    route.hops,
                    route.price_impact,
                    route.platforms,
                    request.slippage_bps,
                    route.time_to_route,
                    route.compute_units,
                    route.out_amount
                )
            
            # Sort routes by efficiency score (descending)
            routes.sort(key=lambda x: x.efficiency_score, reverse=True)
            
            # Get best route
            best_route = routes[0] if routes else None
            
            # Handle different modes
            if request.mode == SwapMode.ANALYZE_ONLY:
                return SwapResponse(
                    success=True,
                    message=f"Found {len(routes)} routes. Analysis complete.",
                    mode=request.mode.value,
                    total_routes_found=len(routes),
                    best_route=best_route,
                    all_routes=routes,
                    demo_mode=demo_mode
                )
            
            elif request.mode == SwapMode.AUTO_SWAP:
                if not request.user_public_key:
                    return SwapResponse(
                        success=False,
                        message="User public key required for auto-swap",
                        mode=request.mode.value,
                        total_routes_found=len(routes),
                        best_route=best_route,
                        all_routes=routes,
                        error="Missing user public key"
                    )
                
                # For demo mode, simulate swap
                if demo_mode:
                    swap_result = {
                        "success": True,
                        "txid": "demo_transaction_123",
                        "route_used": best_route.route_id,
                        "amount_out": best_route.out_amount
                    }
                else:
                    # Get swap transaction from Jupiter
                    async with self.jupiter_client as client:
                        swap_transaction = await client.get_swap_transaction(
                            quote_response, request.user_public_key
                        )
                    
                    if not swap_transaction:
                        return SwapResponse(
                            success=False,
                            message="Failed to create swap transaction",
                            mode=request.mode.value,
                            total_routes_found=len(routes),
                            best_route=best_route,
                            all_routes=routes,
                            error="Swap transaction creation failed"
                        )
                    
                    swap_result = swap_transaction
                
                return SwapResponse(
                    success=True,
                    message=f"Auto-swap executed using best route. Found {len(routes)} routes.",
                    mode=request.mode.value,
                    total_routes_found=len(routes),
                    best_route=best_route,
                    all_routes=routes,
                    selected_route=best_route,
                    swap_result=swap_result,
                    demo_mode=demo_mode
                )
            
            elif request.mode == SwapMode.MANUAL_MODE:
                return SwapResponse(
                    success=True,
                    message=f"Found {len(routes)} routes for manual selection.",
                    mode=request.mode.value,
                    total_routes_found=len(routes),
                    best_route=best_route,
                    all_routes=routes,
                    demo_mode=demo_mode
                )
            
        except Exception as e:
            return SwapResponse(
                success=False,
                message="Error during route analysis",
                mode=request.mode.value,
                total_routes_found=0,
                error=str(e)
            )
    
    def get_route_summary(self, routes: List[RouteAnalysis]) -> dict:
        """
        Get summary statistics for routes.
        
        Args:
            routes: List of analyzed routes
            
        Returns:
            Summary statistics
        """
        if not routes:
            return {}
        
        return {
            "total_routes": len(routes),
            "avg_hops": sum(r.hops for r in routes) / len(routes),
            "avg_price_impact": sum(r.price_impact for r in routes) / len(routes),
            "avg_efficiency": sum(r.efficiency_score for r in routes) / len(routes),
            "platforms_used": list(set(platform for r in routes for platform in r.platforms)),
            "best_efficiency": max(r.efficiency_score for r in routes),
            "worst_efficiency": min(r.efficiency_score for r in routes)
        } 