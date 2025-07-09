import streamlit as st
import pandas as pd
from signals.technicals import run_screener
from signals.screener import load_fundamentals
from utils.alert import send_telegram_message

st.set_page_config(layout="wide")
st.title("📈 NIFTY50 Swing Trade Signal Dashboard")

tech_signals = run_screener()
st.success(f"✅ Found {len(tech_signals)} stocks with breakout setups")

fund_signals = load_fundamentals()
st.write("Tech signal columns:", tech_signals.columns.tolist())
st.write("Fundamental columns:", fund_signals.columns.tolist())

merged = pd.merge(tech_signals, fund_signals, on="symbol", how="inner")


if merged.empty:
    st.warning("⚠️ No stocks meet both technical and fundamental criteria")
else:
    st.subheader("🟢 Final Swing Trade Candidates")

    def calc_targets(row):
        entry = row["close"]
        row["target"] = round(entry * 1.20, 2)
        row["stoploss"] = round(entry * 0.92, 2)
        return row

    merged = merged.apply(calc_targets, axis=1)

    st.dataframe(merged[[
        "symbol", "close", "rsi", "adx", "eps_growth", "roe", "target", "stoploss"
    ]])

    selected = st.multiselect("📬 Select Stocks to Alert", merged["symbol"].tolist())
    if st.button("🚀 Send Alerts"):
        for symbol in selected:
            stock = merged[merged["symbol"] == symbol].iloc[0]
            message = f'''
📈 *Swing Trade Alert* – {symbol}

🔔 *Entry*: ₹{stock['close']}
🎯 *Target*: ₹{stock['target']} (+20%)
🛑 *Stoploss*: ₹{stock['stoploss']}

📊 *RSI*: {stock['rsi']}, *ADX*: {stock['adx']}
📈 *EPS Growth*: {stock['eps_growth']}%, *ROE*: {stock['roe']}%
🕒 *Timeframe*: 2–4 weeks
'''
            if send_telegram_message(message):
                st.success(f"✅ Alert sent for {symbol}")
            else:
                st.error(f"❌ Failed to send alert for {symbol}")
