"""
Utility functions for the Route Efficiency Analyzer
Contains helper functions for formatting, conversions, and data processing.
"""

import re
from typing import Dict, List, Optional, Union
from .constants import TOKEN_MINTS, PLATFORM_NAMES, CLI_COLORS


def format_token_amount(amount: int, decimals: int = 6) -> str:
    """
    Format token amount from raw units to human-readable format.
    
    Args:
        amount: Raw token amount (e.g., lamports for SOL)
        decimals: Number of decimal places for the token
        
    Returns:
        Formatted string with appropriate decimal places
    """
    if amount == 0:
        return "0"
    
    # Convert to float and format
    formatted_amount = amount / (10 ** decimals)
    
    # Handle different precision levels
    if formatted_amount >= 1:
        return f"{formatted_amount:,.6f}".rstrip('0').rstrip('.')
    elif formatted_amount >= 0.001:
        return f"{formatted_amount:.6f}".rstrip('0').rstrip('.')
    else:
        return f"{formatted_amount:.8f}".rstrip('0').rstrip('.')


def format_usd_amount(amount: float) -> str:
    """
    Format USD amounts with appropriate precision.
    
    Args:
        amount: USD amount as float
        
    Returns:
        Formatted USD string
    """
    if amount >= 1:
        return f"${amount:,.2f}"
    elif amount >= 0.01:
        return f"${amount:.4f}"
    else:
        return f"${amount:.6f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format percentage values.
    
    Args:
        value: Percentage as decimal (e.g., 0.05 for 5%)
        decimals: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    return f"{value * 100:.{decimals}f}%"


def parse_token_input(token_input: str) -> str:
    """
    Parse token input which could be a symbol or mint address.
    
    Args:
        token_input: Token symbol (e.g., 'SOL') or mint address
        
    Returns:
        Mint address string
        
    Raises:
        ValueError: If token symbol is not recognized
    """
    # Check if it's already a mint address (base58 format)
    if re.match(r'^[1-9A-HJ-NP-Za-km-z]{32,44}$', token_input):
        return token_input
    
    # Check if it's a known token symbol
    token_input_upper = token_input.upper()
    if token_input_upper in TOKEN_MINTS:
        return TOKEN_MINTS[token_input_upper]
    
    raise ValueError(f"Unknown token: {token_input}. Available tokens: {', '.join(TOKEN_MINTS.keys())}")


def get_token_symbol(mint_address: str) -> str:
    """
    Get token symbol from mint address.
    
    Args:
        mint_address: Token mint address
        
    Returns:
        Token symbol or mint address if not found
    """
    for symbol, mint in TOKEN_MINTS.items():
        if mint == mint_address:
            return symbol
    return mint_address[:8] + "..."  # Truncate long addresses


def format_platform_name(platform: str) -> str:
    """
    Format platform name for display.
    
    Args:
        platform: Raw platform identifier
        
    Returns:
        Formatted platform name
    """
    return PLATFORM_NAMES.get(platform.lower(), platform.title())


def calculate_route_efficiency_score(
    out_amount: int,
    hops: int,
    price_impact: float,
    platforms: List[str],
    slippage_bps: int
) -> float:
    """
    Calculate a comprehensive efficiency score for a route.
    
    Args:
        out_amount: Output amount in raw units
        hops: Number of hops in the route
        price_impact: Price impact as decimal
        platforms: List of platforms used
        slippage_bps: Slippage in basis points
        
    Returns:
        Efficiency score (higher is better)
    """
    from .constants import (
        HOP_WEIGHT, PRICE_IMPACT_WEIGHT, 
        PLATFORM_DIVERSITY_WEIGHT, SLIPPAGE_WEIGHT
    )
    
    # Normalize out_amount (assuming 6 decimals for most tokens)
    normalized_amount = out_amount / 1_000_000
    
    # Hop efficiency (fewer hops is better)
    hop_score = 1.0 / max(hops, 1)
    
    # Price impact efficiency (lower impact is better)
    price_impact_score = 1.0 - min(price_impact, 1.0)
    
    # Platform diversity (more diverse is better, but not too many)
    platform_diversity = min(len(set(platforms)) / max(hops, 1), 1.0)
    
    # Slippage efficiency (lower slippage is better)
    slippage_score = 1.0 - (slippage_bps / 10000)
    
    # Calculate weighted score
    efficiency_score = (
        hop_score * HOP_WEIGHT +
        price_impact_score * PRICE_IMPACT_WEIGHT +
        platform_diversity * PLATFORM_DIVERSITY_WEIGHT +
        slippage_score * SLIPPAGE_WEIGHT
    )
    
    return efficiency_score


def validate_amount(amount: str) -> int:
    """
    Validate and convert amount string to integer.
    
    Args:
        amount: Amount as string (can include decimals)
        
    Returns:
        Amount as integer in raw units
        
    Raises:
        ValueError: If amount is invalid
    """
    try:
        # Handle decimal amounts
        if '.' in amount:
            parts = amount.split('.')
            if len(parts) != 2:
                raise ValueError("Invalid decimal format")
            
            whole, decimal = parts
            if not whole.isdigit() or not decimal.isdigit():
                raise ValueError("Invalid number format")
            
            # Convert to raw units (assuming 6 decimals)
            raw_amount = int(whole) * 1_000_000 + int(decimal.ljust(6, '0')[:6])
        else:
            raw_amount = int(amount) * 1_000_000
        
        if raw_amount <= 0:
            raise ValueError("Amount must be positive")
        
        return raw_amount
    
    except ValueError as e:
        if "Invalid" in str(e):
            raise e
        raise ValueError("Invalid amount format")


def format_route_summary(route_data: Dict) -> Dict:
    """
    Format route data for display.
    
    Args:
        route_data: Raw route data from Jupiter API
        
    Returns:
        Formatted route summary
    """
    platforms = []
    for step in route_data.get('swapSteps', []):
        platform = step.get('platform', 'unknown')
        platforms.append(format_platform_name(platform))
    
    return {
        'route_id': route_data.get('routeId', 'N/A'),
        'out_amount': route_data.get('outAmount', 0),
        'hops': len(route_data.get('swapSteps', [])),
        'platforms': list(set(platforms)),
        'price_impact': route_data.get('priceImpact', 0),
        'slippage_bps': route_data.get('slippageBps', 0),
        'compute_units': route_data.get('computeUnits', 0),
        'time_to_route': route_data.get('timeToRoute', 0),
    }


def create_comparison_table(routes: List[Dict]) -> List[List]:
    """
    Create a comparison table for multiple routes.
    
    Args:
        routes: List of formatted route data
        
    Returns:
        Table data as list of lists
    """
    table_data = []
    
    for i, route in enumerate(routes, 1):
        efficiency_score = calculate_route_efficiency_score(
            route['out_amount'],
            route['hops'],
            route['price_impact'],
            route['platforms'],
            route['slippage_bps']
        )
        
        table_data.append([
            f"Route {i}",
            format_token_amount(route['out_amount']),
            route['hops'],
            ", ".join(route['platforms']),
            format_percentage(route['price_impact']),
            f"{efficiency_score:.4f}"
        ])
    
    return table_data


def get_color_for_score(score: float) -> str:
    """
    Get color for efficiency score.
    
    Args:
        score: Efficiency score (0-1)
        
    Returns:
        Color name for CLI display
    """
    if score >= 0.8:
        return CLI_COLORS['success']
    elif score >= 0.6:
        return CLI_COLORS['info']
    elif score >= 0.4:
        return CLI_COLORS['warning']
    else:
        return CLI_COLORS['error'] 