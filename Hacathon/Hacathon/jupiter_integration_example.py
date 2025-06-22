"""
Jupiter Integration Example
This shows how to integrate route analysis with actual swap execution.
This can be used as a reference for implementing in the main Jupiter application.
"""

import requests
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class SwapRequest:
    """Represents a swap request with all necessary parameters."""
    input_mint: str
    output_mint: str
    amount: int
    slippage_bps: int = 50
    user_public_key: str = ""
    wrap_unwrap_sol: bool = True

@dataclass
class RouteAnalysis:
    """Represents analyzed route with efficiency metrics."""
    route_id: str
    out_amount: int
    hops: int
    platforms: List[str]
    price_impact: float
    efficiency_score: float
    compute_units: int
    time_to_route: int

class JupiterIntegration:
    """
    Complete Jupiter integration for route analysis and swap execution.
    This can be integrated into the main Jupiter application.
    """
    
    def __init__(self):
        self.base_url = "https://quote-api.jup.ag/v6"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Jupiter-Route-Analyzer/1.0',
            'Accept': 'application/json',
        })
    
    def get_quote(self, request: SwapRequest) -> Dict[str, Any]:
        """Get quote from Jupiter API."""
        params = {
            'inputMint': request.input_mint,
            'outputMint': request.output_mint,
            'amount': str(request.amount),
            'slippageBps': request.slippage_bps,
            'maxRoutes': 10,
            'onlyDirectRoutes': 'false',
            'asLegacyTransaction': 'false',
        }
        
        if request.user_public_key:
            params['userPublicKey'] = request.user_public_key
        
        response = self.session.get(f"{self.base_url}/quote", params=params)
        response.raise_for_status()
        return response.json()
    
    def analyze_routes(self, routes: List[Dict], request: SwapRequest) -> List[RouteAnalysis]:
        """Analyze routes and calculate efficiency scores."""
        analyzed_routes = []
        
        for route in routes:
            # Extract route data
            platforms = []
            for step in route.get('swapSteps', []):
                platform = step.get('platform', 'unknown')
                platforms.append(platform)
            
            # Calculate efficiency score (same logic as before)
            hops = len(route.get('swapSteps', []))
            price_impact = route.get('priceImpact', 0)
            out_amount = route.get('outAmount', 0)
            
            # Efficiency calculation
            hop_score = 1.0 / max(hops, 1)
            price_impact_score = 1.0 - min(price_impact, 1.0)
            platform_diversity = min(len(set(platforms)) / max(hops, 1), 1.0)
            slippage_score = 1.0 - (request.slippage_bps / 10000)
            
            efficiency_score = (
                hop_score * 0.3 +
                price_impact_score * 0.4 +
                platform_diversity * 0.2 +
                slippage_score * 0.1
            )
            
            analyzed_routes.append(RouteAnalysis(
                route_id=route.get('routeId', ''),
                out_amount=out_amount,
                hops=hops,
                platforms=list(set(platforms)),
                price_impact=price_impact,
                efficiency_score=efficiency_score,
                compute_units=route.get('computeUnits', 0),
                time_to_route=route.get('timeToRoute', 0)
            ))
        
        # Sort by efficiency score (highest first)
        analyzed_routes.sort(key=lambda x: x.efficiency_score, reverse=True)
        return analyzed_routes
    
    def get_swap_transaction(self, route_id: str, request: SwapRequest) -> Dict[str, Any]:
        """Get swap transaction from Jupiter."""
        payload = {
            'route': route_id,
            'userPublicKey': request.user_public_key,
            'wrapUnwrapSOL': request.wrap_unwrap_sol,
        }
        
        response = self.session.post(f"{self.base_url}/swap", json=payload)
        response.raise_for_status()
        return response.json()
    
    def execute_swap(self, swap_transaction: Dict, wallet_signature: str) -> Dict[str, Any]:
        """
        Execute the swap transaction.
        In a real implementation, this would:
        1. Sign the transaction with the user's wallet
        2. Send it to the Solana network
        3. Return the transaction result
        """
        # This is a placeholder for the actual transaction execution
        # In reality, you would:
        # 1. Use a Solana client library (like solana.py)
        # 2. Sign the transaction with the user's private key
        # 3. Send it to a Solana RPC endpoint
        
        return {
            'success': True,
            'transaction_id': 'mock_transaction_id_123',
            'message': 'Swap executed successfully (mock)'
        }
    
    def auto_swap_with_analysis(self, request: SwapRequest) -> Dict[str, Any]:
        """
        Complete flow: Analyze routes, select best, and execute swap.
        This is the main function that would be called from the Jupiter app.
        """
        try:
            # Step 1: Get quotes
            print(f"🔍 Getting quotes for {request.amount} tokens...")
            quote_data = self.get_quote(request)
            routes = quote_data.get('routes', [])
            
            if not routes:
                return {'error': 'No routes found for the given parameters'}
            
            # Step 2: Analyze routes
            print(f"📊 Analyzing {len(routes)} routes...")
            analyzed_routes = self.analyze_routes(routes, request)
            
            # Step 3: Select best route
            best_route = analyzed_routes[0]
            print(f"✅ Selected best route: {best_route.route_id}")
            print(f"   Efficiency Score: {best_route.efficiency_score:.4f}")
            print(f"   Hops: {best_route.hops}")
            print(f"   Platforms: {', '.join(best_route.platforms)}")
            print(f"   Price Impact: {best_route.price_impact:.4f}")
            
            # Step 4: Get swap transaction
            print("🔄 Getting swap transaction...")
            swap_data = self.get_swap_transaction(best_route.route_id, request)
            
            # Step 5: Execute swap (mock for now)
            print("🚀 Executing swap...")
            result = self.execute_swap(swap_data, "mock_signature")
            
            return {
                'success': True,
                'selected_route': best_route,
                'all_routes': analyzed_routes,
                'swap_result': result,
                'transaction_data': swap_data
            }
            
        except Exception as e:
            return {'error': f'Swap failed: {str(e)}'}

def example_usage():
    """Example of how to use the Jupiter integration."""
    
    # Create a swap request
    request = SwapRequest(
        input_mint="So11111111111111111111111111111111111111112",  # SOL
        output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
        amount=1000000,  # 1 SOL
        slippage_bps=50,  # 0.5%
        user_public_key="YourWalletPublicKeyHere",  # User's wallet address
        wrap_unwrap_sol=True
    )
    
    # Initialize integration
    jupiter = JupiterIntegration()
    
    # Execute auto-swap with analysis
    result = jupiter.auto_swap_with_analysis(request)
    
    if result.get('success'):
        print("\n🎉 Swap completed successfully!")
        print(f"Transaction ID: {result['swap_result']['transaction_id']}")
        
        # Show route analysis
        print("\n📈 Route Analysis:")
        for i, route in enumerate(result['all_routes'][:3], 1):
            print(f"{i}. Route {route.route_id[:8]}...")
            print(f"   Score: {route.efficiency_score:.4f}")
            print(f"   Hops: {route.hops}")
            print(f"   Platforms: {', '.join(route.platforms)}")
            print(f"   Price Impact: {route.price_impact:.4f}%")
            print()
    else:
        print(f"❌ Swap failed: {result.get('error')}")

if __name__ == "__main__":
    print("🧭 Jupiter Integration Example")
    print("This shows how to integrate route analysis with swap execution.")
    print("=" * 50)
    example_usage() 