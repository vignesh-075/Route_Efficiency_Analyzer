import streamlit as st
from route_efficiency_analyzer.utils import (
    parse_token_input, validate_amount, get_token_symbol, create_comparison_table
)
from route_efficiency_analyzer.constants import DEFAULT_SLIPPAGE_BPS, DEFAULT_MAX_ROUTES, TOKEN_MINTS
from route_efficiency_analyzer.jupiter_api import JupiterAPIClient, JupiterAPIError
from route_efficiency_analyzer.analyzer import analyze_routes, get_top_routes

st.set_page_config(page_title="🧭 Route Efficiency Analyzer", layout="centered")
st.title("🧭 Route Efficiency Analyzer (Jupiter)")
st.markdown("Analyze and compare Jupiter swap routes on Solana.")

with st.form("route_form"):
    col1, col2 = st.columns(2)
    with col1:
        input_token = st.selectbox("Input Token", list(TOKEN_MINTS.keys()), index=0)
    with col2:
        output_token = st.selectbox("Output Token", list(TOKEN_MINTS.keys()), index=1)
    amount = st.text_input("Amount to swap", "1.0")
    slippage = st.slider("Slippage (%)", min_value=0.01, max_value=5.0, value=DEFAULT_SLIPPAGE_BPS/100, step=0.01)
    max_routes = st.slider("Max Routes", min_value=1, max_value=10, value=DEFAULT_MAX_ROUTES)
    only_direct = st.checkbox("Only show direct routes (no hops)")
    submitted = st.form_submit_button("Analyze Routes")

if submitted:
    try:
        input_mint = parse_token_input(input_token)
        output_mint = parse_token_input(output_token)
        raw_amount = validate_amount(amount)
        slippage_bps = int(slippage * 100)
        client = JupiterAPIClient()
        with st.spinner("Fetching routes from Jupiter..."):
            routes = client.get_swap_routes(
                input_mint=input_mint,
                output_mint=output_mint,
                amount=raw_amount,
                slippage_bps=slippage_bps,
                max_routes=max_routes,
                only_direct_routes=only_direct
            )
        analyzed = analyze_routes(routes)
        top_routes = get_top_routes(analyzed, top_n=max_routes)
        table_data = create_comparison_table(top_routes)
        st.success(f"Found {len(top_routes)} route(s) for {amount} {input_token} → {output_token}")
        st.table(
            {"Route #": [row[0] for row in table_data],
             "Out Amt": [row[1] for row in table_data],
             "Hops": [row[2] for row in table_data],
             "Platforms": [row[3] for row in table_data],
             "Price Impact": [row[4] for row in table_data],
             "Score": [row[5] for row in table_data]}
        )
        best = top_routes[0]
        st.markdown(f"**Best Route:** {best['hops']} hops, {', '.join(best['platforms'])}<br>"
                    f"**Out:** {table_data[0][1]} {get_token_symbol(output_mint)}<br>"
                    f"**Score:** {best['efficiency_score']:.4f}", unsafe_allow_html=True)
    except JupiterAPIError as e:
        st.error(f"API error: {e}")
    except Exception as e:
        st.error(f"Input error: {e}") 