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

# Add a toggle for demo mode
demo_mode = st.sidebar.checkbox("Demo Mode (Use Mock Data)", value=True)

if demo_mode:
    st.sidebar.info("🔧 Demo Mode: Using sample data since Jupiter API is currently not returning routes.")

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
    if demo_mode:
        # Mock data for demonstration
        st.success("🎭 Demo Mode: Showing sample route analysis")
        
        # Create mock route data
        mock_routes = [
            {
                'routeId': 'mock_route_1',
                'outAmount': 1500000,  # 1.5 USDC
                'priceImpact': 0.001,  # 0.1%
                'slippageBps': 50,
                'computeUnits': 200000,
                'timeToRoute': 150,
                'swapSteps': [
                    {'platform': 'orca'},
                    {'platform': 'raydium'}
                ]
            },
            {
                'routeId': 'mock_route_2',
                'outAmount': 1495000,  # 1.495 USDC
                'priceImpact': 0.002,  # 0.2%
                'slippageBps': 50,
                'computeUnits': 180000,
                'timeToRoute': 120,
                'swapSteps': [
                    {'platform': 'orca'}
                ]
            },
            {
                'routeId': 'mock_route_3',
                'outAmount': 1488000,  # 1.488 USDC
                'priceImpact': 0.003,  # 0.3%
                'slippageBps': 50,
                'computeUnits': 220000,
                'timeToRoute': 180,
                'swapSteps': [
                    {'platform': 'serum'},
                    {'platform': 'lifinity'},
                    {'platform': 'raydium'}
                ]
            }
        ]
        
        analyzed = analyze_routes(mock_routes)
        top_routes = get_top_routes(analyzed, top_n=max_routes)
        table_data = create_comparison_table(top_routes)
        
        st.success(f"Found {len(top_routes)} route(s) for {amount} {input_token} → {output_token}")
        
        # Display results in a nice table
        st.subheader("Route Comparison")
        st.table(
            {"Route #": [row[0] for row in table_data],
             "Out Amt": [row[1] for row in table_data],
             "Hops": [row[2] for row in table_data],
             "Platforms": [row[3] for row in table_data],
             "Price Impact": [row[4] for row in table_data],
             "Score": [row[5] for row in table_data]}
        )
        
        best = top_routes[0]
        st.subheader("Best Route")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Hops", best['hops'])
        with col2:
            st.metric("Platforms", ", ".join(best['platforms']))
        with col3:
            st.metric("Efficiency Score", f"{best['efficiency_score']:.4f}")
        
        st.info("💡 This is demo data. When Jupiter API is working, you'll see real route data here.")
        
    else:
        # Real API call
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

# Add some helpful information
st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.markdown("This tool analyzes Jupiter swap routes for efficiency based on:")
st.sidebar.markdown("- Number of hops")
st.sidebar.markdown("- Price impact")
st.sidebar.markdown("- Platform diversity")
st.sidebar.markdown("- Slippage tolerance")

st.sidebar.markdown("### Current Status")
if demo_mode:
    st.sidebar.warning("🔧 Demo Mode Active")
else:
    st.sidebar.info("🌐 Live API Mode") 