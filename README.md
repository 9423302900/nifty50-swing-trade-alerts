# 📈 NIFTY50 Swing Trade Alerts

A Streamlit dashboard to generate swing trade signals using both technical and fundamental filters for NIFTY50 stocks.

## Features

- Technical Filters: RSI, MACD, ADX, EMA
- Fundamental Filters: EPS growth, ROE, PEG, Debt-Equity
- Calculates Entry, Target (20%) and Stoploss (8%)
- Sends Telegram alerts

## Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

Edit `config.py` with your Telegram Bot Token and Chat ID.
