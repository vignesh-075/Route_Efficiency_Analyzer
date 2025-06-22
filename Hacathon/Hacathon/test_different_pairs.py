import requests
import json

def test_different_pairs():
    # Test different token pairs and amounts
    test_cases = [
        {
            'input_mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',  # USDC
            'output_mint': 'So11111111111111111111111111111111111111112',  # SOL
            'amount': '1000000',  # 1 USDC
            'desc': '1 USDC → SOL'
        },
        {
            'input_mint': 'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB',  # USDT
            'output_mint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',  # USDC
            'amount': '1000000',  # 1 USDT
            'desc': '1 USDT → USDC'
        },
        {
            'input_mint': '4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R',  # RAY
            'output_mint': 'So11111111111111111111111111111111111111112',  # SOL
            'amount': '1000000',  # 1 RAY
            'desc': '1 RAY → SOL'
        },
        {
            'input_mint': 'So11111111111111111111111111111111111111112',  # SOL
            'output_mint': '4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R',  # RAY
            'amount': '100000',  # 0.1 SOL
            'desc': '0.1 SOL → RAY'
        }
    ]
    
    url = "https://quote-api.jup.ag/v6/quote"
    
    for test_case in test_cases:
        print(f"\n--- Testing {test_case['desc']} ---")
        params = {
            'inputMint': test_case['input_mint'],
            'outputMint': test_case['output_mint'],
            'amount': test_case['amount'],
            'slippageBps': '50',
            'maxRoutes': '3'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                routes = data.get('routes', [])
                print(f"Routes found: {len(routes)}")
                
                if routes:
                    print(f"✅ SUCCESS! Found {len(routes)} route(s)")
                    print(f"First route outAmount: {routes[0].get('outAmount', 'N/A')}")
                    print(f"First route priceImpact: {routes[0].get('priceImpact', 'N/A')}")
                    print(f"First route swapSteps: {len(routes[0].get('swapSteps', []))}")
                    return True  # Found working pair
                else:
                    print("❌ No routes available for this pair/amount")
            else:
                print(f"❌ Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    return False

if __name__ == "__main__":
    print("Testing different token pairs to find working combinations...")
    success = test_different_pairs()
    if success:
        print("\n🎉 Found a working token pair! You can use this in your app.")
    else:
        print("\n😞 No working pairs found. This might indicate:")
        print("- Jupiter API is experiencing issues")
        print("- All tested pairs have insufficient liquidity")
        print("- API requirements have changed") 