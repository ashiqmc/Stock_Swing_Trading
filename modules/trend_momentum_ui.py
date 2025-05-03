import streamlit as st
import pandas as pd
import numpy as np

def render_trend_momentum_tab(latest, past_30d):
    """
    Renders the trend and momentum indicators tab
    
    Args:
        latest (Series): Latest data point
        past_30d (DataFrame): Last 30 days of data
    """
    st.write("#### Trend & Momentum Indicators")
    
    # RSI visualization with progress bar
    if 'RSI' in latest:
        col1, col2 = st.columns(2)
        with col1:
            rsi_value = float(latest['RSI'])
            rsi_color = "green" if rsi_value < 30 else "red" if rsi_value > 70 else "orange"
            rsi_status = "Oversold" if rsi_value < 30 else "Overbought" if rsi_value > 70 else "Neutral"
            st.metric("RSI (14)", f"{rsi_value:.2f}", rsi_status)
            
            # Create a custom progress bar for RSI
            progress_html = f"""
            <div style="margin-bottom: 10px;">
                <div style="background-color: #f0f2f6; border-radius: 3px; height: 15px; position: relative;">
                    <div style="position: absolute; left: 0; right: 0;">
                        <div style="position: absolute; left: 30%; width: 2px; height: 15px; background-color: #888;"></div>
                        <div style="position: absolute; left: 70%; width: 2px; height: 15px; background-color: #888;"></div>
                    </div>
                    <div style="width: {rsi_value}%; height: 15px; background-color: {rsi_color}; border-radius: 3px;"></div>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 0.8em;">
                    <span>0</span>
                    <span>30</span>
                    <span>70</span>
                    <span>100</span>
                </div>
            </div>
            """
            st.markdown(progress_html, unsafe_allow_html=True)
        
        # MACD in second column
        with col2:
            if all(col in latest for col in ['MACD', 'MACD_Signal']):
                macd_diff = latest['MACD'] - latest['MACD_Signal']
                macd_status = "Bullish" if macd_diff > 0 else "Bearish"
                st.metric("MACD", f"{latest['MACD']:.2f}", 
                         f"{macd_diff:.2f} ({macd_status})", 
                         delta_color="normal" if macd_diff > 0 else "inverse")
                
                if 'MACD_Hist' in latest:
                    # Simple MACD histogram visualization
                    hist_value = latest['MACD_Hist']
                    hist_color = "green" if hist_value > 0 else "red"
                    hist_width = min(abs(hist_value) * 10, 100)  # Scale for visualization
                    
                    hist_html = f"""
                    <div style="margin-bottom: 10px;">
                        <div style="display: flex; align-items: center; height: 20px;">
                            <div style="flex: 1; text-align: right; padding-right: 5px;">Bearish</div>
                            <div style="width: 100px; background-color: #f0f2f6; height: 15px; position: relative; border-radius: 3px;">
                                <div style="position: absolute; left: 50%; width: 1px; height: 15px; background-color: #888;"></div>
                                <div style="position: absolute; {'left: 50%;' if hist_value > 0 else 'right: 50%;'} 
                                            width: {hist_width}%; height: 15px; background-color: {hist_color}; 
                                            border-radius: 3px;"></div>
                            </div>
                            <div style="flex: 1; padding-left: 5px;">Bullish</div>
                        </div>
                    </div>
                    """
                    st.markdown(hist_html, unsafe_allow_html=True)
    
    # Moving averages comparison with interpretation
    if all(col in latest for col in ['SMA_50', 'SMA_200']):
        st.write("#### Moving Averages")
        col1, col2 = st.columns(2)
        
        with col1:
            ma_diff = latest['SMA_50'] - latest['SMA_200']
            ma_status = "Golden Cross" if ma_diff > 0 else "Death Cross"
            st.metric("SMA 50 vs 200", f"{ma_diff:.2f}", ma_status, 
                     delta_color="normal" if ma_diff > 0 else "inverse")
        
        with col2:
            price_vs_ma = latest['Close'] - latest['SMA_50']
            status = "Above" if price_vs_ma > 0 else "Below"
            st.metric("Price vs SMA 50", f"{price_vs_ma:.2f}", 
                     f"{status} ({(price_vs_ma / latest['SMA_50'] * 100):.2f}%)",
                     delta_color="normal" if price_vs_ma > 0 else "inverse")
    
    # ADX indicator if available
    if 'ADX' in latest:
        st.write("#### Trend Strength (ADX)")
        adx_value = latest['ADX']
        
        # ADX strength interpretation
        if adx_value < 20:
            trend_strength_desc = "Weak or No Trend"
            trend_color_adx = "gray"
        elif adx_value < 25:
            trend_strength_desc = "Developing Trend"
            trend_color_adx = "blue"
        elif adx_value < 30:
            trend_strength_desc = "Strong Trend"
            trend_color_adx = "green"
        else:
            trend_strength_desc = "Very Strong Trend"
            trend_color_adx = "dark green"
        
        st.metric("ADX (14)", f"{adx_value:.2f}", trend_strength_desc)
        
        # ADX progress bar
        adx_bar_html = f"""
        <div style="margin: 10px 0;">
            <div style="background-color: #f0f2f6; border-radius: 3px; height: 15px;">
                <div style="width: {min(adx_value, 50) * 2}%; height: 15px; 
                          background-color: {trend_color_adx}; border-radius: 3px;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.8em; margin-top: 5px;">
                <span>0</span>
                <span>20 - Weak</span>
                <span>25 - Strong</span>
                <span>50+</span>
            </div>
        </div>
        """
        st.markdown(adx_bar_html, unsafe_allow_html=True)
        
        # Show DI+ and DI- if available
        if all(col in latest for col in ['DI_Plus', 'DI_Minus']):
            di_diff = latest['DI_Plus'] - latest['DI_Minus']
            di_direction = "Bullish" if di_diff > 0 else "Bearish"
            st.metric("Directional Movement", f"+DI: {latest['DI_Plus']:.2f} | -DI: {latest['DI_Minus']:.2f}", 
                     f"{di_direction} ({abs(di_diff):.2f})",
                     delta_color="normal" if di_diff > 0 else "inverse")
    
    # Ichimoku Cloud if available
    if all(col in latest for col in ['Ichimoku_A', 'Ichimoku_B']):
        st.write("#### Ichimoku Cloud Analysis")
        
        cloud_diff = latest['Ichimoku_A'] - latest['Ichimoku_B']
        cloud_type = "Bullish" if cloud_diff > 0 else "Bearish"
        
        price_vs_cloud = min(latest['Close'] - latest['Ichimoku_A'], 
                           latest['Close'] - latest['Ichimoku_B'])
        cloud_position = "Above" if price_vs_cloud > 0 else "Below"
        
        st.metric("Ichimoku Cloud", cloud_type, 
                 f"Price {cloud_position} Cloud ({price_vs_cloud:.2f})",
                 delta_color="normal" if price_vs_cloud > 0 else "inverse")

    # Show charts directly without using expanders
    st.write("#### Charts")
    
    chart_tabs = st.tabs(["RSI Chart", "MACD Chart", "Moving Averages Chart"])
    
    with chart_tabs[0]:
        # RSI Chart
        if 'RSI' in past_30d.columns:
            st.write("**RSI Chart (30 Days)**")
            st.line_chart(past_30d['RSI'])
            st.caption("RSI ranges: Below 30 (Oversold), 30-70 (Neutral), Above 70 (Overbought)")
    
    with chart_tabs[1]:
        # MACD Chart
        if all(col in past_30d.columns for col in ['MACD', 'MACD_Signal']):
            st.write("**MACD Chart (30 Days)**")
            st.line_chart(past_30d[['MACD', 'MACD_Signal']])
            st.caption("MACD above signal line is bullish, below is bearish")
    
    with chart_tabs[2]:
        # Moving Averages Chart
        if all(col in past_30d.columns for col in ['SMA_50', 'SMA_200', 'Close']):
            st.write("**Price vs Moving Averages (30 Days)**")
            st.line_chart(past_30d[['Close', 'SMA_50', 'SMA_200']])
            st.caption("Price above moving averages is bullish, below is bearish")