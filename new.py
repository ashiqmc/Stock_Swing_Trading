import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import ta

# Fetch historical data
def get_stock_data(ticker, period="6mo", interval="1d"):
    stock = yf.Ticker(ticker)
    df = stock.history(period=period, interval=interval)
    df["Ticker"] = ticker
    return df

# Calculate Technical Indicators
def calculate_indicators(df):
    df["SMA_50"] = df["Close"].rolling(window=50).mean()
    df["SMA_200"] = df["Close"].rolling(window=200).mean()
    
    df["RSI"] = ta.momentum.RSIIndicator(df["Close"], window=14).rsi()
    df["MACD"] = ta.trend.MACD(df["Close"]).macd()
    df["MACD_Signal"] = ta.trend.MACD(df["Close"]).macd_signal()
    
    df["ADX"] = ta.trend.ADXIndicator(df["High"], df["Low"], df["Close"]).adx()
    df["CCI"] = ta.trend.CCIIndicator(df["High"], df["Low"], df["Close"], window=20).cci()
    df["ROC"] = ta.momentum.ROCIndicator(df["Close"], window=12).roc()
    df["Williams_R"] = ta.momentum.WilliamsRIndicator(df["High"], df["Low"], df["Close"], lbp=14).williams_r()
    df["Parabolic_SAR"] = ta.trend.PSARIndicator(df["High"], df["Low"], df["Close"]).psar()

    return df

# Calculate Fibonacci Levels
def fibonacci_retracement(df):
    max_price = df["Close"].max()
    min_price = df["Close"].min()
    
    fib_levels = [0.236, 0.382, 0.5, 0.618, 0.786]
    fib_prices = {level: min_price + (max_price - min_price) * level for level in fib_levels}
    
    return fib_prices

# Generate Buy/Sell Signals
def generate_signals(df):
    signals = []
    
    if df["SMA_50"].iloc[-1] > df["SMA_200"].iloc[-1]:
        signals.append("Bullish Crossover (Golden Cross)")
    
    if df["RSI"].iloc[-1] < 30:
        signals.append("RSI Oversold (Buy Signal)")
    elif df["RSI"].iloc[-1] > 70:
        signals.append("RSI Overbought (Sell Signal)")
    
    if df["MACD"].iloc[-1] > df["MACD_Signal"].iloc[-1]:
        signals.append("MACD Bullish Crossover (Buy)")
    elif df["MACD"].iloc[-1] < df["MACD_Signal"].iloc[-1]:
        signals.append("MACD Bearish Crossover (Sell)")
    
    if df["CCI"].iloc[-1] < -100:
        signals.append("CCI Oversold (Buy)")
    elif df["CCI"].iloc[-1] > 100:
        signals.append("CCI Overbought (Sell)")
    
    if df["ADX"].iloc[-1] > 25:
        signals.append("Strong Trend (ADX Confirmation)")
    
    if df["Williams_R"].iloc[-1] < -80:
        signals.append("Williams %R Oversold (Buy)")
    elif df["Williams_R"].iloc[-1] > -20:
        signals.append("Williams %R Overbought (Sell)")
    
    return signals

# Plot Stock Data with Indicators
def plot_stock(df, ticker):
    plt.figure(figsize=(12,6))
    
    # Price and Moving Averages
    plt.plot(df["Close"], label=f"{ticker} Price", color="blue")
    plt.plot(df["SMA_50"], label="50-Day SMA", linestyle="--", color="orange")
    plt.plot(df["SMA_200"], label="200-Day SMA", linestyle="--", color="red")
    
    # Highlight Fibonacci Levels
    fib_prices = fibonacci_retracement(df)
    for level, price in fib_prices.items():
        plt.axhline(y=price, linestyle="--", alpha=0.5, label=f"Fibonacci {level:.3f}")

    plt.title(f"{ticker} Price Chart with Indicators")
    plt.legend()
    plt.grid()
    plt.show()
    
    # RSI Plot
    plt.figure(figsize=(12,4))
    plt.plot(df["RSI"], label="RSI", color="purple")
    plt.axhline(70, linestyle="--", color="red", alpha=0.5)
    plt.axhline(30, linestyle="--", color="green", alpha=0.5)
    plt.title(f"{ticker} RSI Indicator")
    plt.legend()
    plt.grid()
    plt.show()
    
    # MACD Plot
    plt.figure(figsize=(12,4))
    plt.plot(df["MACD"], label="MACD", color="blue")
    plt.plot(df["MACD_Signal"], label="MACD Signal", linestyle="--", color="red")
    plt.axhline(0, linestyle="--", color="black", alpha=0.5)
    plt.title(f"{ticker} MACD Indicator")
    plt.legend()
    plt.grid()
    plt.show()

# Run Analysis on a List of Stocks/ETFs
stock_list = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "NFLX", "AMD", "DIS",
              "NIFTY50.NS", "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
              "ITC.NS", "LT.NS", "HUL.NS", "KOTAKBANK.NS"]

for stock in stock_list:
    try:
        print(f"\n🔍 Analyzing {stock} ...")
        df = get_stock_data(stock)
        df = calculate_indicators(df)
        signals = generate_signals(df)
        
        print(f"📈 Fibonacci Levels for {stock}:")
        fib_levels = fibonacci_retracement(df)
        for level, price in fib_levels.items():
            print(f" - {level:.3f}: {price:.2f}")
        
        print("\n💡 Trading Signals:")
        for signal in signals:
            print(f"✅ {signal}")
        
        plot_stock(df, stock)
    
    except Exception as e:
        print(f"⚠ Error analyzing {stock}: {e}")
