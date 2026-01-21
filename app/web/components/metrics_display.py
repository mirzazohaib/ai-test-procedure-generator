"""Metrics UI Component"""
import streamlit as st
from app.utils.currency import get_usd_to_eur_rate

def display_metrics(metadata: dict):
    """
    Renders the cost and performance metrics in the sidebar or main view.
    Uses cached API calls to convert USD costs to EUR dynamically.
    """
    st.markdown("### 📊 Generation Metrics")
    
    # 1. Get Dynamic Rate (Cached)
    # This fetches the live rate once per day to keep performance high
    rate = get_usd_to_eur_rate()
    
    # 2. Calculate Costs
    raw_cost_usd = metadata.get('cost_usd', 0.0)
    cost_eur = raw_cost_usd * rate
    
    # 3. Render Top Metrics (Cost & Time)
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            "Cost", 
            f"€{cost_eur:.4f}", 
            help=f"Live Rate: 1 USD = {rate:.2f} EUR\n(Original Cost: ${raw_cost_usd:.4f})"
        )
    with col2:
        st.metric(
            "Time", 
            f"{metadata.get('generation_time_sec', 0.0):.2f}s",
            help="Total time for AI generation"
        )
    
    # 4. Token Usage Breakdown
    tokens = metadata.get('tokens', {})
    if tokens:
        st.caption("Token Usage")
        # Visual progress bar (normalized to 4096 tokens for context)
        st.progress(
            min(tokens.get('total', 0) / 4096, 1.0), 
            text=f"Total Tokens: {tokens.get('total', 0)}"
        )
        
        # Detailed breakdown
        t1, t2 = st.columns(2)
        t1.caption(f"Input: {tokens.get('input', 0)}")
        t2.caption(f"Output: {tokens.get('output', 0)}")
    
    st.divider()
    
    # 5. Model & Version Info
    st.caption(f"Model: `{metadata.get('model', 'unknown')}`")
    st.caption(f"Prompt Version: `{metadata.get('prompt_version', 'unknown')}`")