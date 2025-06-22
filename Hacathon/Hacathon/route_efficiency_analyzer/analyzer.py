"""
Route Analyzer for the Route Efficiency Analyzer
Contains logic to evaluate, score, and compare swap routes.
"""

from typing import List, Dict, Any
from .utils import format_route_summary, calculate_route_efficiency_score


def analyze_routes(routes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Analyze and score each route.
    Args:
        routes: List of raw route data from Jupiter API
    Returns:
        List of route summaries with efficiency scores
    """
    analyzed = []
    for route in routes:
        summary = format_route_summary(route)
        score = calculate_route_efficiency_score(
            summary['out_amount'],
            summary['hops'],
            summary['price_impact'],
            summary['platforms'],
            summary['slippage_bps']
        )
        summary['efficiency_score'] = score
        analyzed.append(summary)
    return analyzed


def rank_routes(analyzed_routes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Rank routes by efficiency score (descending).
    Args:
        analyzed_routes: List of analyzed route summaries
    Returns:
        Sorted list of route summaries
    """
    return sorted(analyzed_routes, key=lambda r: r['efficiency_score'], reverse=True)


def get_top_routes(analyzed_routes: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
    """
    Get the top N routes by efficiency score.
    Args:
        analyzed_routes: List of analyzed route summaries
        top_n: Number of top routes to return
    Returns:
        Top N route summaries
    """
    ranked = rank_routes(analyzed_routes)
    return ranked[:top_n] 