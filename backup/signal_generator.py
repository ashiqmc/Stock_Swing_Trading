import streamlit as st
import pandas as pd
import ta

from data_fetcher import fetch_stock_data

@st.cache_data
def get_signal(ticker):
    """
    Calculate technical indicators and generate trading signals
    
    Args:
        ticker (str): Stock symbol
        
    Returns:
        tuple or None: (signal, data, scores) or None if error
    """
    # Fetch data
    df = fetch_stock_data(ticker)
    
    if df is None:
        return None
    
    # Check for MultiIndex columns and flatten if needed
    if isinstance(df.columns, pd.MultiIndex):
        # Get the first level of column names
        col_names = [col[0] for col in df.columns]
        # Create a new DataFrame with flattened column names
        data = pd.DataFrame()
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            if (col, ticker) in df.columns:
                data[col] = df[(col, ticker)].values
    else:
        data = df.copy()
    
    # Make sure we have enough data points
    if len(data) < 50:
        st.error(f"Not enough data points for {ticker}")
        return None
    
    # Check required columns
    required_cols = ['Close', 'Volume']
    missing_cols = [col for col in required_cols if col not in data.columns]
    if missing_cols:
        st.error(f"Missing columns in {ticker} data: {missing_cols}")
        return None
    
    # Calculate indicators
    try:
        # Calculate technical indicators
        data["SMA_50"] = ta.trend.sma_indicator(data["Close"], window=50)
        data["SMA_200"] = ta.trend.sma_indicator(data["Close"], window=200)
        data["RSI"] = ta.momentum.rsi(data["Close"], window=14)
        data["MACD"] = ta.trend.macd(data["Close"])
        data["MACD_Signal"] = ta.trend.macd_signal(data["Close"])
        data["Upper_BB"] = ta.volatility.bollinger_hband(data["Close"])
        data["Lower_BB"] = ta.volatility.bollinger_lband(data["Close"])
        data["Volume_Change"] = data["Volume"].pct_change()
        
        # Fill any missing values
        data.fillna(method="bfill", inplace=True)
    except Exception as e:
        st.error(f"Error calculating indicators for {ticker}: {str(e)}")
        return None
    
    # Get last row for signal generation
    last_row = data.iloc[-1]
    
    # Generate signal
    try:
        # Buy score system (count how many buy conditions are met)
        buy_score = 0
        
        if last_row["RSI"] < 40:  # Less strict RSI threshold
            buy_score += 1
        if last_row["SMA_50"] > last_row["SMA_200"]:  # Golden cross
            buy_score += 1
        if last_row["MACD"] > last_row["MACD_Signal"]:  # MACD crossover
            buy_score += 1
        if last_row["Close"] <= last_row["Lower_BB"]:  # Price at lower Bollinger Band
            buy_score += 1
        if last_row["Volume_Change"] > 0:  # Increasing volume
            buy_score += 1
            
        # Sell score system (count how many sell conditions are met)
        sell_score = 0
        
        if last_row["RSI"] > 60:  # Less strict RSI threshold
            sell_score += 1
        if last_row["SMA_50"] < last_row["SMA_200"]:  # Death cross
            sell_score += 1
        if last_row["MACD"] < last_row["MACD_Signal"]:  # MACD crossover bearish
            sell_score += 1
        if last_row["Close"] >= last_row["Upper_BB"]:  # Price at upper Bollinger Band
            sell_score += 1
        if last_row["Volume_Change"] < 0:  # Decreasing volume
            sell_score += 1
            
        # Decision making based on scores
        if buy_score >= 3 and buy_score > sell_score:
            return "BUY", data, {"buy_score": buy_score, "sell_score": sell_score}
        elif sell_score >= 3 and sell_score > buy_score:
            return "SELL", data, {"buy_score": buy_score, "sell_score": sell_score}
        else:
            return "HOLD", data, {"buy_score": buy_score, "sell_score": sell_score}
    except Exception as e:
        st.error(f"Error generating signal for {ticker}: {str(e)}")
        return None