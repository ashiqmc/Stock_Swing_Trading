import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Import modules
from stock_search import search_stocks
from data_fetcher import fetch_stock_data
from signal_generator import get_signal
from ui_components import (
    render_price_data_tab,
    render_indicators_tab,
    render_calendar_tab,
    render_recommendation_tab
)

# App title and configuration
st.set_page_config(
    page_title="Swing Trading AI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Swing Trading AI Dashboard")

# Sidebar for settings and stock selection
st.sidebar.header("⚙️ Settings")

# Default stocks list
# default_stocks = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS","BLUESTARCO.BO","UJJIVANSFB.NS","TATAMOTORS.NS", "SUZLON.NS"]
# Default stocks list
default_stocks = ["BLUESTARCO.NS", "SUZLON.NS","UJJIVANSFB.NS","TATAMOTORS.NS","TATASTEEL.NS"]
# Initialize session state for tracking selected stocks
if 'selected_stocks' not in st.session_state:
    st.session_state.selected_stocks = default_stocks.copy()

# Stock search section
# Stock search section
st.sidebar.subheader("🔍 Search & Add Stocks")
search_query = st.sidebar.text_input("Search for stocks", "")

# Store search results in session state
if 'search_results' not in st.session_state:
    st.session_state.search_results = []

# Search button logic
if st.sidebar.button("Search"):
    if search_query:
        st.session_state.search_results = search_stocks(search_query)
    else:
        st.session_state.search_results = []

# Display search results
if st.session_state.search_results:
    st.sidebar.write(f"Found {len(st.session_state.search_results)} results:")
    for i, stock in enumerate(st.session_state.search_results[:10]):  # Limit to 10 results
        col1, col2 = st.sidebar.columns([1, 3])
        with col1:
            if st.sidebar.button(f"Add", key=f"add_{i}"):
                symbol = stock['symbol']
                if symbol not in st.session_state.selected_stocks:
                    st.session_state.selected_stocks.append(symbol)
                    st.sidebar.success(f"Added {symbol}")
                    # Force a rerun to update the UI
                    st.rerun()
                else:
                    st.sidebar.info(f"{symbol} already in your list")
        with col2:
            st.sidebar.write(f"{stock['symbol']}: {stock['name']} ({stock['exchange']})")
elif search_query and 'search_results' in st.session_state and not st.session_state.search_results:
    st.sidebar.warning("No stocks found for your query")
# Display and manage selected stocks
st.sidebar.subheader("📋 Your Stock List")
if not st.session_state.selected_stocks:
    st.sidebar.warning("⚠️ No stocks selected")
else:
    for i, stock in enumerate(st.session_state.selected_stocks):
        col1, col2 = st.sidebar.columns([3, 1])
        with col1:
            st.write(f"{i+1}. {stock}")
        with col2:
            if st.button("Remove", key=f"remove_{i}"):
                st.session_state.selected_stocks.remove(stock)
                st.experimental_rerun()

# Main area for results
if not st.session_state.selected_stocks:
    st.warning("⚠️ Please select at least one stock from the sidebar.")
