import pandas as pd
import yfinance as yf
from ta.trend import EMAIndicator, ADXIndicator, MACD
from ta.momentum import RSIIndicator

import streamlit as st

def get_technical_signal(symbol):
    try:
        df = yf.download(symbol + ".NS", period="90d", interval="1d", progress=False)
        if df.empty:
            st.warning(f"⚠️ No data from Yahoo for {symbol}")
            return None

        df.dropna(inplace=True)

        # Indicators
        rsi = RSIIndicator(close=df["Close"], window=14)
        macd = MACD(close=df["Close"])
        adx = ADXIndicator(high=df["High"], low=df["Low"], close=df["Close"])
        ema20 = EMAIndicator(close=df["Close"], window=20)
        ema50 = EMAIndicator(close=df["Close"], window=50)

        df["rsi"] = rsi.rsi()
        df["macd"] = macd.macd_diff()
        df["adx"] = adx.adx()
        df["+DI"] = adx.adx_pos()
        df["-DI"] = adx.adx_neg()
        df["ema20"] = ema20.ema_indicator()
        df["ema50"] = ema50.ema_indicator()
        df["avg_vol"] = df["Volume"].rolling(window=20).mean()

        latest = df.iloc[-1]

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
        else:
            st.info(f"ℹ️ {symbol} did not meet conditions: RSI={latest['rsi']:.1f}, MACD={latest['macd']:.2f}, ADX={latest['adx']:.1f}")
            return None

    except Exception as e:
        st.error(f"❌ Error for {symbol}: {e}")
        return None



