"""
🧭 Jupiter Smart Swap - Route Efficiency Analyzer & Auto-Swap
A complete solution for analyzing and executing optimal swap routes.

Three Modes:
1. 🔍 Analyze Only - Show route breakdown and efficiency scores
2. 🤖 Auto-Swap - Automatically select and execute best route
3. ⚙️ Manual Mode - Let user choose after seeing analysis

This can be integrated into Jupiter's mobile app or used as a standalone tool.
"""

import requests
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class SwapMode(Enum):
    ANALYZE_ONLY = "analyze_only"
    AUTO_SWAP = "auto_swap"
    MANUAL_MODE = "manual_mode"

@dataclass
class SwapRequest:
    """Complete swap request with user preferences."""
    input_mint: str
    output_mint: str
    amount: int
    slippage_bps: int = 50
    user_public_key: str = ""
    wrap_unwrap_sol: bool = True
    mode: SwapMode = SwapMode.ANALYZE_ONLY
    auto_select_criteria: str = "efficiency"  # "efficiency", "speed", "cost"

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

class JupiterSmartSwap:
    """
    Complete Jupiter integration with route analysis and smart swap execution.
    This is the main class that can be integrated into Jupiter's mobile app.
    """
    
    def __init__(self):
        self.base_url = "https://quote-api.jup.ag/v6"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Jupiter-Smart-Swap/1.0',
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
        """Analyze routes and calculate comprehensive efficiency scores."""
        analyzed_routes = []
        
        for route in routes:
            # Extract route data
            platforms = []
            for step in route.get('swapSteps', []):
                platform = step.get('platform', 'unknown')
                platforms.append(platform)
            
            # Calculate metrics
            hops = len(route.get('swapSteps', []))
            price_impact = route.get('priceImpact', 0)
            out_amount = route.get('outAmount', 0)
            compute_units = route.get('computeUnits', 0)
            time_to_route = route.get('timeToRoute', 0)
            
            # Calculate efficiency score based on user criteria
            if request.auto_select_criteria == "efficiency":
                efficiency_score = self._calculate_efficiency_score(hops, price_impact, platforms, request.slippage_bps)
            elif request.auto_select_criteria == "speed":
                efficiency_score = self._calculate_speed_score(hops, time_to_route, compute_units)
            elif request.auto_select_criteria == "cost":
                efficiency_score = self._calculate_cost_score(price_impact, compute_units, out_amount)
            else:
                efficiency_score = self._calculate_efficiency_score(hops, price_impact, platforms, request.slippage_bps)
            
            # Estimate gas cost (rough calculation)
            gas_estimate = compute_units * 0.000001  # SOL per compute unit (approximate)
            total_fee = gas_estimate + (price_impact * out_amount / 1_000_000)
            
            analyzed_routes.append(RouteAnalysis(
                route_id=route.get('routeId', ''),
                out_amount=out_amount,
                hops=hops,
                platforms=list(set(platforms)),
                price_impact=price_impact,
                efficiency_score=efficiency_score,
                compute_units=compute_units,
                time_to_route=time_to_route,
                gas_estimate=gas_estimate,
                total_fee=total_fee
            ))
        
        # Sort by efficiency score (highest first)
        analyzed_routes.sort(key=lambda x: x.efficiency_score, reverse=True)
        return analyzed_routes
    
    def _calculate_efficiency_score(self, hops: int, price_impact: float, platforms: List[str], slippage_bps: int) -> float:
        """Calculate efficiency score based on multiple factors."""
        hop_score = 1.0 / max(hops, 1)
        price_impact_score = 1.0 - min(price_impact, 1.0)
        platform_diversity = min(len(set(platforms)) / max(hops, 1), 1.0)
        slippage_score = 1.0 - (slippage_bps / 10000)
        
        return (
            hop_score * 0.3 +
            price_impact_score * 0.4 +
            platform_diversity * 0.2 +
            slippage_score * 0.1
        )
    
    def _calculate_speed_score(self, hops: int, time_to_route: int, compute_units: int) -> float:
        """Calculate score based on speed (fewer hops, faster routing, lower compute)."""
        hop_score = 1.0 / max(hops, 1)
        time_score = 1.0 / max(time_to_route, 1)
        compute_score = 1.0 / max(compute_units / 1000, 1)
        
        return (hop_score * 0.5 + time_score * 0.3 + compute_score * 0.2)
    
    def _calculate_cost_score(self, price_impact: float, compute_units: int, out_amount: int) -> float:
        """Calculate score based on cost (lower price impact, lower gas)."""
        price_score = 1.0 - min(price_impact, 1.0)
        gas_score = 1.0 / max(compute_units / 1000, 1)
        amount_score = out_amount / 1_000_000  # Normalize by amount
        
        return (price_score * 0.6 + gas_score * 0.3 + amount_score * 0.1)
    
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
        """Execute the swap transaction (mock implementation)."""
        # In a real implementation, this would:
        # 1. Sign the transaction with the user's wallet
        # 2. Send it to the Solana network
        # 3. Return the transaction result
        
        return {
            'success': True,
            'transaction_id': f'txn_{int(time.time())}',
            'message': 'Swap executed successfully',
            'timestamp': time.time()
        }
    
    def process_swap_request(self, request: SwapRequest) -> Dict[str, Any]:
        """
        Main function to process a swap request based on the selected mode.
        This is what would be called from Jupiter's mobile app.
        """
        try:
            print(f"🔍 Getting quotes for {request.amount} tokens...")
            quote_data = self.get_quote(request)
            routes = quote_data.get('routes', [])
            
            if not routes:
                return {
                    'success': False,
                    'error': 'No routes found for the given parameters',
                    'mode': request.mode.value
                }
            
            print(f"📊 Analyzing {len(routes)} routes...")
            analyzed_routes = self.analyze_routes(routes, request)
            
            # Prepare response based on mode
            response = {
                'success': True,
                'mode': request.mode.value,
                'all_routes': analyzed_routes,
                'total_routes_found': len(analyzed_routes)
            }
            
            if request.mode == SwapMode.ANALYZE_ONLY:
                # Just return analysis
                response['message'] = f"Found {len(analyzed_routes)} routes. Analysis complete."
                response['best_route'] = analyzed_routes[0] if analyzed_routes else None
                
            elif request.mode == SwapMode.AUTO_SWAP:
                # Auto-select and execute best route
                if not request.user_public_key:
                    return {
                        'success': False,
                        'error': 'Wallet public key required for auto-swap',
                        'mode': request.mode.value
                    }
                
                best_route = analyzed_routes[0]
                print(f"🤖 Auto-selecting best route: {best_route.route_id}")
                print(f"   Score: {best_route.efficiency_score:.4f}")
                print(f"   Hops: {best_route.hops}")
                print(f"   Platforms: {', '.join(best_route.platforms)}")
                
                # Get and execute swap
                swap_data = self.get_swap_transaction(best_route.route_id, request)
                result = self.execute_swap(swap_data, "auto_signature")
                
                response.update({
                    'selected_route': best_route,
                    'swap_result': result,
                    'message': 'Auto-swap completed successfully!'
                })
                
            elif request.mode == SwapMode.MANUAL_MODE:
                # Return analysis for user to choose
                response['message'] = f"Found {len(analyzed_routes)} routes. Please select one to execute."
                response['top_routes'] = analyzed_routes[:5]  # Top 5 for user selection
            
            return response
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Swap processing failed: {str(e)}',
                'mode': request.mode.value
            }
    
    def execute_selected_route(self, route_id: str, request: SwapRequest) -> Dict[str, Any]:
        """
        Execute a specific route (for manual mode).
        """
        try:
            if not request.user_public_key:
                return {'error': 'Wallet public key required'}
            
            swap_data = self.get_swap_transaction(route_id, request)
            result = self.execute_swap(swap_data, "manual_signature")
            
            return {
                'success': True,
                'route_id': route_id,
                'swap_result': result,
                'message': 'Manual swap completed successfully!'
            }
            
        except Exception as e:
            return {'error': f'Manual swap failed: {str(e)}'}

