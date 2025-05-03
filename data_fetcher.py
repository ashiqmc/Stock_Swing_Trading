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
            
        # Ensure we have a DatetimeIndex
        if not isinstance(data.index, pd.DatetimeIndex):
            st.warning(f"Converting index to DatetimeIndex for {stock}")
            # Try to convert the index to datetime if it's not already
            try:
                data.index = pd.to_datetime(data.index)
            except:
                st.error("Could not convert index to datetime format")
                
        return data
    except Exception as e:
        st.error(f"❌ Error fetching data for {stock}: {e}")
        return None