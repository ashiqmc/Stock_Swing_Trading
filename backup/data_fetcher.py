import streamlit as st
import yfinance as yf
import pandas as pd

def fetch_stock_data(stock):
    """
    Safely fetch stock data from Yahoo Finance API
    
    Args:
        stock (str): Stock symbol
    
    Returns:
        pandas.DataFrame or None: DataFrame with stock data or None if error
    """
    try:
        data = yf.download(stock, period="6mo", interval="1d")
        if data.empty:
            st.error(f"❌ No data found for {stock}. Please try another stock.")
            return None
        return data
    except Exception as e:
        st.error(f"❌ Error fetching data for {stock}: {e}")
        return None