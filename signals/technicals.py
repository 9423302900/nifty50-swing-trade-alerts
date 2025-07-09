import pandas as pd
import yfinance as yf
from ta.trend import EMAIndicator, ADXIndicator
from ta.momentum import RSIIndicator
from ta.trend import MACD

def get_technical_signal(symbol):
    try:
        df = yf.download(symbol + ".NS", period="90d", interval="1d", progress=False)
        if df.empty:
            return None

        df.dropna(inplace=True)

        df["rsi"] = RSIIndicator(df["Close"], window=14).rsi()
        df["macd"] = MACD(df["Close"]).macd_diff()
        df["adx"] = ADXIndicator(df["High"], df["Low"], df["Close"]).adx()
        df["+DI"] = ADXIndicator(df["High"], df["Low"], df["Close"]).adx_pos()
        df["-DI"] = ADXIndicator(df["High"], df["Low"], df["Close"]).adx_neg()
        df["ema20"] = EMAIndicator(df["Close"], window=20).ema_indicator()
        df["ema50"] = EMAIndicator(df["Close"], window=50).ema_indicator()
        df["avg_vol"] = df["Volume"].rolling(window=20).mean()

        latest = df.iloc[-1]

        conditions = [
            latest["rsi"] > 60 and latest["rsi"] < 70,
            latest["macd"] > 0,
            latest["adx"] > 25 and latest["+DI"] > latest["-DI"],
            latest["Close"] > latest["ema20"],
            latest["Close"] > latest["ema50"],
            latest["Volume"] > 2 * latest["avg_vol"],
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
    df = pd.read_csv(nifty_csv)
    results = []
    for _, row in df.iterrows():
        result = get_technical_signal(row["symbol"])
        if result:
            results.append(result)
    return pd.DataFrame(results)
