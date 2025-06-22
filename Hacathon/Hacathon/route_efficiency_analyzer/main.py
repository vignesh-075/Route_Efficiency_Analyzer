"""
Main CLI entry point for the Route Efficiency Analyzer
Handles user input, fetches routes, analyzes, and outputs results.
"""

import argparse
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from .jupiter_api import JupiterAPIClient, JupiterAPIError
from .analyzer import analyze_routes, get_top_routes
from .utils import (
    parse_token_input, validate_amount, get_token_symbol, create_comparison_table, get_color_for_score
)
from .constants import DEFAULT_SLIPPAGE_BPS, DEFAULT_MAX_ROUTES

console = Console()

def main():
    parser = argparse.ArgumentParser(
        description="🧭 Route Efficiency Analyzer: Analyze and compare Jupiter swap routes on Solana"
    )
    parser.add_argument("input_token", help="Input token symbol or mint address (e.g., SOL)")
    parser.add_argument("output_token", help="Output token symbol or mint address (e.g., USDC)")
    parser.add_argument("amount", help="Amount to swap (e.g., 1.5)")
    parser.add_argument("--slippage", type=float, default=DEFAULT_SLIPPAGE_BPS / 100.0, help="Slippage percent (default: 0.5)")
    parser.add_argument("--max-routes", type=int, default=DEFAULT_MAX_ROUTES, help="Max number of routes to fetch (default: 5)")
    parser.add_argument("--direct", action="store_true", help="Only show direct routes (no hops)")
    args = parser.parse_args()

    try:
        input_mint = parse_token_input(args.input_token)
        output_mint = parse_token_input(args.output_token)
        amount = validate_amount(args.amount)
        slippage_bps = int(args.slippage * 100)  # percent to bps
        max_routes = args.max_routes
        only_direct_routes = args.direct
    except Exception as e:
        console.print(f"[red]Input error:[/red] {e}")
        return

    client = JupiterAPIClient()
    console.print(Panel(f"[bold]Fetching routes for[/bold] [cyan]{args.amount} {args.input_token}[/cyan] → [cyan]{args.output_token}[/cyan]...", title="Route Efficiency Analyzer", style="bold blue"))

    try:
        routes = client.get_swap_routes(
            input_mint=input_mint,
            output_mint=output_mint,
            amount=amount,
            slippage_bps=slippage_bps,
            max_routes=max_routes,
            only_direct_routes=only_direct_routes
        )
    except JupiterAPIError as e:
        console.print(f"[red]API error:[/red] {e}")
        return

    analyzed = analyze_routes(routes)
    top_routes = get_top_routes(analyzed, top_n=max_routes)
    table_data = create_comparison_table(top_routes)

    table = Table(title="Route Comparison", box=box.SIMPLE_HEAVY)
    table.add_column("Route #", style="bold")
    table.add_column("Out Amt", style="green")
    table.add_column("Hops", style="magenta")
    table.add_column("Platforms", style="cyan")
    table.add_column("Price Impact", style="yellow")
    table.add_column("Score", style="bold")

    for i, row in enumerate(table_data):
        score = float(row[-1])
        color = get_color_for_score(score)
        table.add_row(*row, style=color)

    console.print(table)

    best = top_routes[0]
    console.print(Panel(f"[bold green]Best Route:[/bold green] {best['hops']} hops, {', '.join(best['platforms'])}\n[bold]Out:[/bold] {row[1]} {get_token_symbol(output_mint)}\n[bold]Score:[/bold] {best['efficiency_score']:.4f}", title="Best Route", style="green"))

if __name__ == "__main__":
    main() 