"""
🧭 Jupiter Smart Swap - Complete Demo Application
Shows what the integration would look like in Jupiter's mobile app.
"""

import streamlit as st
import requests
import json
import time
import asyncio
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Jupiter Smart Swap Demo",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for mobile app-like styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .mode-card {
        background: white;
        border: 2px solid #e0e0e0;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .success-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    .route-card {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .metric-box {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        margin: 0.5rem;
    }
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Mock data for demo
MOCK_ROUTES = [
    {
        "route_id": "route_1",
        "out_amount": 1000000,
        "hops": 1,
        "platforms": ["Raydium"],
        "price_impact": 0.001,
        "efficiency_score": 0.999,
        "compute_units": 5000,
        "time_to_route": 150,
        "gas_estimate": 0.005,
        "total_fee": 0.05
    },
    {
        "route_id": "route_2",
        "out_amount": 980000,
        "hops": 1,
        "platforms": ["Orca"],
        "price_impact": 0.002,
        "efficiency_score": 0.998,
        "compute_units": 3000,
        "time_to_route": 100,
        "gas_estimate": 0.003,
        "total_fee": 0.03
    },
    {
        "route_id": "route_3",
        "out_amount": 975000,
        "hops": 2,
        "platforms": ["Raydium", "Serum"],
        "price_impact": 0.003,
        "efficiency_score": 0.997,
        "compute_units": 8000,
        "time_to_route": 200,
        "gas_estimate": 0.008,
        "total_fee": 0.08
    }
]

# Token options
TOKENS = {
    "SOL": "So11111111111111111111111111111111111111112",
    "USDC": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
    "USDT": "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
    "RAY": "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R",
    "SRM": "SRMuApVNdxXokk5GT7XD5cUUgXMBCoAz2LHeuAoKWRt"
}

def main_header():
    """Main header section"""
    st.markdown("""
    <div class="main-header">
        <h1>🧭 Jupiter Smart Swap</h1>
        <p>Route Efficiency Analyzer & Auto-Swap Engine</p>
        <p><em>Demo: What Jupiter Mobile App Integration Would Look Like</em></p>
    </div>
    """, unsafe_allow_html=True)

