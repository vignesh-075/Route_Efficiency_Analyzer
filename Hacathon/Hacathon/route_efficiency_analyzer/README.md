# 🧭 Route Efficiency Analyzer

A Python tool to analyze and visualize the efficiency of token swap routes via Jupiter's Quote API on Solana.

## Features
- Input a token swap (e.g., SOL → USDC, amount)
- Fetches swap routes from Jupiter Quote API
- Analyzes:
  - Number of hops (route length)
  - Gas estimate (compute units)
  - Platforms/DEXs used (Orca, Raydium, etc.)
  - Minimum amount received (post-slippage)
  - Price impact
  - Comparison with alternative routes
- Outputs a detailed efficiency score and comparison table
- CLI output with `rich` (optionally Streamlit UI)

## Installation

1. Clone the repo and install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the analyzer:

```bash
python -m route_efficiency_analyzer.main SOL USDC 1.5 --slippage 0.5 --max-routes 5
```

## Usage

```
python -m route_efficiency_analyzer.main <input_token> <output_token> <amount> [--slippage <percent>] [--max-routes <N>] [--direct]
```

- `<input_token>`: Token symbol or mint address (e.g., SOL)
- `<output_token>`: Token symbol or mint address (e.g., USDC)
- `<amount>`: Amount to swap (e.g., 1.5)
- `--slippage`: Slippage percent (default: 0.5)
- `--max-routes`: Max number of routes to fetch (default: 5)
- `--direct`: Only show direct routes (no hops)

## Example

```
python -m route_efficiency_analyzer.main SOL USDC 1.5 --slippage 0.5 --max-routes 3
```

## Project Structure

- `main.py` - CLI entry point
- `jupiter_api.py` - Handles API requests
- `analyzer.py` - Route analysis logic
- `utils.py` - Utility functions
- `constants.py` - Token mints and config

## Why?
- Adds transparency to Jupiter's routing
- Educational for devs and DEX users
- Lightweight, modular, and extendable

## License
MIT 