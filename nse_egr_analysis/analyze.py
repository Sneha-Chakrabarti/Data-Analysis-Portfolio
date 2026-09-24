"""
Computes daily returns, volatility, and liquidity metrics from the
cleaned EGR data. Saves output/egr_analysis.csv and prints a summary.
"""

import os
import numpy as np
import pandas as pd

from config import CLEANED_FILE, OUTPUT_DIR

TRADING_DAYS = 252


def main():
    df = pd.read_csv(CLEANED_FILE, parse_dates=["Date"])

    df["DailyReturn"] = df["Close Price"].pct_change()
    df["DailyRange"] = df["High Price"] - df["Low Price"]
    df["DailyRangePct"] = df["DailyRange"] / df["Open Price"]
    df["AvgTradeSize"] = df["Value"] / df["No. Of Trades"]
    df["Turnover"] = df["Value"]

    out_path = os.path.join(OUTPUT_DIR, "egr_analysis.csv")
    df.to_csv(out_path, index=False)

    n_days = len(df)
    total_return = df["Close Price"].iloc[-1] / df["Close Price"].iloc[0] - 1
    daily_vol = df["DailyReturn"].std()
    annualized_vol = daily_vol * np.sqrt(TRADING_DAYS)
    avg_daily_volume = df["Total Traded Quantity"].mean()
    avg_daily_value = df["Value"].mean()
    avg_trades_per_day = df["No. Of Trades"].mean()

    print(f"Saved {n_days} rows to {out_path}\n")
    print(f"Period: {df['Date'].min().date()} to {df['Date'].max().date()} ({n_days} trading days)")
    print(f"Close price: {df['Close Price'].iloc[0]:,.2f} -> {df['Close Price'].iloc[-1]:,.2f} "
          f"({total_return:+.2%})")
    print(f"Daily volatility: {daily_vol:.2%}")
    print(f"Annualized volatility (naive, from {n_days} days): {annualized_vol:.2%}")
    print(f"Average daily traded quantity: {avg_daily_volume:,.0f} units")
    print(f"Average daily traded value: Rs {avg_daily_value:,.0f}")
    print(f"Average trades per day: {avg_trades_per_day:,.1f}")
    print(f"Average trade size: Rs {(avg_daily_value / avg_trades_per_day):,.0f}")


if __name__ == "__main__":
    main()
