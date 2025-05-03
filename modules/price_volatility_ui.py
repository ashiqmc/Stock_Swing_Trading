import streamlit as st
import pandas as pd
import numpy as np

def render_price_volatility_tab(latest, past_30d):
    """
    Renders the price action and volatility indicators tab
    
    Args:
        latest (Series): Latest data point
        past_30d (DataFrame): Last 30 days of data
    """
    st.write("#### Price Action & Volatility")
    
    # Bollinger Bands
    if all(col in latest for col in ['Upper_BB', 'Lower_BB', 'Middle_BB']):
        col1, col2 = st.columns(2)
        
        with col1:
            # Calculate price position relative to bands
            bb_range = latest['Upper_BB'] - latest['Lower_BB']
            position_in_band = (latest['Close'] - latest['Lower_BB']) / bb_range
            position_pct = position_in_band * 100
            
            # Determine position text
            if position_in_band <= 0:
                band_position = "Below Lower Band"
            elif position_in_band < 0.2:
                band_position = "Near Lower Band"
            elif position_in_band < 0.4:
                band_position = "Lower Half"
            elif position_in_band < 0.6:
                band_position = "Middle"
            elif position_in_band < 0.8:
                band_position = "Upper Half"
            elif position_in_band < 1:
                band_position = "Near Upper Band"
            else:
                band_position = "Above Upper Band"
            
            st.metric("Bollinger Band Position", f"{position_pct:.1f}%", band_position)
            
            # Visual representation of position in band
            bb_html = f"""
            <div style="margin: 10px 0;">
                <div style="background-color: #f0f2f6; border-radius: 3px; height: 15px; position: relative;">
                    <div style="position: absolute; left: 0; right: 0; height: 15px; display: flex;">
                        <div style="flex: 1; border-right: 1px solid #888;"></div>
                        <div style="flex: 1;"></div>
                    </div>
                    <div style="position: absolute; left: {position_pct}%; width: 3px; height: 15px; 
                              background-color: black; transform: translateX(-50%);"></div>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 0.8em; margin-top: 5px;">
                    <span>Lower Band</span>
                    <span>Middle Band</span>
                    <span>Upper Band</span>
                </div>
            </div>
            """
            st.markdown(bb_html, unsafe_allow_html=True)
        
        with col2:
            if 'BB_Width' in latest:
                # BB Width shows volatility
                st.metric("Bollinger Band Width", f"{latest['BB_Width']:.4f}")
                st.caption("Wider bands indicate higher volatility, narrow bands indicate lower volatility")
    
    # ATR (Average True Range) for volatility measurement
    if 'ATR' in latest and 'ATR_Percent' in latest:
        st.write("#### Volatility (ATR)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("ATR (14)", f"{latest['ATR']:.4f}")
        
        with col2:
            # ATR as percentage of price gives context
            st.metric("ATR %", f"{latest['ATR_Percent']:.2f}%")
            st.caption("Higher % indicates higher volatility relative to price")
    
    # Parabolic SAR
    if 'PSAR' in latest:
        st.write("#### Parabolic SAR")
        
        # Determine if price is above or below PSAR
        psar_diff = latest['Close'] - latest['PSAR']
        psar_position = "Above" if psar_diff > 0 else "Below"
        psar_signal = "Bullish" if psar_diff > 0 else "Bearish"
        
        st.metric("PSAR Position", f"{psar_position} Price", 
                 f"{psar_signal} ({abs(psar_diff):.2f})",
                 delta_color="normal" if psar_diff > 0 else "inverse")
        
        # Show recent PSAR signals if available
        if 'PSAR_Up_Indicator' in latest and 'PSAR_Down_Indicator' in latest:
            recent_signal = "Buy" if latest['PSAR_Up_Indicator'] == 1 else "Sell" if latest['PSAR_Down_Indicator'] == 1 else "None"
            signal_color = "green" if recent_signal == "Buy" else "red" if recent_signal == "Sell" else "gray"
            
            st.markdown(f"""
            <div style="margin: 10px 0; padding: 10px; border-radius: 5px; 
                      background-color: {'#d4edda' if signal_color == 'green' else '#f8d7da' if signal_color == 'red' else '#e2e3e5'};">
                <span style="font-weight: bold;">Latest Signal:</span> 
                <span style="color: {signal_color};">{recent_signal}</span>
            </div>
            """, unsafe_allow_html=True)
    
    # Display chart data - using tabs instead of expanders
    st.write("#### Charts")
    
    chart_tabs = st.tabs(["Bollinger Bands", "ATR Chart"])
    
    with chart_tabs[0]:
        # Bollinger Bands Chart
        if all(col in past_30d.columns for col in ['Close', 'Upper_BB', 'Lower_BB', 'Middle_BB']):
            st.write("**Bollinger Bands (30 Days)**")
            
            # Create BB chart data with fills
            bb_chart = pd.DataFrame({
                'Price': past_30d['Close'],
                'Upper Band': past_30d['Upper_BB'],
                'Middle Band': past_30d['Middle_BB'],
                'Lower Band': past_30d['Lower_BB']
            })
            
            st.line_chart(bb_chart)
            st.caption("Price at lower band indicates potential reversal up, price at upper band indicates potential reversal down")
    
    with chart_tabs[1]:
        # ATR Chart
        if 'ATR' in past_30d.columns:
            st.write("**ATR (Average True Range) - 30 Days**")
            st.line_chart(past_30d['ATR'])
            st.caption("Rising ATR indicates increasing volatility, falling ATR indicates decreasing volatility")