import streamlit as st
import pandas as pd
import numpy as np

def render_volume_tab(latest, past_30d):
    """
    Renders the volume analysis indicators tab
    
    Args:
        latest (Series): Latest data point
        past_30d (DataFrame): Last 30 days of data
    """
    st.write("#### Volume Analysis")
    
    # Volume Ratio (current volume vs average)
    if 'Volume_Ratio' in latest:
        vol_ratio = latest['Volume_Ratio']
        vol_status = "High" if vol_ratio > 1.5 else "Average" if vol_ratio > 0.8 else "Low"
        
        st.metric("Volume vs Average", f"{vol_ratio:.2f}x", 
                 f"{vol_status} Volume",
                 delta_color="normal" if vol_ratio > 1 else "inverse")
    
    # On Balance Volume
    if 'OBV' in latest and 'OBV_EMA' in latest:
        obv_diff = latest['OBV'] - latest['OBV_EMA']
        obv_signal = "Bullish" if obv_diff > 0 else "Bearish"
        
        st.metric("OBV vs EMA", f"{obv_diff:.0f}", 
                 obv_signal,
                 delta_color="normal" if obv_diff > 0 else "inverse")
        
        st.caption("OBV above its EMA suggests increasing buying pressure")
    
    # Accumulation/Distribution Line
    if 'AD_Line' in latest and 'AD_EMA' in latest:
        ad_diff = latest['AD_Line'] - latest['AD_EMA']
        ad_signal = "Accumulation" if ad_diff > 0 else "Distribution"
        
        st.metric("A/D Line", ad_signal, 
                 f"{ad_diff:.0f}",
                 delta_color="normal" if ad_diff > 0 else "inverse")
        
        st.caption("Rising A/D Line indicates buying pressure, falling indicates selling pressure")
    
    # Volume change visualization
    if 'Volume_Change' in latest:
        vol_change = latest['Volume_Change'] * 100
        vol_change_text = f"{vol_change:.2f}%" if not np.isnan(vol_change) else "N/A"
        
        st.metric("Volume Change", vol_change_text, 
                 "Increasing" if vol_change > 0 else "Decreasing",
                 delta_color="normal" if vol_change > 0 else "inverse")
    
    # Volume and price relationship
    if 'Volume' in latest and 'Close' in latest and len(past_30d) > 1:
        # Calculate if volume is increasing on up days and decreasing on down days
        price_change = latest['Close'] - past_30d['Close'].iloc[-2]
        
        if price_change > 0 and latest.get('Volume_Change', 0) > 0:
            vol_signal = "Strong Bullish (↑Price, ↑Volume)"
            vol_signal_color = "green"
        elif price_change < 0 and latest.get('Volume_Change', 0) > 0:
            vol_signal = "Strong Bearish (↓Price, ↑Volume)"
            vol_signal_color = "red"
        elif price_change > 0 and latest.get('Volume_Change', 0) < 0:
            vol_signal = "Weak Bullish (↑Price, ↓Volume)"
            vol_signal_color = "orange"
        elif price_change < 0 and latest.get('Volume_Change', 0) < 0:
            vol_signal = "Weak Bearish (↓Price, ↓Volume)"
            vol_signal_color = "orange"
        else:
            vol_signal = "Neutral"
            vol_signal_color = "gray"
        
        st.markdown(f"""
        <div style="margin: 10px 0; padding: 10px; border-radius: 5px; 
                  background-color: {'#d4edda' if vol_signal_color == 'green' else '#f8d7da' if vol_signal_color == 'red' else '#fff3cd'};">
            <span style="font-weight: bold;">Volume Signal:</span> 
            <span style="color: {vol_signal_color};">{vol_signal}</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Display chart data - using tabs instead of nested expanders
    st.write("#### Volume Charts")
    
    volume_chart_tabs = st.tabs(["Volume", "OBV", "A/D Line"])
    
    with volume_chart_tabs[0]:
        # Volume Chart
        if 'Volume' in past_30d.columns:
            st.write("**Volume (30 Days)**")
            st.bar_chart(past_30d['Volume'])
            st.caption("Volume spikes can indicate potential trend reversals or confirmations")
    
    with volume_chart_tabs[1]:
        # OBV Chart
        if 'OBV' in past_30d.columns:
            st.write("**On-Balance Volume (30 Days)**")
            st.line_chart(past_30d['OBV'])
            st.caption("Rising OBV confirms uptrend, falling OBV confirms downtrend")
    
    with volume_chart_tabs[2]:
        # A/D Line Chart
        if 'AD_Line' in past_30d.columns:
            st.write("**Accumulation/Distribution Line (30 Days)**")
            st.line_chart(past_30d['AD_Line'])
            st.caption("A/D Line trends can precede price movements")