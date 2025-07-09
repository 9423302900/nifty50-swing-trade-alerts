import pandas as pd
import yfinance as yf
from ta.trend import EMAIndicator, ADXIndicator, MACD
from ta.momentum import RSIIndicator

def get_technical_signal(symbol):
    try:
        df = yf.download(symbol + ".NS", period="90d", interval="1d", progress=False)
        if df.empty:
            return None

        df.dropna(inplace=True)

        # Indicators
        rsi = RSIIndicator(close=df["Close"], window=14)
        macd = MACD(close=df["Close"])
        adx = ADXIndicator(high=df["High"], low=df["Low"], close=df["Close"])
        ema20 = EMAIndicator(close=df["Close"], window=20)
        ema50 = EMAIndicator(close=df["Close"], window=50)

        # Calculations
        df["rsi"] = rsi.rsi()
        df["macd"] = macd.macd_diff()
        df["adx"] = adx.adx()
        df["+DI"] = adx.adx_pos()
        df["-DI"] = adx.adx_neg()
        df["ema20"] = ema20.ema_indicator()
        df["ema50"] = ema50.ema_indicator()
        df["avg_vol"] = df["Volume"].rolling(window=20).mean()

        latest = df.iloc[-1]

        # Relaxed conditions
        conditions = [
            latest["rsi"] > 55,
            latest["macd"] > 0,
            latest["adx"] > 20,
            latest["Close"] > latest["ema20"],
        ]

        if all(conditions):
            return {
                "symbol": symbol,
                "rsi": round(latest["rsi"], 2),
                "adx": round(latest["adx"], 2),
                "macd": round(latest["macd"], 2),
                "close": round(latest["Close"], 2),
                "volume": int(latest["Volume"]),
            }

        return None

    except Exception as e:
        print(f"Error for {symbol}: {e}")
        return None

def run_screener(nifty_csv="data/nifty50.csv"):
    import streamlit as st  # Add this only if you're running from app.py
    df = pd.read_csv(nifty_csv)
    st.write("📄 Nifty50 symbols loaded:", df["symbol"].tolist())
    
    results = []
    for symbol in df["symbol"]:
        st.write(f"🔍 Checking {symbol}...")
        result = get_technical_signal(symbol)
        if result:
            st.success(f"✅ Match found: {result}")
            results.append(result)
        else:
            st.warning(f"❌ No signal for {symbol}")
    
    st.write(f"📊 Total signals found: {len(results)}")
    return pd.DataFrame(results)


