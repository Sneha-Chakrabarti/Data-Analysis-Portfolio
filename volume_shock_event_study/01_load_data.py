"""
Loads the 20 raw daily OHLCV CSVs and builds two wide matrices, close
prices and traded volume, restricted to the common date range. Saves
data/prices_wide.csv and data/volume_wide.csv.
"""

import os
import pandas as pd

from config import RAW_DIR, DATA_DIR, UNIVERSE, START_DATE, END_DATE


def load_one(symbol: str) -> pd.DataFrame:
    path = os.path.join(RAW_DIR, f"{symbol}.csv")
    df = pd.read_csv(path, usecols=["Date", "Close", "Volume"])
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.drop_duplicates(subset="Date").set_index("Date")
    return df.rename(columns={"Close": symbol + "_close", "Volume": symbol + "_volume"})


def main():
    frames = [load_one(sym) for sym in UNIVERSE]
    merged = pd.concat(frames, axis=1, sort=False).sort_index()
    merged = merged.loc[START_DATE:END_DATE]

    close_cols = [c for c in merged.columns if c.endswith("_close")]
    vol_cols = [c for c in merged.columns if c.endswith("_volume")]

    prices = merged[close_cols].copy()
    prices.columns = [c.replace("_close", "") for c in prices.columns]
    volume = merged[vol_cols].copy()
    volume.columns = [c.replace("_volume", "") for c in volume.columns]

    n_before = len(prices)
    complete = prices.dropna(how="any").index.intersection(volume.dropna(how="any").index)
    prices = prices.loc[complete]
    volume = volume.loc[complete]

    prices.to_csv(os.path.join(DATA_DIR, "prices_wide.csv"))
    volume.to_csv(os.path.join(DATA_DIR, "volume_wide.csv"))

    print(f"Merged {len(UNIVERSE)} stocks, {START_DATE} to {END_DATE}")
    print(f"Rows before dropping incomplete dates: {n_before}")
    print(f"Rows after (fully complete price AND volume): {len(prices)}")


if __name__ == "__main__":
    main()
