"""
Computes returns, moving averages, drawdown, delivery-percentage trend
and golden/death cross events from the cleaned ITC data. Saves
output/itc_analysis.csv and output/yearly_summary.csv, and prints a
summary to the console.
"""

import os
import numpy as np
import pandas as pd

from config import CLEANED_FILE, OUTPUT_DIR, SMA_SHORT, SMA_LONG, TRADING_DAYS


def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["DailyReturn"] = df["Close Price"].pct_change()
    df[f"SMA{SMA_SHORT}"] = df["Close Price"].rolling(SMA_SHORT).mean()
    df[f"SMA{SMA_LONG}"] = df["Close Price"].rolling(SMA_LONG).mean()

    # Running maximum and drawdown from peak
    df["RunningMax"] = df["Close Price"].cummax()
    df["Drawdown"] = df["Close Price"] / df["RunningMax"] - 1

    return df


def flag_crosses(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    short_col, long_col = f"SMA{SMA_SHORT}", f"SMA{SMA_LONG}"
    diff = df[short_col] - df[long_col]
    prev_diff = diff.shift(1)

    df["GoldenCross"] = (prev_diff <= 0) & (diff > 0)
    df["DeathCross"] = (prev_diff >= 0) & (diff < 0)
    return df


def yearly_summary(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Year"] = df["Date"].dt.year

    rows = []
    for year, group in df.groupby("Year"):
        group = group.sort_values("Date")
        year_return = group["Close Price"].iloc[-1] / group["Close Price"].iloc[0] - 1
        avg_delivery_pct = group["% Dly Qt to Traded Qty"].mean()
        avg_volume = group["Total Traded Quantity"].mean()
        rows.append({
            "Year": year,
            "OpenPrice": group["Close Price"].iloc[0],
            "ClosePrice": group["Close Price"].iloc[-1],
            "YearReturn": year_return,
            "AvgDeliveryPct": avg_delivery_pct,
            "AvgDailyVolume": avg_volume,
            "TradingDays": len(group),
        })
    return pd.DataFrame(rows)


def main():
    df = pd.read_csv(CLEANED_FILE, parse_dates=["Date"])
    df = compute_indicators(df)
    df = flag_crosses(df)

    out_path = os.path.join(OUTPUT_DIR, "itc_analysis.csv")
    df.to_csv(out_path, index=False)

    yearly = yearly_summary(df)
    yearly_path = os.path.join(OUTPUT_DIR, "yearly_summary.csv")
    yearly.to_csv(yearly_path, index=False)

    total_return = df["Close Price"].iloc[-1] / df["Close Price"].iloc[0] - 1
    n_years = (df["Date"].iloc[-1] - df["Date"].iloc[0]).days / 365.25
    cagr = (1 + total_return) ** (1 / n_years) - 1
    daily_vol = df["DailyReturn"].std()
    annualized_vol = daily_vol * np.sqrt(TRADING_DAYS)
    max_drawdown = df["Drawdown"].min()
    avg_delivery_pct = df["% Dly Qt to Traded Qty"].mean()
    n_golden = int(df["GoldenCross"].sum())
    n_death = int(df["DeathCross"].sum())

    print(f"Saved {len(df)} rows to {out_path}")
    print(f"Saved yearly summary to {yearly_path}\n")
    print(f"Period: {df['Date'].min().date()} to {df['Date'].max().date()}")
    print(f"Close price: {df['Close Price'].iloc[0]:.2f} -> {df['Close Price'].iloc[-1]:.2f} "
          f"({total_return:+.2%} total, {cagr:+.2%} CAGR)")
    print(f"Annualized volatility: {annualized_vol:.2%}")
    print(f"Maximum drawdown from peak: {max_drawdown:.2%}")
    print(f"Average delivery percentage: {avg_delivery_pct:.1f}%")
    print(f"Golden cross events (50 DMA crossing above 200 DMA): {n_golden}")
    print(f"Death cross events (50 DMA crossing below 200 DMA): {n_death}")
    print("\nYearly summary:")
    print(yearly.to_string(index=False))


if __name__ == "__main__":
    main()