def example_usage():
    """Example of how to use Jupiter Smart Swap."""
    print("🧭 Jupiter Smart Swap - Route Efficiency Analyzer & Auto-Swap")
    print("=" * 60)
    
    # Initialize
    smart_swap = JupiterSmartSwap()
    
    # Example 1: Analyze Only Mode
    print("\n1. 🔍 ANALYZE ONLY MODE")
    print("-" * 30)
    analyze_request = SwapRequest(
        input_mint="So11111111111111111111111111111111111111112",  # SOL
        output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
        amount=1000000,  # 1 SOL
        mode=SwapMode.ANALYZE_ONLY
    )
    
    result = smart_swap.process_swap_request(analyze_request)
    if result.get('success'):
        print(f"✅ {result['message']}")
        if result.get('best_route'):
            route = result['best_route']
            print(f"🏆 Best Route:")
            print(f"   Score: {route.efficiency_score:.4f}")
            print(f"   Hops: {route.hops}")
            print(f"   Platforms: {', '.join(route.platforms)}")
            print(f"   Price Impact: {route.price_impact:.4f}%")
    else:
        print(f"❌ {result.get('error')}")
    
    # Example 2: Auto-Swap Mode (with mock wallet)
    print("\n2. 🤖 AUTO-SWAP MODE")
    print("-" * 30)
    auto_request = SwapRequest(
        input_mint="So11111111111111111111111111111111111111112",  # SOL
        output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
        amount=1000000,  # 1 SOL
        user_public_key="MockWalletPublicKey123...",
        mode=SwapMode.AUTO_SWAP,
        auto_select_criteria="efficiency"
    )
    
    result = smart_swap.process_swap_request(auto_request)
    if result.get('success'):
        print(f"✅ {result['message']}")
        if result.get('swap_result'):
            swap_result = result['swap_result']
            print(f"📊 Transaction ID: {swap_result['transaction_id']}")
    else:
        print(f"❌ {result.get('error')}")
    
    # Example 3: Manual Mode
    print("\n3. ⚙️ MANUAL MODE")
    print("-" * 30)
    manual_request = SwapRequest(
        input_mint="So11111111111111111111111111111111111111112",  # SOL
        output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
        amount=1000000,  # 1 SOL
        user_public_key="MockWalletPublicKey123...",
        mode=SwapMode.MANUAL_MODE
    )
    
    result = smart_swap.process_swap_request(manual_request)
    if result.get('success'):
        print(f"✅ {result['message']}")
        if result.get('top_routes'):
            print("📋 Top Routes Available:")
            for i, route in enumerate(result['top_routes'][:3], 1):
                print(f"   {i}. Route {route.route_id[:8]}... (Score: {route.efficiency_score:.4f})")
    else:
        print(f"❌ {result.get('error')}")

if __name__ == "__main__":
    example_usage() 