"""
Constants for the Route Efficiency Analyzer
Contains common Solana token mint addresses and configuration settings.
"""

# Common Solana Token Mint Addresses
TOKEN_MINTS = {
    "SOL": "So11111111111111111111111111111111111111112",
    "USDC": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "USDT": "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
    "RAY": "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R",
    "SRM": "SRMuApVNdxXokk5GT7XD5cUUgXMBCoAz2LHeuAoKWRt",
    "ORCA": "orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE",
    "BONK": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
    "JUP": "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN",
    "PYTH": "HZ1JovNiVvGrGNiiYvEozEVgZ58xaU3RKwX8eACQBCt3",
    "WIF": "EKpQGSJtjMFqKZ1KQanSqYXRcF8fBopzLHYxdM65Qjm",
}

# Jupiter API Configuration
JUPITER_QUOTE_API_BASE = "https://quote-api.jup.ag/v6"
JUPITER_QUOTE_ENDPOINT = f"{JUPITER_QUOTE_API_BASE}/quote"

# Default Configuration
DEFAULT_SLIPPAGE_BPS = 50  # 0.5%
DEFAULT_MAX_ROUTES = 5
DEFAULT_ONLY_DIRECT_ROUTES = False

# Route Analysis Weights (for efficiency scoring)
HOP_WEIGHT = 0.3
PRICE_IMPACT_WEIGHT = 0.4
PLATFORM_DIVERSITY_WEIGHT = 0.2
SLIPPAGE_WEIGHT = 0.1

# Platform Names (for better display)
PLATFORM_NAMES = {
    "orca": "Orca",
    "raydium": "Raydium",
    "serum": "Serum",
    "lifinity": "Lifinity",
    "crema": "Crema",
    "mercurial": "Mercurial",
    "stepn": "STEPN",
    "saber": "Saber",
    "aldrin": "Aldrin",
    "cropper": "Cropper",
    "invariant": "Invariant",
    "goosefx": "GooseFX",
    "deltafi": "DeltaFi",
    "marinade": "Marinade",
    "step": "Step",
    "sencha": "Sencha",
    "saros": "Saros",
    "cykura": "Cykura",
    "phoenix": "Phoenix",
    "meteora": "Meteora",
    "openbook": "OpenBook",
    "balansol": "Balansol",
    "pump": "Pump",
    "whirlpool": "Whirlpool",
    "mango": "Mango",
    "dexlab": "Dexlab",
    "lifinity_v2": "Lifinity V2",
    "raydium_clmm": "Raydium CLMM",
    "orca_whirlpool": "Orca Whirlpool",
    "meteora_dlmm": "Meteora DLMM",
    "invariant_amm": "Invariant AMM",
    "goosefx_clmm": "GooseFX CLMM",
    "deltafi_clmm": "DeltaFi CLMM",
    "balansol_amm": "Balansol AMM",
    "crema_amm": "Crema AMM",
    "lifinity_amm": "Lifinity AMM",
    "raydium_amm": "Raydium AMM",
    "serum_amm": "Serum AMM",
    "stepn_amm": "STEPN AMM",
    "saber_amm": "Saber AMM",
    "aldrin_amm": "Aldrin AMM",
    "cropper_amm": "Cropper AMM",
    "step_amm": "Step AMM",
    "sencha_amm": "Sencha AMM",
    "saros_amm": "Saros AMM",
    "cykura_amm": "Cykura AMM",
    "phoenix_amm": "Phoenix AMM",
    "openbook_amm": "OpenBook AMM",
    "pump_amm": "Pump AMM",
    "mango_amm": "Mango AMM",
    "dexlab_amm": "Dexlab AMM",
}

# CLI Colors and Styling
CLI_COLORS = {
    "success": "green",
    "warning": "yellow",
    "error": "red",
    "info": "blue",
    "highlight": "cyan",
    "muted": "dim",
} 