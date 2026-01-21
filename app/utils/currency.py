"""
Currency conversion utilities with caching and fallback.
"""
import httpx
import streamlit as st
from app.utils.logging import get_logger

logger = get_logger(__name__)

# Fallback in case API fails
DEFAULT_USD_TO_EUR = 0.95
API_URL = "https://open.er-api.com/v6/latest/USD"

@st.cache_data(ttl=3600 * 24)  # Cache for 24 hours
def get_usd_to_eur_rate() -> float:
    """
    Fetches the live USD -> EUR conversion rate.
    Returns default rate if API call fails.
    """
    try:
        with httpx.Client(timeout=3.0) as client:
            response = client.get(API_URL)
            response.raise_for_status()
            data = response.json()
            
            rate = data.get("rates", {}).get("EUR")
            if rate:
                logger.info(f"Updated currency rate: 1 USD = {rate} EUR")
                return float(rate)
            
    except Exception as e:
        logger.warning(f"Failed to fetch live currency rate: {e}. Using fallback.")
    
    return DEFAULT_USD_TO_EUR