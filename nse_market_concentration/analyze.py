"""
Computes rolling averages, fiscal-year averages, and linear trends for
the Top-N turnover-share series (securities and members/brokers), and
compares how concentrated trading is on the securities side versus the
member side. Saves output/concentration_analysis.csv and
output/fiscal_year_summary.csv.
"""

import os
import numpy as np
import pandas as pd

from config import INPUT_FILE, OUTPUT_DIR, ROLLING_WINDOW

TOP_N_COLS_SEC = ["Securities_Top5", "Securities_Top10", "Securities_Top25",
                   "Securities_Top50", "Securities_Top100"]
TOP_N_COLS_MEM = ["Members_Top5", "Members_Top10", "Members_Top25",
                   "Members_Top50", "Members_Top100"]


def fiscal_year(month_str: str) -> str:
    """NSE's reporting year runs April to March, e.g. 2022-04 to
    2023-03 is fiscal year 2022-2023."""
    year, month = int(month_str[:4]), int(month_str[5:7])
    if month >= 4:
        return f"{year}-{year + 1}"
    return f"{year - 1}-{year}"


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df = pd.read_csv(INPUT_FILE)
    df["MonthDate"] = pd.to_datetime(df["Month"], format="%Y-%m")
    df = df.sort_values("MonthDate").reset_index(drop=True)
    df["FiscalYear"] = df["Month"].apply(fiscal_year)

    for col in TOP_N_COLS_SEC + TOP_N_COLS_MEM:
        df[f"{col}_Rolling3M"] = df[col].rolling(ROLLING_WINDOW).mean()

    out_path = os.path.join(OUTPUT_DIR, "concentration_analysis.csv")
    df.to_csv(out_path, index=False)

    fiscal_summary = df.groupby("FiscalYear")[TOP_N_COLS_SEC + TOP_N_COLS_MEM].mean().round(1)
    fiscal_path = os.path.join(OUTPUT_DIR, "fiscal_year_summary.csv")
    fiscal_summary.to_csv(fiscal_path)

    print(f"Saved {len(df)} months to {out_path}")
    print(f"Saved fiscal-year summary to {fiscal_path}\n")

    x = np.arange(len(df))
    print("Linear trend, percentage points per month (full 53-month period):")
    for col in ["Securities_Top10", "Members_Top10", "Securities_Top100", "Members_Top100"]:
        slope = np.polyfit(x, df[col], 1)[0]
        print(f"  {col}: {slope:+.3f} pp/month "
              f"({slope * 12:+.2f} pp/year), std dev {df[col].std():.2f}")

    print(f"\nFirst month ({df['Month'].iloc[0]}) vs latest month ({df['Month'].iloc[-1]}):")
    for col in TOP_N_COLS_SEC + TOP_N_COLS_MEM:
        first, last = df[col].iloc[0], df[col].iloc[-1]
        print(f"  {col}: {first} -> {last} ({last - first:+d} pp)")

    print("\nFiscal-year averages:")
    print(fiscal_summary.to_string())


if __name__ == "__main__":
    main()
