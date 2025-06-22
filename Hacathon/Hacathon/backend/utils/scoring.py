"""
Efficiency scoring algorithms for route analysis.
"""

from typing import List

def calculate_efficiency_score(hops: int, price_impact: float, platforms: List[str], slippage_bps: int) -> float:
    """
    Calculate efficiency score based on multiple factors.
    
    Args:
        hops: Number of hops in the route
        price_impact: Price impact as decimal
        platforms: List of platforms used
        slippage_bps: Slippage in basis points
        
    Returns:
        Efficiency score (0-1, higher is better)
    """
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
        hop_score * 0.3 +
        price_impact_score * 0.4 +
        platform_diversity * 0.2 +
        slippage_score * 0.1
    )
    
    return efficiency_score

def calculate_speed_score(hops: int, time_to_route: int, compute_units: int) -> float:
    """
    Calculate score based on speed (fewer hops, faster routing, lower compute).
    
    Args:
        hops: Number of hops
        time_to_route: Time to route in milliseconds
        compute_units: Compute units required
        
    Returns:
        Speed score (0-1, higher is better)
    """
    hop_score = 1.0 / max(hops, 1)
    time_score = 1.0 / max(time_to_route, 1)
    compute_score = 1.0 / max(compute_units / 1000, 1)
    
    return (hop_score * 0.5 + time_score * 0.3 + compute_score * 0.2)

def calculate_cost_score(price_impact: float, compute_units: int, out_amount: int) -> float:
    """
    Calculate score based on cost (lower price impact, lower gas).
    
    Args:
        price_impact: Price impact as decimal
        compute_units: Compute units required
        out_amount: Output amount in raw units
        
    Returns:
        Cost score (0-1, higher is better)
    """
    price_score = 1.0 - min(price_impact, 1.0)
    gas_score = 1.0 / max(compute_units / 1000, 1)
    amount_score = out_amount / 1_000_000  # Normalize by amount
    
    return (price_score * 0.6 + gas_score * 0.3 + amount_score * 0.1)

def get_score_by_criteria(criteria: str, hops: int, price_impact: float, platforms: List[str], 
                         slippage_bps: int, time_to_route: int, compute_units: int, out_amount: int) -> float:
    """
    Get score based on specified criteria.
    
    Args:
        criteria: "efficiency", "speed", or "cost"
        hops: Number of hops
        price_impact: Price impact as decimal
        platforms: List of platforms
        slippage_bps: Slippage in basis points
        time_to_route: Time to route in milliseconds
        compute_units: Compute units required
        out_amount: Output amount in raw units
        
    Returns:
        Score based on criteria (0-1, higher is better)
    """
    if criteria == "efficiency":
        return calculate_efficiency_score(hops, price_impact, platforms, slippage_bps)
    elif criteria == "speed":
        return calculate_speed_score(hops, time_to_route, compute_units)
    elif criteria == "cost":
        return calculate_cost_score(price_impact, compute_units, out_amount)
    else:
        # Default to efficiency
        return calculate_efficiency_score(hops, price_impact, platforms, slippage_bps) 