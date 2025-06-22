"""
🧭 Route Efficiency Analyzer - Jupiter Swap Intelligence
Visualize, compare, and understand Jupiter's routing decisions with educational insights.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import requests
import json
import time
from datetime import datetime
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Route Efficiency Analyzer",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for creative UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .route-card {
        background: white;
        border: 2px solid #e0e0e0;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    .route-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    .best-route {
        border: 3px solid #4CAF50;
        background: linear-gradient(135deg, #f0f8f0 0%, #e8f5e8 100%);
    }
    .insight-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    .metric-box {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        margin: 0.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    .route-visualization {
        background: #f8f9fa;
        border-radius: 15px;
        padding: 2rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Mock data with detailed route information
MOCK_ROUTES_DETAILED = [
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
        "total_fee": 0.05,
        "route_path": ["SOL", "USDC"],
        "liquidity_pools": ["Raydium SOL-USDC"],
        "reasoning": "Direct route with highest liquidity and lowest price impact",
        "advantages": ["Lowest price impact", "Fastest execution", "Single hop"],
        "disadvantages": ["Slightly higher gas fees"],
        "risk_level": "Low",
        "recommendation": "Best choice for this swap"
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
        "total_fee": 0.03,
        "route_path": ["SOL", "USDC"],
        "liquidity_pools": ["Orca SOL-USDC"],
        "reasoning": "Alternative DEX with lower gas fees but higher price impact",
        "advantages": ["Lower gas fees", "Good liquidity"],
        "disadvantages": ["Higher price impact", "Slightly lower output"],
        "risk_level": "Low",
        "recommendation": "Good alternative if gas fees are priority"
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
        "total_fee": 0.08,
        "route_path": ["SOL", "RAY", "USDC"],
        "liquidity_pools": ["Raydium SOL-RAY", "Serum RAY-USDC"],
        "reasoning": "Multi-hop route using intermediate token for better liquidity distribution",
        "advantages": ["Better liquidity distribution", "Lower individual pool impact"],
        "disadvantages": ["Higher gas fees", "More complex", "Lower output"],
        "risk_level": "Medium",
        "recommendation": "Only use if direct routes fail"
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
    """Main header with project description"""
    st.markdown("""
    <div class="main-header">
        <h1>🧭 Route Efficiency Analyzer</h1>
        <h3>Jupiter Swap Intelligence & Route Visualization</h3>
        <p><em>Understand Jupiter's routing decisions with detailed analysis and visual insights</em></p>
    </div>
    """, unsafe_allow_html=True)

def create_route_visualization(route):
    """Create visual route map"""
    fig = go.Figure()
    
    # Create nodes
    nodes = route["route_path"]
    node_positions = {node: i for i, node in enumerate(nodes)}
    
    # Add nodes
    fig.add_trace(go.Scatter(
        x=[node_positions[node] for node in nodes],
        y=[0] * len(nodes),
        mode='markers+text',
        marker=dict(size=30, color='#667eea'),
        text=nodes,
        textposition="top center",
        name="Tokens"
    ))
    
    # Add edges (routes)
    for i in range(len(nodes) - 1):
        fig.add_trace(go.Scatter(
            x=[i, i + 1],
            y=[0, 0],
            mode='lines',
            line=dict(color='#764ba2', width=3),
            name=f"Route {i+1}",
            showlegend=False
        ))
    
    # Add platform labels
    for i, platform in enumerate(route["platforms"]):
        fig.add_annotation(
            x=i + 0.5,
            y=-0.2,
            text=platform,
            showarrow=False,
            font=dict(color="#764ba2", size=12)
        )
    
    fig.update_layout(
        title=f"Route Visualization: {' → '.join(route['route_path'])}",
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(showgrid=False, showticklabels=False),
        height=300,
        showlegend=False
    )
    
    return fig

def create_efficiency_radar_chart(routes):
    """Create radar chart comparing route efficiency metrics"""
    categories = ['Efficiency', 'Speed', 'Cost', 'Simplicity', 'Liquidity']
    
    fig = go.Figure()
    
    for route in routes:
        # Calculate radar values
        efficiency = route['efficiency_score']
        speed = 1 / (route['time_to_route'] / 100)  # Normalize speed
        cost = 1 - (route['total_fee'] / 0.1)  # Normalize cost
        simplicity = 1 / route['hops']  # Fewer hops = more simple
        liquidity = 1 - route['price_impact']  # Lower impact = more liquidity
        
        values = [efficiency, speed, cost, simplicity, liquidity]
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=f"Route {route['route_id']}",
            line_color='#667eea'
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=True,
        title="Route Efficiency Comparison (Radar Chart)"
    )
    
    return fig

def display_route_analysis_detailed(routes, config):
    """Display detailed route analysis with educational insights"""
    st.markdown("### 📊 Route Analysis Dashboard")
    
    # Summary metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="metric-box">
            <h4>Routes Found</h4>
            <h2>{len(routes)}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        best_route = max(routes, key=lambda x: x['efficiency_score'])
        st.markdown(f"""
        <div class="metric-box">
            <h4>Best Efficiency</h4>
            <h2>{best_route['efficiency_score']:.3f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-box">
            <h4>Best Output</h4>
            <h2>{best_route['out_amount'] / 1_000_000:.2f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-box">
            <h4>Lowest Impact</h4>
            <h2>{min(r['price_impact'] for r in routes) * 100:.2f}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="metric-box">
            <h4>Fastest Route</h4>
            <h2>{min(r['time_to_route'] for r in routes)}ms</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Route comparison charts
    st.markdown("### 📈 Route Comparison Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Efficiency comparison bar chart
        routes_df = pd.DataFrame(routes)
        fig_bar = px.bar(
            routes_df,
            x="route_id",
            y="efficiency_score",
            title="Route Efficiency Scores",
            color="efficiency_score",
            color_continuous_scale="viridis"
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        # Radar chart
        fig_radar = create_efficiency_radar_chart(routes)
        st.plotly_chart(fig_radar, use_container_width=True)
    
    # Detailed route cards with educational insights
    st.markdown("### 🔍 Detailed Route Analysis & Educational Insights")
    
    # Sort routes by efficiency
    sorted_routes = sorted(routes, key=lambda x: x['efficiency_score'], reverse=True)
    
    for i, route in enumerate(sorted_routes):
        is_best = i == 0
        
        with st.expander(f"Route {i+1}: {route['route_id']} {'🏆' if is_best else ''} (Efficiency: {route['efficiency_score']:.3f})", expanded=is_best):
            
            # Route visualization
            st.markdown("#### 🗺️ Route Visualization")
            fig_route = create_route_visualization(route)
            st.plotly_chart(fig_route, use_container_width=True)
            
            # Route details in columns
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("#### 📊 Route Metrics")
                st.write(f"**Platforms:** {', '.join(route['platforms'])}")
                st.write(f"**Hops:** {route['hops']}")
                st.write(f"**Output Amount:** {route['out_amount'] / 1_000_000:.6f} {config['output_token']}")
                st.write(f"**Price Impact:** {route['price_impact'] * 100:.3f}%")
                st.write(f"**Gas Estimate:** {route['gas_estimate']:.6f} SOL")
                st.write(f"**Total Fee:** {route['total_fee']:.6f} SOL")
                st.write(f"**Risk Level:** {route['risk_level']}")
            
            with col2:
                st.markdown("#### 🧠 Jupiter's Reasoning")
                st.info(route['reasoning'])
                
                st.markdown("#### ✅ Advantages")
                for advantage in route['advantages']:
                    st.write(f"• {advantage}")
                
                st.markdown("#### ⚠️ Disadvantages")
                for disadvantage in route['disadvantages']:
                    st.write(f"• {disadvantage}")
            
            with col3:
                st.markdown("#### 🎯 Recommendation")
                st.success(route['recommendation'])
                
                st.markdown("#### 🔗 Liquidity Pools")
                for pool in route['liquidity_pools']:
                    st.write(f"• {pool}")
                
                st.markdown("#### 📈 Performance Metrics")
                st.write(f"**Time to Route:** {route['time_to_route']}ms")
                st.write(f"**Compute Units:** {route['compute_units']}")
                st.write(f"**Route Path:** {' → '.join(route['route_path'])}")

def display_educational_insights(routes, config):
    """Display educational insights about Jupiter's routing logic"""
    st.markdown("### 🎓 Educational Insights: How Jupiter Makes Routing Decisions")
    
    # Best route analysis
    best_route = max(routes, key=lambda x: x['efficiency_score'])
    
    st.markdown(f"""
    <div class="insight-box">
        <h3>🏆 Why Jupiter Chose Route {best_route['route_id']} as Best</h3>
        <p><strong>Primary Factor:</strong> {best_route['reasoning']}</p>
        <p><strong>Efficiency Score:</strong> {best_route['efficiency_score']:.3f} (highest among all routes)</p>
        <p><strong>Key Advantage:</strong> {best_route['advantages'][0] if best_route['advantages'] else 'N/A'}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Route comparison insights
    st.markdown("#### 📊 Route Comparison Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🔍 Route Selection Factors:**")
        st.write("• **Price Impact:** Lower is better (affects output amount)")
        st.write("• **Gas Fees:** Lower is better (affects total cost)")
        st.write("• **Hops:** Fewer is better (faster execution)")
        st.write("• **Liquidity:** Higher is better (less slippage)")
        st.write("• **Platform Reliability:** Established DEXs preferred")
    
    with col2:
        st.markdown("**🎯 When Each Route Type is Best:**")
        st.write("• **Direct Routes:** Best for high liquidity pairs")
        st.write("• **Multi-hop Routes:** Better for low liquidity or complex swaps")
        st.write("• **Alternative DEXs:** Good when main DEX has high fees")
        st.write("• **Hybrid Routes:** Optimal for large amounts to minimize impact")
    
    # Risk analysis
    st.markdown("#### ⚠️ Risk Analysis")
    
    risk_levels = [route['risk_level'] for route in routes]
    if 'High' in risk_levels:
        st.warning("⚠️ Some routes have higher risk due to multiple hops or lower liquidity")
    elif 'Medium' in risk_levels:
        st.info("ℹ️ Some routes have moderate risk, suitable for experienced users")
    else:
        st.success("✅ All routes have low risk, safe for all users")

def main():
    """Main application"""
    main_header()
    
    # Sidebar configuration
    st.sidebar.markdown("### ⚙️ Configuration")
    
    input_token = st.sidebar.selectbox("From Token", list(TOKENS.keys()), index=0)
    output_token = st.sidebar.selectbox("To Token", list(TOKENS.keys()), index=1)
    amount = st.sidebar.number_input("Amount", min_value=0.01, value=1.0, step=0.1)
    slippage = st.sidebar.slider("Slippage (%)", 0.01, 5.0, 0.5, 0.01)
    demo_mode = st.sidebar.checkbox("Demo Mode", value=True, help="Use mock data for demonstration")
    
    config = {
        "input_token": input_token,
        "output_token": output_token,
        "amount": amount,
        "slippage": slippage,
        "demo_mode": demo_mode
    }
    
    # Main analysis button
    if st.button("🔍 Analyze Routes with Jupiter Intelligence", type="primary", use_container_width=True):
        with st.spinner("Analyzing routes with Jupiter's intelligence..."):
            time.sleep(2)  # Simulate analysis time
            
            # Use mock data for demo
            routes = MOCK_ROUTES_DETAILED
            
            # Display detailed analysis
            display_route_analysis_detailed(routes, config)
            
            # Display educational insights
            display_educational_insights(routes, config)
    
    # Demo information
    if demo_mode:
        st.sidebar.markdown("---")
        st.sidebar.info("🎭 **Demo Mode Active**: Using mock data to demonstrate route analysis capabilities.")
    
    # About section
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📚 About This Tool")
    st.sidebar.markdown("""
    This Route Efficiency Analyzer provides:
    
    • **Visual route mapping**
    • **Detailed efficiency analysis**
    • **Educational insights**
    • **Risk assessment**
    • **Jupiter routing logic explanation**
    
    Perfect for understanding how Jupiter makes routing decisions!
    """)

if __name__ == "__main__":
    main() 



# 🪙 Swap Simulator: SOL → USDC (Using Jupiter Aggregator API)
import requests
import streamlit as st

st.header("🔁 SOL → USDC Swap Simulator (Jupiter)")

SOL_MINT = "So11111111111111111111111111111111111111112"
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # ✅ Correct

sol_amount = st.number_input("Enter SOL amount to swap:", min_value=0.001, value=1.0, step=0.001)

if st.button("Get Swap Quote"):
    try:
        lamports = int(float(f"{sol_amount:.9f}") * 1e9)
        params = {
            "inputMint": SOL_MINT,
            "outputMint": USDC_MINT,
            "amount": str(lamports),
            "slippageBps": 100,  # 1% slippage
        }

        quote_url = "https://quote-api.jup.ag/v6/quote"
        query_url = requests.Request('GET', quote_url, params=params).prepare().url
        st.write("📡 Jupiter API URL:", query_url)

        resp = requests.get(query_url)

        if resp.status_code == 200:
           quote = resp.json()

# Validate if required fields exist
        if "outAmount" in quote and "routePlan" in quote:
            out_amount = int(quote["outAmount"]) / 1e6  # USDC has 6 decimals
            st.success(f"💸 Estimated Output: {out_amount:.4f} USDC")
    
            st.markdown("**Swap Route:**")
            st.write(f"⚙️ AMM: {quote['routePlan'][0]['swapInfo']['label']}")
            st.write(f"🔁 In: {int(quote['routePlan'][0]['swapInfo']['inAmount']) / 1e9} SOL")
            st.write(f"💰 Out: {int(quote['routePlan'][0]['swapInfo']['outAmount']) / 1e6} USDC")

            st.markdown("### 🧾 Full Quote JSON")
            st.json(quote)

        else:
            st.error("Jupiter returned a response, but it's missing route data.")

        #out_amount = int(best_route["outAmount"]) / 1e6  # USDC has 6 decimals
        #st.success(f"💸 Estimated Output: {out_amount:.4f} USDC")
        #st.json(best_route)
        #else:
        #st.warning("No routes found. Try a different amount.")
        #else:
            #st.error("Failed to fetch quote from Jupiter API.")
    except Exception as e:
        st.error(f"Error: {str(e)}")
