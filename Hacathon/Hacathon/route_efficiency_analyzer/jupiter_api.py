"""
Jupiter API client for the Route Efficiency Analyzer
Handles all interactions with Jupiter's Quote API.
"""

import requests
import time
from typing import Dict, List, Optional, Any
from .constants import JUPITER_QUOTE_ENDPOINT, DEFAULT_SLIPPAGE_BPS, DEFAULT_MAX_ROUTES


class JupiterAPIError(Exception):
    """Custom exception for Jupiter API errors."""
    pass


class JupiterAPIClient:
    """
    Client for interacting with Jupiter's Quote API.
    """
    
    def __init__(self, timeout: int = 30):
        """
        Initialize the Jupiter API client.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Route-Efficiency-Analyzer/1.0',
            'Accept': 'application/json',
        })
    
    def get_quote(
        self,
        input_mint: str,
        output_mint: str,
        amount: int,
        slippage_bps: int = DEFAULT_SLIPPAGE_BPS,
        only_direct_routes: bool = False,
        max_routes: int = DEFAULT_MAX_ROUTES,
        as_legacy_transaction: bool = False,
        platform_fee_bps: Optional[int] = None,
        platform_fee_account: Optional[str] = None,
        max_accounts: Optional[int] = None,
        force_fetch: bool = False
    ) -> Dict[str, Any]:
        """
        Get quote from Jupiter API.
        
        Args:
            input_mint: Input token mint address
            output_mint: Output token mint address
            amount: Input amount in raw units
            slippage_bps: Slippage in basis points (1 bps = 0.01%)
            only_direct_routes: Only return direct routes
            max_routes: Maximum number of routes to return
            as_legacy_transaction: Return as legacy transaction
            platform_fee_bps: Platform fee in basis points
            platform_fee_account: Platform fee account
            max_accounts: Maximum number of accounts
            force_fetch: Force fetch from API (ignore cache)
            
        Returns:
            Quote response from Jupiter API
            
        Raises:
            JupiterAPIError: If API request fails
        """
        params = {
            'inputMint': input_mint,
            'outputMint': output_mint,
            'amount': str(amount),
            'slippageBps': slippage_bps,
            'onlyDirectRoutes': str(only_direct_routes).lower(),
            'maxRoutes': max_routes,
            'asLegacyTransaction': str(as_legacy_transaction).lower(),
        }
        
        # Add optional parameters
        if platform_fee_bps is not None:
            params['platformFeeBps'] = platform_fee_bps
        if platform_fee_account is not None:
            params['platformFeeAccount'] = platform_fee_account
        if max_accounts is not None:
            params['maxAccounts'] = max_accounts
        if force_fetch:
            params['forceFetch'] = str(force_fetch).lower()
        
        try:
            response = self.session.get(
                JUPITER_QUOTE_ENDPOINT,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('error', str(e))
                except:
                    error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            else:
                error_msg = str(e)
            
            raise JupiterAPIError(f"Failed to get quote: {error_msg}")
    
    def get_swap_routes(
        self,
        input_mint: str,
        output_mint: str,
        amount: int,
        slippage_bps: int = DEFAULT_SLIPPAGE_BPS,
        max_routes: int = DEFAULT_MAX_ROUTES,
        only_direct_routes: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get swap routes from Jupiter API.
        
        Args:
            input_mint: Input token mint address
            output_mint: Output token mint address
            amount: Input amount in raw units
            slippage_bps: Slippage in basis points
            max_routes: Maximum number of routes to return
            only_direct_routes: Only return direct routes
            
        Returns:
            List of route data
            
        Raises:
            JupiterAPIError: If API request fails
        """
        quote_data = self.get_quote(
            input_mint=input_mint,
            output_mint=output_mint,
            amount=amount,
            slippage_bps=slippage_bps,
            max_routes=max_routes,
            only_direct_routes=only_direct_routes
        )
        
        routes = quote_data.get('routes', [])
        
        if not routes:
            raise JupiterAPIError("No routes found for the given parameters")
        
        return routes
    
    def get_route_details(self, route_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific route.
        
        Args:
            route_id: Route ID from quote response
            
        Returns:
            Route details
            
        Raises:
            JupiterAPIError: If API request fails
        """
        # Note: This endpoint might not exist in the current Jupiter API
        # This is a placeholder for future implementation
        endpoint = f"{JUPITER_QUOTE_ENDPOINT}/route/{route_id}"
        
        try:
            response = self.session.get(endpoint, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise JupiterAPIError(f"Failed to get route details: {str(e)}")
    
    def get_token_list(self) -> List[Dict[str, Any]]:
        """
        Get list of supported tokens from Jupiter.
        
        Returns:
            List of token data
            
        Raises:
            JupiterAPIError: If API request fails
        """
        endpoint = "https://token.jup.ag/all"
        
        try:
            response = self.session.get(endpoint, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise JupiterAPIError(f"Failed to get token list: {str(e)}")
    
    def get_platform_list(self) -> List[Dict[str, Any]]:
        """
        Get list of supported platforms/DEXs from Jupiter.
        
        Returns:
            List of platform data
            
        Raises:
            JupiterAPIError: If API request fails
        """
        endpoint = "https://quote-api.jup.ag/v6/platforms"
        
        try:
            response = self.session.get(endpoint, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise JupiterAPIError(f"Failed to get platform list: {str(e)}")
    
    def test_connection(self) -> bool:
        """
        Test connection to Jupiter API.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Try a simple quote request with SOL to USDC
            test_quote = self.get_quote(
                input_mint="So11111111111111111111111111111111111111112",  # SOL
                output_mint="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
                amount=1_000_000,  # 1 SOL
                max_routes=1
            )
            return 'routes' in test_quote
        except:
            return False
    
    def get_api_status(self) -> Dict[str, Any]:
        """
        Get Jupiter API status and health information.
        
        Returns:
            API status information
            
        Raises:
            JupiterAPIError: If API request fails
        """
        # This is a placeholder - Jupiter might not have a dedicated status endpoint
        # We'll use the test connection approach
        try:
            start_time = time.time()
            is_healthy = self.test_connection()
            response_time = time.time() - start_time
            
            return {
                'status': 'healthy' if is_healthy else 'unhealthy',
                'response_time': response_time,
                'endpoint': JUPITER_QUOTE_ENDPOINT,
                'timestamp': time.time()
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'endpoint': JUPITER_QUOTE_ENDPOINT,
                'timestamp': time.time()
            } 