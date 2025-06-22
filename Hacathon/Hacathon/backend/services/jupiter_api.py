"""
Jupiter API client service for fetching routes and swap data.
"""

import aiohttp
import asyncio
import json
from typing import List, Dict, Optional
from backend.models.swap_request import SwapRequest
from backend.models.route_analysis import RouteAnalysis

class JupiterAPIClient:
    """Client for interacting with Jupiter API."""
    
    def __init__(self, base_url: str = "https://quote-api.jup.ag/v6"):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_quote(self, request: SwapRequest) -> Optional[Dict]:
        """
        Get quote from Jupiter API.
        
        Args:
            request: Swap request with parameters
            
        Returns:
            Quote response from Jupiter API
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        url = f"{self.base_url}/quote"
        params = {
            "inputMint": request.input_mint,
            "outputMint": request.output_mint,
            "amount": str(request.amount),
            "slippageBps": str(request.slippage_bps),
            "wrapUnwrapSOL": str(request.wrap_unwrap_sol).lower()
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Jupiter API error: {response.status}")
                    return None
        except Exception as e:
            print(f"Error fetching quote: {e}")
            return None
    
    async def get_swap_transaction(self, quote_response: Dict, user_public_key: str) -> Optional[Dict]:
        """
        Get swap transaction from Jupiter API.
        
        Args:
            quote_response: Response from get_quote
            user_public_key: User's public key
            
        Returns:
            Swap transaction data
        """
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        url = f"{self.base_url}/swap"
        
        payload = {
            "quoteResponse": quote_response,
            "userPublicKey": user_public_key,
            "wrapUnwrapSOL": True
        }
        
        try:
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Jupiter swap API error: {response.status}")
                    return None
        except Exception as e:
            print(f"Error getting swap transaction: {e}")
            return None
    
    def parse_routes(self, quote_response: Dict) -> List[RouteAnalysis]:
        """
        Parse Jupiter quote response into RouteAnalysis objects.
        
        Args:
            quote_response: Response from Jupiter API
            
        Returns:
            List of RouteAnalysis objects
        """
        routes = []
        
        if "data" not in quote_response:
            return routes
        
        for route in quote_response["data"]:
            # Extract platforms used
            platforms = []
            if "routePlan" in route:
                for step in route["routePlan"]:
                    if "swapInfo" in step and "amm" in step["swapInfo"]:
                        platforms.append(step["swapInfo"]["amm"]["label"])
            
            # Create RouteAnalysis object
            route_analysis = RouteAnalysis(
                route_id=route.get("routeId", ""),
                out_amount=int(route.get("outAmount", 0)),
                hops=len(route.get("routePlan", [])),
                platforms=platforms,
                price_impact=float(route.get("priceImpactPct", 0)) / 100,
                efficiency_score=0.0,  # Will be calculated later
                compute_units=int(route.get("computeUnitPriceMicroLamports", 0)),
                time_to_route=int(route.get("timeTaken", 0)),
                gas_estimate=float(route.get("computeUnitPriceMicroLamports", 0)) / 1_000_000,
                total_fee=float(route.get("otherAmountThreshold", 0)) / 1_000_000
            )
            
            routes.append(route_analysis)
        
        return routes

# Demo/Mock data for testing
def get_mock_quote_response() -> Dict:
    """Get mock quote response for demo purposes."""
    return {
        "data": [
            {
                "routeId": "route_1",
                "outAmount": "1000000",
                "routePlan": [
                    {
                        "swapInfo": {
                            "amm": {"label": "Raydium"},
                            "inAmount": "500000",
                            "outAmount": "1000000"
                        }
                    }
                ],
                "priceImpactPct": "0.1",
                "computeUnitPriceMicroLamports": "5000",
                "timeTaken": "150",
                "otherAmountThreshold": "50000"
            },
            {
                "routeId": "route_2", 
                "outAmount": "980000",
                "routePlan": [
                    {
                        "swapInfo": {
                            "amm": {"label": "Orca"},
                            "inAmount": "500000",
                            "outAmount": "980000"
                        }
                    }
                ],
                "priceImpactPct": "0.2",
                "computeUnitPriceMicroLamports": "3000",
                "timeTaken": "100",
                "otherAmountThreshold": "30000"
            }
        ]
    } 