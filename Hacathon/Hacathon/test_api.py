import requests
import json

def test_jupiter_api():
    # Test with different amounts
    test_cases = [
        {'amount': '100000', 'desc': '0.1 SOL'},
        {'amount': '1000000', 'desc': '1 SOL'},
        {'amount': '10000000', 'desc': '10 SOL'},
    ]
    
    url = "https://quote-api.jup.ag/v6/quote"
    
    for test_case in test_cases:
        print(f"\n--- Testing {test_case['desc']} ---")
        params = {
            'inputMint': 'So11111111111111111111111111111111111111112',  # SOL
            'outputMint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',  # USDC
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
                    print(f"First route outAmount: {routes[0].get('outAmount', 'N/A')}")
                    print(f"First route priceImpact: {routes[0].get('priceImpact', 'N/A')}")
                    print(f"First route swapSteps: {len(routes[0].get('swapSteps', []))}")
                else:
                    print("No routes available for this amount")
            else:
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    test_jupiter_api() 