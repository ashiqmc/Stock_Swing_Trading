import streamlit as st
import pandas as pd
import numpy as np
import ta
from ta.volume import OnBalanceVolumeIndicator, AccDistIndexIndicator
from ta.volatility import AverageTrueRange
from ta.trend import ADXIndicator, PSARIndicator, IchimokuIndicator, VortexIndicator
from ta.momentum import StochasticOscillator

from data_fetcher import fetch_stock_data

@st.cache_data
def get_signal(ticker):
    """
    Calculate technical indicators and generate trading signals with enhanced criteria
    
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
    required_cols = ['Close', 'High', 'Low', 'Volume']
    missing_cols = [col for col in required_cols if col not in data.columns]
    if missing_cols:
        st.error(f"Missing columns in {ticker} data: {missing_cols}")
        return None
    
    # Calculate indicators
    try:
        # TREND & MOMENTUM INDICATORS
        # Moving Averages
        data["SMA_50"] = ta.trend.sma_indicator(data["Close"], window=50)
        data["SMA_100"] = ta.trend.sma_indicator(data["Close"], window=100)
        data["SMA_200"] = ta.trend.sma_indicator(data["Close"], window=200)
        data["EMA_50"] = ta.trend.ema_indicator(data["Close"], window=50)
        data["EMA_100"] = ta.trend.ema_indicator(data["Close"], window=100)
        data["EMA_200"] = ta.trend.ema_indicator(data["Close"], window=200)
        
        # Relative Strength Index
        data["RSI"] = ta.momentum.rsi(data["Close"], window=14)
        
        # MACD
        data["MACD"] = ta.trend.macd(data["Close"])
        data["MACD_Signal"] = ta.trend.macd_signal(data["Close"])
        data["MACD_Hist"] = data["MACD"] - data["MACD_Signal"]
        
        # ADX Indicator
        adx_indicator = ADXIndicator(data["High"], data["Low"], data["Close"], window=14)
        data["ADX"] = adx_indicator.adx()
        data["DI_Plus"] = adx_indicator.adx_pos()
        data["DI_Minus"] = adx_indicator.adx_neg()
        
        # Ichimoku Cloud
        ichimoku = IchimokuIndicator(data["High"], data["Low"])
        data["Ichimoku_Conversion_Line"] = ichimoku.ichimoku_conversion_line()
        data["Ichimoku_Base_Line"] = ichimoku.ichimoku_base_line()
        data["Ichimoku_A"] = ichimoku.ichimoku_a()
        data["Ichimoku_B"] = ichimoku.ichimoku_b()
        
        # Stochastic Oscillator
        stoch = StochasticOscillator(data["High"], data["Low"], data["Close"])
        data["Stoch_K"] = stoch.stoch()
        data["Stoch_D"] = stoch.stoch_signal()
        
        # Vortex Indicator
        vortex = VortexIndicator(data["High"], data["Low"], data["Close"], window=14)
        data["Vortex_Positive"] = vortex.vortex_indicator_pos()
        data["Vortex_Negative"] = vortex.vortex_indicator_neg()
        
        # PRICE ACTION & VOLATILITY INDICATORS
        # Bollinger Bands
        data["Upper_BB"] = ta.volatility.bollinger_hband(data["Close"])
        data["Middle_BB"] = ta.volatility.bollinger_mavg(data["Close"])
        data["Lower_BB"] = ta.volatility.bollinger_lband(data["Close"])
        data["BB_Width"] = (data["Upper_BB"] - data["Lower_BB"]) / data["Middle_BB"]
        
        # Average True Range
        atr = AverageTrueRange(data["High"], data["Low"], data["Close"])
        data["ATR"] = atr.average_true_range()
        data["ATR_Percent"] = data["ATR"] / data["Close"] * 100
        
        # Parabolic SAR
        psar = PSARIndicator(data["High"], data["Low"], data["Close"])
        data["PSAR"] = psar.psar()
        data["PSAR_Up"] = psar.psar_up()
        data["PSAR_Down"] = psar.psar_down()
        data["PSAR_Up_Indicator"] = psar.psar_up_indicator()
        data["PSAR_Down_Indicator"] = psar.psar_down_indicator()
        
        # VWAP (Simplified daily calculation)
        data["Typical_Price"] = (data["High"] + data["Low"] + data["Close"]) / 3
        data["VP"] = data["Typical_Price"] * data["Volume"]
        data["VWAP"] = data["VP"].cumsum() / data["Volume"].cumsum()
        
        # VOLUME INDICATORS
        # On-Balance Volume
        obv = OnBalanceVolumeIndicator(data["Close"], data["Volume"])
        data["OBV"] = obv.on_balance_volume()
        data["OBV_EMA"] = ta.trend.ema_indicator(data["OBV"], window=20)
        
        # Accumulation/Distribution Line
        ad = AccDistIndexIndicator(data["High"], data["Low"], data["Close"], data["Volume"])
        data["AD_Line"] = ad.acc_dist_index()
        data["AD_EMA"] = ta.trend.ema_indicator(data["AD_Line"], window=20)
        
        # Volume Change
        data["Volume_Change"] = data["Volume"].pct_change()
        data["Volume_MA"] = ta.trend.sma_indicator(data["Volume"], window=20)
        data["Volume_Ratio"] = data["Volume"] / data["Volume_MA"]
        
        # SUPPORT & RESISTANCE (Basic calculations)
        # Calculate pivot points (simple version)
        data["PP"] = (data["High"].shift(1) + data["Low"].shift(1) + data["Close"].shift(1)) / 3
        data["R1"] = 2 * data["PP"] - data["Low"].shift(1)
        data["S1"] = 2 * data["PP"] - data["High"].shift(1)
        data["R2"] = data["PP"] + (data["High"].shift(1) - data["Low"].shift(1))
        data["S2"] = data["PP"] - (data["High"].shift(1) - data["Low"].shift(1))
        
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
        buy_reasons = []
        
        # TREND & MOMENTUM BUY SIGNALS
        # RSI oversold condition
        if last_row["RSI"] < 30:
            buy_score += 1
            buy_reasons.append("RSI below 30 (oversold)")
        elif last_row["RSI"] < 40:
            buy_score += 0.5
            buy_reasons.append("RSI below 40 (approaching oversold)")
            
        # Moving average golden crosses
        if last_row["SMA_50"] > last_row["SMA_200"]:
            buy_score += 1
            buy_reasons.append("Golden Cross: 50-day SMA above 200-day")
        if last_row["EMA_50"] > last_row["EMA_200"]:
            buy_score += 1
            buy_reasons.append("Golden Cross: 50-day EMA above 200-day")
            
        # MACD crossover
        if last_row["MACD"] > last_row["MACD_Signal"]:
            buy_score += 1
            buy_reasons.append("MACD above signal line (bullish)")
        
        # ADX strong trend with positive DI
        if last_row["ADX"] > 25 and last_row["DI_Plus"] > last_row["DI_Minus"]:
            buy_score += 1
            buy_reasons.append("Strong bullish trend (ADX > 25 with +DI > -DI)")
            
        # Ichimoku bullish signals
        if (last_row["Close"] > last_row["Ichimoku_A"] and 
            last_row["Close"] > last_row["Ichimoku_B"]):
            buy_score += 1
            buy_reasons.append("Price above Ichimoku Cloud (bullish)")
            
        # Stochastic bullish crossover in oversold region
        if (last_row["Stoch_K"] < 30 and last_row["Stoch_D"] < 30 and 
            last_row["Stoch_K"] > last_row["Stoch_D"]):
            buy_score += 1
            buy_reasons.append("Stochastic bullish crossover in oversold region")
            
        # PRICE ACTION & VOLATILITY BUY SIGNALS
        # Bollinger Bands signals
        if last_row["Close"] <= last_row["Lower_BB"]:
            buy_score += 1
            buy_reasons.append("Price at lower Bollinger Band (potential reversal)")
            
        # Parabolic SAR buy signal
        if last_row["PSAR_Up_Indicator"] == 1:
            buy_score += 1
            buy_reasons.append("Parabolic SAR bullish signal")
            
        # Price above VWAP
        if last_row["Close"] > last_row["VWAP"]:
            buy_score += 0.5
            buy_reasons.append("Price above VWAP (bullish)")
            
        # VOLUME BUY SIGNALS
        # OBV increasing
        if last_row["OBV"] > last_row["OBV_EMA"]:
            buy_score += 1
            buy_reasons.append("OBV above its EMA (increasing buying pressure)")
            
        # A/D Line increasing
        if last_row["AD_Line"] > last_row["AD_EMA"]:
            buy_score += 1
            buy_reasons.append("Accumulation/Distribution Line rising")
            
        # Increasing volume
        if last_row["Volume_Ratio"] > 1.5:
            buy_score += 1
            buy_reasons.append("Volume spike (50% above average)")
        elif last_row["Volume_Ratio"] > 1:
            buy_score += 0.5
            buy_reasons.append("Above average volume")
            
        # SUPPORT & RESISTANCE BUY SIGNALS
        # Price near support level
        if (last_row["Close"] < last_row["S1"] * 1.01 and 
            last_row["Close"] > last_row["S1"] * 0.99):
            buy_score += 1
            buy_reasons.append("Price near support level S1")
            
        # Sell score system (count how many sell conditions are met)
        sell_score = 0
        sell_reasons = []
        
        # TREND & MOMENTUM SELL SIGNALS
        # RSI overbought condition
        if last_row["RSI"] > 70:
            sell_score += 1
            sell_reasons.append("RSI above 70 (overbought)")
        elif last_row["RSI"] > 60:
            sell_score += 0.5
            sell_reasons.append("RSI above 60 (approaching overbought)")
            
        # Moving average death crosses
        if last_row["SMA_50"] < last_row["SMA_200"]:
            sell_score += 1
            sell_reasons.append("Death Cross: 50-day SMA below 200-day")
        if last_row["EMA_50"] < last_row["EMA_200"]:
            sell_score += 1
            sell_reasons.append("Death Cross: 50-day EMA below 200-day")
            
        # MACD bearish crossover
        if last_row["MACD"] < last_row["MACD_Signal"]:
            sell_score += 1
            sell_reasons.append("MACD below signal line (bearish)")
            
        # ADX strong trend with negative DI
        if last_row["ADX"] > 25 and last_row["DI_Minus"] > last_row["DI_Plus"]:
            sell_score += 1
            sell_reasons.append("Strong bearish trend (ADX > 25 with -DI > +DI)")
            
        # Ichimoku bearish signals
        if (last_row["Close"] < last_row["Ichimoku_A"] and 
            last_row["Close"] < last_row["Ichimoku_B"]):
            sell_score += 1
            sell_reasons.append("Price below Ichimoku Cloud (bearish)")
            
        # Stochastic bearish crossover in overbought region
        if (last_row["Stoch_K"] > 70 and last_row["Stoch_D"] > 70 and 
            last_row["Stoch_K"] < last_row["Stoch_D"]):
            sell_score += 1
            sell_reasons.append("Stochastic bearish crossover in overbought region")
            
        # PRICE ACTION & VOLATILITY SELL SIGNALS
        # Bollinger Bands signals
        if last_row["Close"] >= last_row["Upper_BB"]:
            sell_score += 1
            sell_reasons.append("Price at upper Bollinger Band (potential reversal)")
            
        # Parabolic SAR sell signal
        if last_row["PSAR_Down_Indicator"] == 1:
            sell_score += 1
            sell_reasons.append("Parabolic SAR bearish signal")
            
        # Price below VWAP
        if last_row["Close"] < last_row["VWAP"]:
            sell_score += 0.5
            sell_reasons.append("Price below VWAP (bearish)")
            
        # VOLUME SELL SIGNALS
        # OBV decreasing
        if last_row["OBV"] < last_row["OBV_EMA"]:
            sell_score += 1
            sell_reasons.append("OBV below its EMA (decreasing buying pressure)")
            
        # A/D Line decreasing
        if last_row["AD_Line"] < last_row["AD_EMA"]:
            sell_score += 1
            sell_reasons.append("Accumulation/Distribution Line falling")
            
        # Decreasing volume on up days
        if last_row["Close"] > data.iloc[-2]["Close"] and last_row["Volume_Ratio"] < 0.7:
            sell_score += 1
            sell_reasons.append("Low volume on up day (30% below average)")
            
        # SUPPORT & RESISTANCE SELL SIGNALS
        # Price near resistance level
        if (last_row["Close"] < last_row["R1"] * 1.01 and 
            last_row["Close"] > last_row["R1"] * 0.99):
            sell_score += 1
            sell_reasons.append("Price near resistance level R1")
        
        # Calculate the strength of signals as percentages
        buy_strength = (buy_score / 15) * 100  # 15 possible buy signals
        sell_strength = (sell_score / 15) * 100  # 15 possible sell signals
        
        # Decision making based on scores with more nuance
        signal_info = {
            "buy_score": buy_score,
            "sell_score": sell_score,
            "buy_strength": buy_strength,
            "sell_strength": sell_strength,
            "buy_reasons": buy_reasons,
            "sell_reasons": sell_reasons
        }
        
        # Clear buy or sell signals
        if buy_score >= 6 and buy_score > sell_score * 1.5:
            return "STRONG BUY", data, signal_info
        elif buy_score >= 4 and buy_score > sell_score:
            return "BUY", data, signal_info
        elif sell_score >= 6 and sell_score > buy_score * 1.5:
            return "STRONG SELL", data, signal_info
        elif sell_score >= 4 and sell_score > buy_score:
            return "SELL", data, signal_info
        elif buy_score > sell_score:
            return "WEAK BUY", data, signal_info
        elif sell_score > buy_score:
            return "WEAK SELL", data, signal_info
        else:
            return "NEUTRAL", data, signal_info
            
    except Exception as e:
        st.error(f"Error generating signal for {ticker}: {str(e)}")
        return None