def token_input_section():
    """Token input section"""
    st.markdown("### 📊 Swap Configuration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        input_token = st.selectbox("From Token", list(TOKENS.keys()), index=0)
        amount = st.number_input("Amount", min_value=0.01, value=1.0, step=0.1)
    
    with col2:
        output_token = st.selectbox("To Token", list(TOKENS.keys()), index=1)
        slippage = st.slider("Slippage (%)", 0.01, 5.0, 0.5, 0.01)
    
    with col3:
        max_routes = st.slider("Max Routes", 1, 10, 5)
        demo_mode = st.checkbox("Demo Mode", value=True, help="Use mock data for demonstration")
    
    return {
        "input_token": input_token,
        "output_token": output_token,
        "amount": amount,
        "slippage": slippage,
        "max_routes": max_routes,
        "demo_mode": demo_mode
    }

def mode_selection():
    """Mode selection section"""
    st.markdown("### 🎯 Select Operation Mode")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Analyze Only", use_container_width=True):
            st.session_state.mode = "analyze"
    
    with col2:
        if st.button("🤖 Auto-Swap", use_container_width=True):
            st.session_state.mode = "auto_swap"
    
    with col3:
        if st.button("✋ Manual Mode", use_container_width=True):
            st.session_state.mode = "manual"
    
    return st.session_state.get("mode", "analyze")

def analyze_routes(config):
    """Analyze routes using backend API or mock data"""
    if config["demo_mode"]:
        # Use mock data
        time.sleep(1)  # Simulate API delay
        return {
            "success": True,
            "message": f"Found {len(MOCK_ROUTES)} routes for {config['amount']} {config['input_token']} → {config['output_token']}",
            "mode": "analyze_only",
            "total_routes_found": len(MOCK_ROUTES),
            "best_route": MOCK_ROUTES[0],
            "all_routes": MOCK_ROUTES,
            "demo_mode": True
        }
    else:
        # Call real backend API
        try:
            response = requests.post(
                "http://localhost:8000/api/v1/analyze",
                json={
                    "input_mint": TOKENS[config["input_token"]],
                    "output_mint": TOKENS[config["output_token"]],
                    "amount": int(config["amount"] * 1_000_000),  # Convert to lamports
                    "slippage_bps": int(config["slippage"] * 100),
                    "demo_mode": False
                }
            )
            return response.json()
        except:
            st.error("Backend API not available. Please run the backend server first.")
            return None

def execute_auto_swap(config):
    """Execute auto-swap"""
    if config["demo_mode"]:
        # Simulate auto-swap
        time.sleep(2)  # Simulate transaction time
        return {
            "success": True,
            "message": "Auto-swap executed successfully!",
            "mode": "auto_swap",
            "total_routes_found": len(MOCK_ROUTES),
            "best_route": MOCK_ROUTES[0],
            "selected_route": MOCK_ROUTES[0],
            "swap_result": {
                "success": True,
                "txid": "demo_tx_" + str(int(time.time())),
                "route_used": MOCK_ROUTES[0]["route_id"],
                "amount_out": MOCK_ROUTES[0]["out_amount"]
            },
            "demo_mode": True
        }
    else:
        # Call real backend API
        try:
            response = requests.post(
                "http://localhost:8000/api/v1/auto-swap",
                json={
                    "input_mint": TOKENS[config["input_token"]],
                    "output_mint": TOKENS[config["output_token"]],
                    "amount": int(config["amount"] * 1_000_000),
                    "slippage_bps": int(config["slippage"] * 100),
                    "user_public_key": "demo_user_123",
                    "demo_mode": False
                }
            )
            return response.json()
        except:
            st.error("Backend API not available. Please run the backend server first.")
            return None

def display_route_analysis(response, config):
    """Display route analysis results"""
    if not response or not response.get("success"):
        st.error("Failed to analyze routes. Please try again.")
        return
    
    st.markdown("### 📈 Route Analysis Results")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-box">
            <h4>Routes Found</h4>
            <h2>{response['total_routes_found']}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        best_route = response.get("best_route", {})
        st.markdown(f"""
        <div class="metric-box">
            <h4>Best Efficiency</h4>
            <h2>{best_route.get('efficiency_score', 0):.3f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-box">
            <h4>Output Amount</h4>
            <h2>{best_route.get('out_amount', 0) / 1_000_000:.2f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-box">
            <h4>Price Impact</h4>
            <h2>{best_route.get('price_impact', 0) * 100:.2f}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Route comparison chart
    if response.get("all_routes"):
        routes_df = pd.DataFrame(response["all_routes"])
        
        # Efficiency comparison
        fig = px.bar(
            routes_df, 
            x="route_id", 
            y="efficiency_score",
            title="Route Efficiency Comparison",
            color="efficiency_score",
            color_continuous_scale="viridis"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed route cards
        st.markdown("### 🔍 Detailed Route Analysis")
        for i, route in enumerate(response["all_routes"]):
            with st.expander(f"Route {i+1}: {route['route_id']} (Efficiency: {route['efficiency_score']:.3f})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Platforms:** {', '.join(route['platforms'])}")
                    st.write(f"**Hops:** {route['hops']}")
                    st.write(f"**Output Amount:** {route['out_amount'] / 1_000_000:.6f} {config['output_token']}")
                
                with col2:
                    st.write(f"**Price Impact:** {route['price_impact'] * 100:.3f}%")
                    st.write(f"**Gas Estimate:** {route['gas_estimate']:.6f} SOL")
                    st.write(f"**Total Fee:** {route['total_fee']:.6f} SOL")

def display_auto_swap_result(response, config):
    """Display auto-swap results"""
    if not response or not response.get("success"):
        st.error("Auto-swap failed. Please try again.")
        return
    
    st.markdown("### 🤖 Auto-Swap Results")
    
    # Success card
    st.markdown(f"""
    <div class="success-card">
        <h3>✅ Swap Executed Successfully!</h3>
        <p><strong>Transaction ID:</strong> {response.get('swap_result', {}).get('txid', 'N/A')}</p>
        <p><strong>Route Used:</strong> {response.get('selected_route', {}).get('route_id', 'N/A')}</p>
        <p><strong>Amount Out:</strong> {response.get('selected_route', {}).get('out_amount', 0) / 1_000_000:.6f} {config['output_token']}</p>
        <p><strong>Efficiency Score:</strong> {response.get('selected_route', {}).get('efficiency_score', 0):.3f}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Transaction details
    st.markdown("### 📋 Transaction Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Input Amount:** {config['amount']} {config['input_token']}")
        st.write(f"**Output Amount:** {response.get('selected_route', {}).get('out_amount', 0) / 1_000_000:.6f} {config['output_token']}")
        st.write(f"**Slippage Used:** {config['slippage']}%")
    
    with col2:
        st.write(f"**Platforms Used:** {', '.join(response.get('selected_route', {}).get('platforms', []))}")
        st.write(f"**Gas Paid:** {response.get('selected_route', {}).get('gas_estimate', 0):.6f} SOL")
        st.write(f"**Total Fee:** {response.get('selected_route', {}).get('total_fee', 0):.6f} SOL")

def display_manual_mode(response, config):
    """Display manual mode for route selection"""
    if not response or not response.get("success"):
        st.error("Failed to fetch routes for manual selection.")
        return
    
    st.markdown("### ✋ Manual Route Selection")
    st.info("Select a route manually from the options below:")
    
    if response.get("all_routes"):
        selected_route = st.selectbox(
            "Choose Route:",
            options=response["all_routes"],
            format_func=lambda x: f"Route {x['route_id']} - Efficiency: {x['efficiency_score']:.3f} - {', '.join(x['platforms'])}"
        )
        
        if selected_route:
            st.markdown("### 📊 Selected Route Details")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Route ID:** {selected_route['route_id']}")
                st.write(f"**Platforms:** {', '.join(selected_route['platforms'])}")
                st.write(f"**Hops:** {selected_route['hops']}")
                st.write(f"**Efficiency Score:** {selected_route['efficiency_score']:.3f}")
            
            with col2:
                st.write(f"**Output Amount:** {selected_route['out_amount'] / 1_000_000:.6f} {config['output_token']}")
                st.write(f"**Price Impact:** {selected_route['price_impact'] * 100:.3f}%")
                st.write(f"**Gas Estimate:** {selected_route['gas_estimate']:.6f} SOL")
                st.write(f"**Total Fee:** {selected_route['total_fee']:.6f} SOL")
            
            # Execute button
            if st.button("🚀 Execute Selected Route", type="primary"):
                with st.spinner("Executing swap..."):
                    time.sleep(2)  # Simulate execution
                    st.success(f"Swap executed using {selected_route['route_id']}!")
                    st.balloons()

def main():
    """Main application"""
    main_header()
    
    # Initialize session state
    if "mode" not in st.session_state:
        st.session_state.mode = "analyze"
    
    # Get configuration
    config = token_input_section()
    
    # Mode selection
    mode = mode_selection()
    
    # Process based on mode
    if mode == "analyze":
        if st.button("🔍 Analyze Routes", type="primary"):
            with st.spinner("Analyzing routes..."):
                response = analyze_routes(config)
                display_route_analysis(response, config)
    
    elif mode == "auto_swap":
        if st.button("🤖 Execute Auto-Swap", type="primary"):
            with st.spinner("Executing auto-swap..."):
                response = execute_auto_swap(config)
                display_auto_swap_result(response, config)
    
    elif mode == "manual":
        if st.button("📋 Get Routes for Manual Selection", type="primary"):
            with st.spinner("Fetching routes..."):
                response = analyze_routes(config)
                display_manual_mode(response, config)
    
    # Demo information
    if config["demo_mode"]:
        st.markdown("---")
        st.info("🎭 **Demo Mode Active**: This is using mock data to simulate the Jupiter API integration. In production, this would connect to real Jupiter API endpoints.")

if __name__ == "__main__":
    main() 