import streamlit as st
import pandas as pd
from signals.technicals import run_screener
from signals.screener import load_fundamentals
from utils.alert import send_telegram_message

st.set_page_config(layout="wide")
st.title("📈 NIFTY50 Swing Trade Signal Dashboard")

# Run technical screener
tech_signals = run_screener()
st.write("⚙️ Tech signal columns:", tech_signals.columns.tolist())
st.write("🧾 Tech signals preview:")
st.dataframe(tech_signals)

# Handle case when no technical signals are found
if tech_signals.empty:
    st.warning("⚠️ No technical signals found. Check indicator conditions or data files.")
    st.stop()

# Load fundamentals
fund_signals = load_fundamentals()
st.write("📊 Fundamental columns:", fund_signals.columns.tolist())

# Merge on 'symbol'
try:
    merged = pd.merge(tech_signals, fund_signals, on="symbol", how="inner")
except KeyError as e:
    st.error(f"Merge failed: missing column {e}")
    st.stop()

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

