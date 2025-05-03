import streamlit as st
import pandas as pd
import numpy as np

def render_price_data_tab(last_5_days, last_30_days, data):
    """
    Render the price data tab with tables and charts
    
    Args:
        last_5_days (DataFrame): Last 5 days of price data
        last_30_days (DataFrame): Last 30 days of price data
        data (DataFrame): Full stock data
    """
    st.write("### Last 5 Trading Days")
    
    # Convert the index to a column if it contains dates
    if isinstance(last_5_days.index, pd.DatetimeIndex):
        # Process the last 5 days for the table
        last_5_days = last_5_days.reset_index()
        last_5_days.rename(columns={'index': 'Date'}, inplace=True)
        # Format the date column
        last_5_days['Date'] = last_5_days['Date'].dt.strftime('%Y-%m-%d')
        # Reorder columns to show Date first
        date_display = last_5_days[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
        
        # Add visual sparkline chart next to the table for a quick trend view
        col1, col2 = st.columns([2, 1])
        with col1:
            st.dataframe(date_display, height=200)
        with col2:
            st.write("#### 30 Day Trend")
            # Quick sparkline of closing prices
            close_data = data['Close'].tail(30)
            st.line_chart(close_data)
    else:
        st.dataframe(last_5_days[['Open', 'High', 'Low', 'Close', 'Volume']])
    
    # Add a 30-day price chart
    st.write("### 30-Day Price History")
    price_history = data[['Close']].tail(30).copy()
    if isinstance(price_history.index, pd.DatetimeIndex):
        price_history = price_history.reset_index()
        price_history.rename(columns={'index': 'Date'}, inplace=True)
        st.line_chart(price_history.set_index('Date'))
    else:
        st.line_chart(price_history)


def render_indicators_tab(latest, past_30d, metrics, price_change_pct, 
                         volume_change_pct, volatility, trend_strength, trend_color):
    """
    Render the indicators tab with technical analysis visualizations
    
    Args:
        latest (Series): Latest data point
        past_30d (DataFrame): Last 30 days of data
        metrics (list): List of metrics dictionaries
        price_change_pct (float): Price change percentage
        volume_change_pct (float): Volume change percentage
        volatility (float): Volatility value
        trend_strength (str): Trend strength description
        trend_color (str): Color for trend display
    """
    st.write("### Key Indicators & Trading Insights")
    
    # Display trend insights with more interactive metrics
    col1, col2, col3 = st.columns(3)
    
    # Display summary insights in metrics format instead of a box
    with col1:
        trend_delta = f"{price_change_pct:.2f}%"
        st.metric("30-Day Trend", trend_strength, trend_delta)
    
    with col2:
        st.metric("Volatility", f"{volatility:.2f}%", None)
    
    with col3:
        volume_delta = f"{volume_change_pct:.2f}%"
        st.metric("Volume Trend", "Increasing" if volume_change_pct > 0 else "Decreasing", volume_delta)
    
    # Create a more visual indicators section using metrics and progress bars
    st.write("#### Technical Indicators Detail")
    
    # Use two columns for indicators to make better use of space
    for i in range(0, len(metrics), 2):
        cols = st.columns(2)
        for j in range(2):
            if i+j < len(metrics):
                metric = metrics[i+j]
                with cols[j]:
                    # Create a more visual indicator display
                    text_color = "green" if metric["condition"] else "red"
                    status_text = metric["buy_text"] if metric["condition"] else metric["sell_text"]
                    
                    # Show the indicator name and value using metric component
                    st.metric(metric['name'], metric['value'], 
                              delta=status_text, 
                              delta_color="normal" if metric["condition"] else "inverse")
                    st.caption(metric["explanation"])
                    
                    # Add a visual bar for applicable metrics
                    if metric['name'] == "RSI (14)":
                        # Create a custom progress bar for RSI
                        rsi_value = float(latest['RSI'])
                        # Normalize to 0-100 range
                        progress_html = f"""
                        <div style="margin-bottom: 10px;">
                            <div style="background-color: #f0f2f6; border-radius: 3px; height: 15px; position: relative;">
                                <div style="position: absolute; left: 0; right: 0;">
                                    <div style="position: absolute; left: 30%; width: 2px; height: 15px; background-color: #888;"></div>
                                    <div style="position: absolute; left: 70%; width: 2px; height: 15px; background-color: #888;"></div>
                                </div>
                                <div style="width: {rsi_value}%; height: 15px; background-color: {'green' if rsi_value < 30 else 'red' if rsi_value > 70 else 'orange'}; border-radius: 3px;"></div>
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
    
    # Show combined charts of the indicators instead of separate ones
    st.write("#### Key Charts")
    
    # Combined chart for RSI and Price
    chart_tabs = st.tabs(["RSI Chart", "Moving Averages", "MACD"])
    
    with chart_tabs[0]:
        st.write("**RSI Chart (30 Days)**")
        rsi_data = past_30d[['RSI']].copy()
        if isinstance(rsi_data.index, pd.DatetimeIndex):
            rsi_data = rsi_data.reset_index()
            date_col = 'Date' if 'Date' in rsi_data.columns else 'index'
            st.line_chart(rsi_data.set_index(date_col)['RSI'])
        else:
            st.line_chart(rsi_data)
        st.caption("RSI ranges: Below 30 (Oversold), 30-70 (Neutral), Above 70 (Overbought)")
    
    with chart_tabs[1]:
        st.write("**Price vs Moving Averages (30 Days)**")
        sma_data = past_30d[['Close', 'SMA_50', 'SMA_200']].copy()
        if isinstance(sma_data.index, pd.DatetimeIndex):
            sma_data = sma_data.reset_index()
            date_col = 'Date' if 'Date' in sma_data.columns else 'index'
            st.line_chart(sma_data.set_index(date_col)[['Close', 'SMA_50', 'SMA_200']])
        else:
            st.line_chart(sma_data)
    
    with chart_tabs[2]:
        st.write("**MACD (30 Days)**")
        macd_data = past_30d[['MACD', 'MACD_Signal']].copy()
        if isinstance(macd_data.index, pd.DatetimeIndex):
            macd_data = macd_data.reset_index()
            date_col = 'Date' if 'Date' in macd_data.columns else 'index'
            st.line_chart(macd_data.set_index(date_col)[['MACD', 'MACD_Signal']])
        else:
            st.line_chart(macd_data)
        st.caption("MACD above signal line is bullish, below is bearish")


def render_calendar_tab(last_30_days):
    """
    Render the calendar tab with color-coded daily performance
    
    Args:
        last_30_days (DataFrame): Last 30 days of data
    """
    st.write("### Calendar View (Last 30 Trading Days)")
    
    # Create a calendar view with the last 30 days
    calendar_data = last_30_days.copy()
    
    if isinstance(calendar_data.index, pd.DatetimeIndex):
        calendar_data = calendar_data.reset_index()
        calendar_data['Day'] = calendar_data['Date'].dt.day
        calendar_data['Month'] = calendar_data['Date'].dt.month
        calendar_data['Year'] = calendar_data['Date'].dt.year
        calendar_data['DayOfWeek'] = calendar_data['Date'].dt.dayofweek
        calendar_data['DateStr'] = calendar_data['Date'].dt.strftime('%Y-%m-%d')
        
        # Calculate daily returns for color coding
        calendar_data['Return'] = calendar_data['Close'].pct_change() * 100
        
        # Get unique months in the data
        months = calendar_data[['Year', 'Month']].drop_duplicates().sort_values(['Year', 'Month'])
        
        for _, month_row in months.iterrows():
            year = month_row['Year']
            month = month_row['Month']
            month_name = pd.Timestamp(year=year, month=month, day=1).strftime('%B %Y')
            
            st.write(f"**{month_name}**")
            
            # Filter data for this month
            month_data = calendar_data[(calendar_data['Year'] == year) & 
                                    (calendar_data['Month'] == month)]
            
            # Create a calendar grid
            # First, create a list of day names for the header
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            
            # Start with an empty calendar
            calendar_html = '<div style="display: grid; grid-template-columns: repeat(7, 1fr); gap: 5px; width: 100%;">'
            
            # Add day headers
            for day in days:
                calendar_html += f'<div style="text-align: center; font-weight: bold; padding: 5px;">{day}</div>'
            
            # Get the first day of the month
            first_day = pd.Timestamp(year=year, month=month, day=1)
            # Get the day of week (0 = Monday, 6 = Sunday)
            first_weekday = first_day.dayofweek
            
            # Add empty cells for days before the first day of the month
            for _ in range(first_weekday):
                calendar_html += '<div style="padding: 5px;"></div>'
            
            # Get the number of days in the month
            if month == 12:
                last_day = pd.Timestamp(year=year+1, month=1, day=1) - pd.Timedelta(days=1)
            else:
                last_day = pd.Timestamp(year=year, month=month+1, day=1) - pd.Timedelta(days=1)
            
            num_days = last_day.day
            
            # Add cells for each day of the month
            for day in range(1, num_days + 1):
                date_str = f"{year}-{month:02d}-{day:02d}"
                
                # Check if this day is in our trading data
                day_data = month_data[month_data['Day'] == day]
                
                if len(day_data) > 0:
                    # This is a trading day, get the data
                    close_price = day_data['Close'].values[0]
                    ret = day_data['Return'].values[0]
                    
                    # Determine color based on return
                    if np.isnan(ret):
                        bg_color = "#FFFFFF"  # White for no return data
                    elif ret > 1:
                        bg_color = "#00AA00"  # Strong green for >1% gain
                    elif ret > 0:
                        bg_color = "#88CC88"  # Light green for 0-1% gain
                    elif ret < -1:
                        bg_color = "#AA0000"  # Strong red for >1% loss
                    elif ret < 0:
                        bg_color = "#CC8888"  # Light red for 0-1% loss
                    else:
                        bg_color = "#CCCCCC"  # Gray for no change
                    
                    # Create cell with trading data
                    calendar_html += f'''
                    <div style="background-color: {bg_color}; color: white; padding: 5px; border-radius: 5px; text-align: center;">
                        <div style="font-weight: bold;">{day}</div>
                        <div style="font-size: 0.8em;">{close_price:.2f}</div>
                        <div style="font-size: 0.7em;">{ret:.2f}%</div>
                    </div>
                    '''
                else:
                    # Not a trading day, just show the date
                    calendar_html += f'''
                    <div style="background-color: #F0F0F0; padding: 5px; border-radius: 5px; text-align: center;">
                        <div>{day}</div>
                    </div>
                    '''
            
            # Close the calendar grid
            calendar_html += '</div>'
            
            # Display the calendar
            st.markdown(calendar_html, unsafe_allow_html=True)
            
            # Add a legend
            legend_html = '''
            <div style="display: flex; gap: 10px; margin-top: 10px; margin-bottom: 20px;">
                <div style="display: flex; align-items: center;">
                    <div style="width: 15px; height: 15px; background-color: #00AA00; margin-right: 5px;"></div>
                    <span>Gain >1%</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 15px; height: 15px; background-color: #88CC88; margin-right: 5px;"></div>
                    <span>Gain 0-1%</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 15px; height: 15px; background-color: #CC8888; margin-right: 5px;"></div>
                    <span>Loss 0-1%</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 15px; height: 15px; background-color: #AA0000; margin-right: 5px;"></div>
                    <span>Loss >1%</span>
                </div>
            </div>
            '''
            st.markdown(legend_html, unsafe_allow_html=True)
    else:
        st.error("Calendar view requires datetime index data")


def render_recommendation_tab(signal_info, buy_score, sell_score, buy_reasons, sell_reasons, latest, past_30d, price_change_pct, volatility):
    """
    Render the trade recommendation tab with signals and explanation
    
    Args:
        signal_info (str): Signal recommendation (BUY/SELL/HOLD)
        buy_score (int): Buy signal score
        sell_score (int): Sell signal score
        buy_reasons (list): List of reasons to buy
        sell_reasons (list): List of reasons to sell
        latest (Series): Latest data point
        past_30d (DataFrame): Last 30 days of data
        price_change_pct (float): Price change percentage
        volatility (float): Volatility value
    """
    # Add trade recommendation with reasoning
    st.write("### 🎯 Trade Recommendation")
    
    # Create more interactive cards for the recommendations
    if signal_info == "BUY":
        # Create a visual buy recommendation card with progress bar for confidence
        st.markdown("""
        <div style="background-color: #d4edda; border-left: 5px solid #28a745; padding: 15px; border-radius: 5px;">
            <h4 style="margin-top: 0; color: #155724;">BUY Recommendation</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Show confidence score with a visual gauge
        confidence = buy_score / 5 * 100
        st.write(f"**Confidence Score:** {buy_score}/5 ({confidence:.0f}%)")
        st.progress(confidence/100)
        
        # Show reasoning in an expandable section
        with st.expander("View Detailed Reasoning"):
            for reason in buy_reasons:
                st.markdown(f"✅ {reason}")
        
        # Show target prices and strategy in a more visual way
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current Price", f"{latest['Close']:.2f}")
        with col2:
            target_price = latest['Close'] * 1.05
            st.metric("Target Price", f"{target_price:.2f}", "+5%")
        with col3:
            stop_loss = latest['Close'] * 0.97
            st.metric("Stop Loss", f"{stop_loss:.2f}", "-3%")
        
        # Add a risk/reward visualization
        st.write("**Risk/Reward Ratio:** 1:1.67")
        risk_reward_html = f"""
        <div style="display: flex; height: 20px; margin: 10px 0;">
            <div style="background-color: #dc3545; width: 37.5%; text-align: center; color: white;">Risk</div>
            <div style="background-color: #28a745; width: 62.5%; text-align: center; color: white;">Reward</div>
        </div>
        """
        st.markdown(risk_reward_html, unsafe_allow_html=True)
        
    elif signal_info == "SELL":
        # Create a visual sell recommendation card
        st.markdown("""
        <div style="background-color: #f8d7da; border-left: 5px solid #dc3545; padding: 15px; border-radius: 5px;">
            <h4 style="margin-top: 0; color: #721c24;">SELL Recommendation</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Show confidence score with a visual gauge
        confidence = sell_score / 5 * 100
        st.write(f"**Confidence Score:** {sell_score}/5 ({confidence:.0f}%)")
        st.progress(confidence/100)
        
        # Show reasoning in an expandable section
        with st.expander("View Detailed Reasoning"):
            for reason in sell_reasons:
                st.markdown(f"⚠️ {reason}")
        
        # Show target prices and strategy in a more visual way
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Current Price", f"{latest['Close']:.2f}")
        with col2:
            target_price = latest['Close'] * 0.95
            st.metric("Target Price", f"{target_price:.2f}", "-5%")
        with col3:
            stop_loss = latest['Close'] * 1.03
            st.metric("Stop Loss", f"{stop_loss:.2f}", "+3%")
        
        # Add a risk/reward visualization
        st.write("**Risk/Reward Ratio:** 1:1.67")
        risk_reward_html = f"""
        <div style="display: flex; height: 20px; margin: 10px 0;">
            <div style="background-color: #dc3545; width: 37.5%; text-align: center; color: white;">Risk</div>
            <div style="background-color: #28a745; width: 62.5%; text-align: center; color: white;">Reward</div>
        </div>
        """
        st.markdown(risk_reward_html, unsafe_allow_html=True)
        
    else:
        # Create a visual hold recommendation card
        st.markdown("""
        <div style="background-color: #fff3cd; border-left: 5px solid #ffc107; padding: 15px; border-radius: 5px;">
            <h4 style="margin-top: 0; color: #856404;">HOLD Recommendation</h4>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("Mixed signals detected. Consider waiting for clearer trend direction.")
        
        # Create a visual comparison of bullish vs bearish factors
        st.write(f"**Signal Strength:** {max(buy_score, sell_score)}/5")
        
        # Visual comparison of bullish/bearish factors
        comparison_html = f"""
        <div style="display: flex; height: 30px; margin: 10px 0; border-radius: 4px; overflow: hidden;">
            <div style="background-color: #28a745; width: {buy_score/5*100}%; text-align: center; color: white;">
                Bullish ({buy_score})
            </div>
            <div style="background-color: #dc3545; width: {sell_score/5*100}%; text-align: center; color: white;">
                Bearish ({sell_score})
            </div>
        </div>
        """
        st.markdown(comparison_html, unsafe_allow_html=True)
        
        # Show both bullish and bearish factors
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Bullish Factors:**")
            if buy_reasons:
                for reason in buy_reasons:
                    st.markdown(f"✅ {reason}")
            else:
                st.write("None found")
        with col2:
            st.write("**Bearish Factors:**")
            if sell_reasons:
                for reason in sell_reasons:
                    st.markdown(f"⚠️ {reason}")
            else:
                st.write("None found")
    
    # Historical performance stats in a single row of metrics
    st.write("### 📊 Historical Performance")
    
    # Calculate key stats
    returns = past_30d['Close'].pct_change().dropna()
    stats = {
        "30-Day Return": f"{price_change_pct:.2f}%",
        "Annualized Volatility": f"{volatility * np.sqrt(252):.2f}%",
        "Max Daily Gain": f"{returns.max() * 100:.2f}%",
        "Max Daily Loss": f"{returns.min() * 100:.2f}%",
        "Profitable Days": f"{np.sum(returns > 0)} / {len(returns)} ({np.sum(returns > 0)/len(returns)*100:.1f}%)"
    }
    
    # Display stats
    cols = st.columns(len(stats))
    for i, (label, value) in enumerate(stats.items()):
        with cols[i]:
            st.metric(label, value)
            
    # Add a new performance chart for more visual insight
    st.write("### Performance Distribution")
    # Create a histogram of daily returns
    fig_html = f"""
    <div style="width: 100%; height: 200px; background-color: #f8f9fa; border-radius: 5px; overflow: hidden;">
        <div style="padding: 10px; text-align: center; font-weight: bold;">Daily Returns Distribution</div>
        <div style="display: flex; align-items: flex-end; height: 150px; padding: 0 10px;">
    """
    
    # Bin the returns data for a histogram
    bins = np.linspace(returns.min(), returns.max(), 15)
    hist, bin_edges = np.histogram(returns, bins=bins)
    max_count = max(hist) if len(hist) > 0 else 1
    
    # Generate the histogram bars
    for i in range(len(hist)):
        height_pct = (hist[i] / max_count) * 100
        bar_color = "#28a745" if bin_edges[i] >= 0 else "#dc3545"
        
        # Create bar with tooltip showing range and count
        fig_html += f"""
        <div style="flex: 1; height: {height_pct}%; background-color: {bar_color}; margin: 0 1px; position: relative;"
             title="{bin_edges[i]:.2f}% to {bin_edges[i+1]:.2f}% ({hist[i]} days)"></div>
        """
    
    fig_html += """
        </div>
        <div style="display: flex; justify-content: space-between; padding: 0 10px; font-size: 0.8em;">
            <span>Min</span>
            <span>Negative</span>
            <span>0%</span>
            <span>Positive</span>
            <span>Max</span>
        </div>
    </div>
    """
    st.markdown(fig_html, unsafe_allow_html=True)