else:
    # UI to show results
    if st.button("🔄 Refresh Data"):
        results = []
        detailed_results = {}
        
        with st.spinner("Fetching and analyzing stock data... ⏳"):
            for stock in st.session_state.selected_stocks:
                signal_result = get_signal(stock)
                
                if signal_result:
                    signal, data, scores = signal_result
                    results.append([stock, signal, scores["buy_score"], scores["sell_score"]])
                    detailed_results[stock] = data
            
            # Display results table
            if results:
                df = pd.DataFrame(results, columns=["Stock", "Signal", "Buy Score", "Sell Score"])
                
                # Add styling based on signal
                def highlight_signal(val):
                    if val == 'BUY':
                        return 'background-color: #8AFF8A'  # Light green
                    elif val == 'SELL':
                        return 'background-color: #FF8A8A'  # Light red
                    else:
                        return 'background-color: #FFFF8A'  # Light yellow
                
                styled_df = df.style.applymap(highlight_signal, subset=['Signal'])
                
                # Add timestamp to the success message
                current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.success(f"✅ Signals updated successfully! (Last updated: {current_date})")
                st.dataframe(styled_df)
                
                # Add a section to display detailed analysis with date
                current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.subheader(f"📈 Detailed Analysis (as of {current_date})")
                
                for stock, signal_info, buy_score, sell_score in results:
                    with st.expander(f"{stock} - {signal_info} (Buy: {buy_score}/5, Sell: {sell_score}/5)"):
                        if stock in detailed_results:
                            data = detailed_results[stock]
                            latest = data.iloc[-1]
                            past_30d = data.iloc[-30:]
                            
                            # Calculate metrics needed across tabs
                            price_start = past_30d['Close'].iloc[0]
                            price_end = past_30d['Close'].iloc[-1]
                            price_change_pct = ((price_end - price_start) / price_start) * 100
                            daily_returns = past_30d['Close'].pct_change().dropna()
                            volatility = daily_returns.std() * 100
                            
                            # Process the last 5 days for display
                            last_5_days = data.tail(5).copy()
                            last_30_days = data.tail(30).copy()
                            
                            # Create tabs for a more interactive design
                            tab1, tab2, tab3, tab4 = st.tabs([
                                "📈 Price Data", 
                                "📊 Key Indicators", 
                                "📆 Calendar View", 
                                "🎯 Trade Recommendation"
                            ])
                            
                            with tab1:
                                render_price_data_tab(last_5_days, last_30_days, data)
                            
                            with tab2:
                                # Generate metrics for technical indicators
                                metrics = [
                                    {"name": "RSI (14)", "value": f"{latest['RSI']:.2f}", "condition": latest['RSI'] < 40, 
                                     "buy_text": "Oversold (Buy)", "sell_text": "Overbought (Sell)",
                                     "explanation": f"{'Below 40 indicates oversold conditions, potential buying opportunity' if latest['RSI'] < 40 else 'Above 60 indicates overbought conditions, potential selling opportunity' if latest['RSI'] > 60 else 'In neutral territory'}"},
                                    
                                    {"name": "SMA 50 vs 200", "value": f"{latest['SMA_50']:.2f} vs {latest['SMA_200']:.2f}", 
                                     "condition": latest['SMA_50'] > latest['SMA_200'], 
                                     "buy_text": "Golden Cross (Buy)", "sell_text": "Death Cross (Sell)",
                                     "explanation": f"{'50-day average above 200-day indicates bullish trend' if latest['SMA_50'] > latest['SMA_200'] else '50-day average below 200-day indicates bearish trend'}"},
                                    
                                    {"name": "MACD vs Signal", "value": f"{latest['MACD']:.2f} vs {latest['MACD_Signal']:.2f}", 
                                     "condition": latest['MACD'] > latest['MACD_Signal'], 
                                     "buy_text": "Bullish Crossover (Buy)", "sell_text": "Bearish Crossover (Sell)",
                                     "explanation": f"{'MACD above signal line suggests upward momentum' if latest['MACD'] > latest['MACD_Signal'] else 'MACD below signal line suggests downward momentum'}"},
                                    
                                    {"name": "Bollinger Bands", "value": f"{latest['Close']:.2f} (Price)", 
                                     "condition": latest['Close'] <= latest['Lower_BB'], 
                                     "buy_text": "At Lower Band (Buy)", "sell_text": "At Upper Band (Sell)",
                                     "explanation": f"{'Price near lower band suggests potential reversal upward' if latest['Close'] <= latest['Lower_BB'] else 'Price near upper band suggests potential reversal downward' if latest['Close'] >= latest['Upper_BB'] else 'Price within bands indicates normal trading range'}"},
                                    
                                    {"name": "Volume Change", "value": f"{latest['Volume_Change']*100:.2f}%", 
                                     "condition": latest['Volume_Change'] > 0, 
                                     "buy_text": "Increasing (Buy)", "sell_text": "Decreasing (Sell)",
                                     "explanation": f"{'Increasing volume supports price direction' if latest['Volume_Change'] > 0 else 'Decreasing volume may indicate weakening trend'}"}
                                ]
                                
                                # Volume trend calculation for indicators tab
                                avg_volume = past_30d['Volume'].mean()
                                recent_volume = past_30d['Volume'].iloc[-5:].mean()
                                volume_change_pct = ((recent_volume - avg_volume) / avg_volume) * 100
                                
                                # Trend strength
                                if price_change_pct > 5:
                                    trend_color = "green"
                                    trend_strength = "Strong Uptrend"
                                elif price_change_pct > 0:
                                    trend_color = "green"
                                    trend_strength = "Weak Uptrend"
                                elif price_change_pct > -5:
                                    trend_color = "red"
                                    trend_strength = "Weak Downtrend"
                                else:
                                    trend_color = "red"
                                    trend_strength = "Strong Downtrend"
                                
                                render_indicators_tab(
                                    latest, past_30d, metrics, price_change_pct,
                                    volume_change_pct, volatility, trend_strength, trend_color
                                )
                            
                            with tab3:
                                render_calendar_tab(last_30_days)
                            
                            with tab4:
                                # Generate buy/sell reasons for recommendation tab
                                buy_reasons = []
                                sell_reasons = []
                                
                                for metric in metrics:
                                    if metric["condition"]:
                                        buy_reasons.append(f"{metric['name']}: {metric['buy_text']}")
                                    else:
                                        sell_reasons.append(f"{metric['name']}: {metric['sell_text']}")
                                
                                render_recommendation_tab(
                                    signal_info, buy_score, sell_score,
                                    buy_reasons, sell_reasons, latest,
                                    past_30d, price_change_pct, volatility
                                )
            else:
                st.warning("⚠️ No valid signals generated. Check if stock data is available.")
