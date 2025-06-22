"""
Test script for backend services.
"""

import asyncio
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.models.swap_request import SwapRequest, SwapMode, SelectionCriteria
from backend.services.route_analyzer import RouteAnalyzer

async def test_backend():
    """Test the backend services."""
    print("🧪 Testing Jupiter Smart Swap Backend Services...")
    
    # Test data
    test_request = SwapRequest(
        input_mint="So11111111111111111111111111111111111111112",  # SOL
        output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
        amount=1000000,  # 1 SOL
        slippage_bps=50,
        mode=SwapMode.ANALYZE_ONLY,
        auto_select_criteria=SelectionCriteria.EFFICIENCY
    )
    
    # Test with demo mode
    print("\n📊 Testing Route Analysis (Demo Mode)...")
    analyzer = RouteAnalyzer(use_demo_mode=True)
    
    try:
        response = await analyzer.analyze_routes(test_request)
        
        if response.success:
            print(f"✅ Analysis successful!")
            print(f"📈 Found {response.total_routes_found} routes")
            print(f"🏆 Best route efficiency: {response.best_route.efficiency_score:.3f}")
            print(f"🔄 Best route hops: {response.best_route.hops}")
            print(f"💰 Best route price impact: {response.best_route.price_impact:.4f}")
            print(f"🏢 Platforms used: {', '.join(response.best_route.platforms)}")
            
            if response.all_routes:
                print(f"\n📋 All routes summary:")
                for i, route in enumerate(response.all_routes[:3]):  # Show top 3
                    print(f"  {i+1}. Efficiency: {route.efficiency_score:.3f}, Hops: {route.hops}, Impact: {route.price_impact:.4f}")
        else:
            print(f"❌ Analysis failed: {response.error}")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    
    # Test auto-swap mode
    print("\n🤖 Testing Auto-Swap Mode (Demo)...")
    auto_swap_request = SwapRequest(
        input_mint="So11111111111111111111111111111111111111112",
        output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        amount=1000000,
        user_public_key="demo_public_key_123",
        mode=SwapMode.AUTO_SWAP,
        auto_select_criteria=SelectionCriteria.EFFICIENCY
    )
    
    try:
        auto_response = await analyzer.analyze_routes(auto_swap_request)
        
        if auto_response.success:
            print(f"✅ Auto-swap successful!")
            print(f"🎯 Selected route: {auto_response.selected_route.route_id}")
            print(f"📊 Swap result: {auto_response.swap_result}")
        else:
            print(f"❌ Auto-swap failed: {auto_response.error}")
            
    except Exception as e:
        print(f"❌ Auto-swap test failed: {e}")
    
    print("\n🎉 Backend services test completed!")

if __name__ == "__main__":
    asyncio.run(test_backend()) 