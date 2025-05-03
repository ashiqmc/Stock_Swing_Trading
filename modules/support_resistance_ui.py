import streamlit as st
import pandas as pd
import numpy as np

def render_support_resistance_tab(latest, past_30d):
    """
    Renders the support and resistance levels tab
    
    Args:
        latest (Series): Latest data point
        past_30d (DataFrame): Last 30 days of data
    """
    st.write("#### Support & Resistance Levels")
    
    if all(key in latest for key in ['PP', 'R1', 'R2', 'S1', 'S2']):
        # Create a visual representation of price vs support/resistance levels
        price = latest['Close']
        levels = {
            'R2': latest['R2'],
            'R1': latest['R1'],
            'PP': latest['PP'],
            'S1': latest['S1'],
            'S2': latest['S2']
        }
        
        # Sort levels by price
        sorted_levels = sorted(levels.items(), key=lambda x: x[1], reverse=True)
        
        # Find nearest support and resistance
        above_price = [level for name, level in sorted_levels if level > price]
        below_price = [level for name, level in sorted_levels if level <= price]
        
        nearest_resistance = min(above_price) if above_price else None
        nearest_support = max(below_price) if below_price else None
        
        # Calculate distances
        resistance_distance = 0
        support_distance = 0
        resistance_name = ""
        support_name = ""
        
        if nearest_resistance:
            resistance_distance = ((nearest_resistance - price) / price) * 100
            resistance_name = next(name for name, level in sorted_levels if level == nearest_resistance)
        
        if nearest_support:
            support_distance = ((price - nearest_support) / price) * 100
            support_name = next(name for name, level in sorted_levels if level == nearest_support)
        
        # Display metrics
        col1, col2 = st.columns(2)
        
        with col1:
            if nearest_resistance:
                st.metric(f"Nearest Resistance ({resistance_name})", 
                         f"{nearest_resistance:.2f}", 
                         f"{resistance_distance:.2f}% above")
        
        with col2:
            if nearest_support:
                st.metric(f"Nearest Support ({support_name})", 
                         f"{nearest_support:.2f}", 
                         f"{support_distance:.2f}% below")
        
        # Visual representation of price vs levels
        sr_html = """<div style="margin: 15px 0;">"""
        
        for name, level in sorted_levels:
            # Determine if this is price level
            is_price = False
            if level <= price and (next_level := next((l for n, l in sorted_levels if l < level), None)) is not None:
                if price <= level and price > next_level:
                    is_price = True
            
            level_color = "#dc3545" if "R" in name else "#28a745" if "S" in name else "#ffc107"
            
            sr_html += f"""
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <div style="width: 40px; text-align: right; margin-right: 10px;">{name}</div>
                <div style="flex-grow: 1; height: 2px; background-color: {level_color};"></div>
                <div style="width: 80px; text-align: left; margin-left: 10px;">{level:.2f}</div>
            </div>
            """
            
            # Add price marker between levels if applicable
            if is_price:
                sr_html += f"""
                <div style="display: flex; align-items: center; margin-bottom: 5px;">
                    <div style="width: 40px; text-align: right; margin-right: 10px; font-weight: bold;">PRICE</div>
                    <div style="flex-grow: 1; height: 0; border-top: 2px dashed #000;"></div>
                    <div style="width: 80px; text-align: left; margin-left: 10px; font-weight: bold;">{price:.2f}</div>
                </div>
                """
        
        sr_html += "</div>"
        st.markdown(sr_html, unsafe_allow_html=True)
        
        # Legend
        st.markdown("""
        <div style="display: flex; gap: 20px; margin-top: 10px; font-size: 0.8em;">
            <div style="display: flex; align-items: center;">
                <div style="width: 12px; height: 12px; background-color: #dc3545; margin-right: 5px;"></div>
                <span>Resistance</span>
            </div>
            <div style="display: flex; align-items: center;">
                <div style="width: 12px; height: 12px; background-color: #ffc107; margin-right: 5px;"></div>
                <span>Pivot Point</span>
            </div>
            <div style="display: flex; align-items: center;">
                <div style="width: 12px; height: 12px; background-color: #28a745; margin-right: 5px;"></div>
                <span>Support</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Trading implications
        price_from_pp = price - latest['PP']
        if price_from_pp > 0:
            st.info("Price is above the pivot point, suggesting bullish sentiment in the near term.")
        else:
            st.info("Price is below the pivot point, suggesting bearish sentiment in the near term.")
        
        # Support and resistance interpretation
        if nearest_resistance and resistance_distance < 1.0:
            st.warning(f"Price is very close to resistance level {resistance_name} ({resistance_distance:.2f}% away). This could act as a barrier to upward movement.")
        
        if nearest_support and support_distance < 1.0:
            st.warning(f"Price is very close to support level {support_name} ({support_distance:.2f}% away). This could provide a floor for price.")
        
        # Display trade suggestions
        st.subheader("Trade Suggestions")
        
        if nearest_resistance and resistance_distance < 2.0:
            if price_from_pp > 0:
                st.markdown("""
                <div style="background-color: #f8d7da; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                    <strong>Resistance Approaching:</strong> Price is approaching a resistance level while above pivot point. 
                    Consider taking partial profits or tightening stop loss.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background-color: #f8d7da; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                    <strong>Resistance Test:</strong> Price is approaching a resistance level while below pivot point.
                    This is a potential short entry, with stop loss above resistance.
                </div>
                """, unsafe_allow_html=True)
        
        if nearest_support and support_distance < 2.0:
            if price_from_pp < 0:
                st.markdown("""
                <div style="background-color: #d4edda; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                    <strong>Support Approaching:</strong> Price is approaching a support level while below pivot point.
                    Consider adding to positions or entering new long positions if support holds.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background-color: #d4edda; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                    <strong>Support Test:</strong> Price is approaching a support level while above pivot point.
                    This indicates potential strength if support holds - possible continuation pattern.
                </div>
                """, unsafe_allow_html=True)
        
        # Advanced S/R techniques explained - Use tabs instead of expanders
        st.subheader("Support & Resistance Trading Strategies")
        
        strategy_tabs = st.tabs(["Bounce Trading", "Breakout Trading", "Pivot Points", "Range Trading", "Price Action"])
        
        with strategy_tabs[0]:
            st.markdown("""
            ### Bounce Trading
            
            - **Buy at Support**: Enter long positions when price approaches and bounces off support
            - **Sell at Resistance**: Enter short positions when price approaches and rejects from resistance
            - **Stop Loss**: Place stops just below support (for longs) or above resistance (for shorts)
            """)
        
        with strategy_tabs[1]:
            st.markdown("""
            ### Breakout Trading
            
            - **Buy on Resistance Break**: Enter long positions when price breaks above resistance
            - **Sell on Support Break**: Enter short positions when price breaks below support
            - **Confirmation**: Wait for candle close above/below level for confirmation
            """)
        
        with strategy_tabs[2]:
            st.markdown("""
            ### Pivot Point Strategies
            
            - **PP as Bias Indicator**: Above PP = bullish bias, Below PP = bearish bias
            - **R1/S1 as First Targets**: Use first levels as initial profit targets
            - **R2/S2 as Extended Targets**: Use second levels for strong trend days
            """)
        
        with strategy_tabs[3]:
            st.markdown("""
            ### Range Trading
            
            - **Buy at S1, Sell at R1**: Classic range-bound strategy
            - **Tighter Range**: Buy at PP when below, Sell at PP when above
            """)
        
        with strategy_tabs[4]:
            st.markdown("""
            ### Price Action Confirmations
            
            - Look for rejection candles (wicks) at levels
            - Multiple tests of a level can weaken it
            - Volume spike at level increases its significance
            """)
        
        # Show price chart - using a tab for the chart
        chart_tab = st.tabs(["Price Chart"])
        
        with chart_tab[0]:
            if 'Close' in past_30d.columns:
                st.write("**Price Chart with Support/Resistance Levels (30 Days)**")
                
                # Create a DataFrame for charting
                sr_chart = pd.DataFrame({
                    'Price': past_30d['Close'],
                })
                
                # Add horizontal lines for support/resistance levels
                # We'll just show this as text since Streamlit doesn't support horizontal lines in charts
                st.line_chart(sr_chart)
                
                # Display the levels as text below the chart
                level_text = ", ".join([f"{name}: {level:.2f}" for name, level in sorted_levels])
                st.caption(f"Support and resistance levels: {level_text}")
                st.caption("Note: Trading at support suggests buying, trading at resistance suggests selling or waiting for breakout confirmation")
    else:
        st.warning("Support and resistance data not available for this security.")
        
        # Display basic price chart
        if 'Close' in past_30d.columns:
            st.line_chart(past_30d['Close'])
            
            # Provide information about why S/R levels are important
            st.info("""
            Support and resistance levels help identify key price points where the stock may reverse or pause.
            These levels are not available in the current data, but would typically show:
            - Where buyers tend to enter the market (support)
            - Where sellers tend to enter the market (resistance)
            - Potential reversal points and price targets
            """)
            
            # Offer alternative approaches using tabs instead of expanders
            st.subheader("Alternative S/R Methods")
            
            alt_tabs = st.tabs(["Previous Highs/Lows", "Moving Averages", "Round Numbers", "Trendlines"])
            
            with alt_tabs[0]:
                st.markdown("""
                ### Previous Highs and Lows
                
                Look for price levels where the stock has reversed in the past. These often become support/resistance on subsequent tests.
                """)
            
            with alt_tabs[1]:
                st.markdown("""
                ### Moving Averages
                
                The 50, 100, and 200-day moving averages often act as dynamic support/resistance. Price tends to respect these levels.
                """)
            
            with alt_tabs[2]:
                st.markdown("""
                ### Round Numbers
                
                Price levels at whole or half numbers often become psychological support/resistance (e.g., $50.00, $75.50).
                """)
            
            with alt_tabs[3]:
                st.markdown("""
                ### Trendlines
                
                Draw lines connecting peaks (for resistance) or troughs (for support) to identify diagonal support/resistance.
                """)