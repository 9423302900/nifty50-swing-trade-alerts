import pandas as pd

def load_fundamentals(csv_path="data/fundamentals.csv"):
    df = pd.read_csv(csv_path)
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

    df = df[
        (df["eps_growth"] > 15) &
        (df["roe"] > 15) &
        (df["peg"] < 1.5) &
        (df["debt_to_equity"] < 0.5)
    ]

    return df
