"""
Computes derived breadth metrics from the monthly advances/declines
counts: A/D ratio, net advances, a cumulative monthly Advance-Decline
Line, and a rolling 3-month average of the ratio to smooth month-to-month
noise. Saves output/breadth_monthly_analysis.csv.
"""

import os
import pandas as pd

from config import INPUT_FILE, OUTPUT_DIR, ROLLING_WINDOW


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df = pd.read_csv(INPUT_FILE, parse_dates=["Month"])
    df = df.sort_values("Month").reset_index(drop=True)

    df["Total"] = df["Advances"] + df["Declines"]
    df["AD_Ratio"] = df["Advances"] / df["Declines"]
    df["NetAdvances"] = df["Advances"] - df["Declines"]
    df["AD_Line_Monthly"] = df["NetAdvances"].cumsum()
    df["AD_Ratio_Rolling"] = df["AD_Ratio"].rolling(ROLLING_WINDOW).mean()

    # Classify each month as breadth-positive or breadth-negative
    df["BreadthPositive"] = df["AD_Ratio"] > 1.0

    out_path = os.path.join(OUTPUT_DIR, "breadth_monthly_analysis.csv")
    df.to_csv(out_path, index=False)

    n_positive = int(df["BreadthPositive"].sum())
    n_total = len(df)
    strongest = df.loc[df["AD_Ratio"].idxmax()]
    weakest = df.loc[df["AD_Ratio"].idxmin()]

    print(f"Saved {n_total} months to {out_path}")
    print(f"Breadth-positive months (AD ratio > 1): {n_positive}/{n_total}")
    print(f"Strongest breadth month: {strongest['Month'].strftime('%Y-%m')} "
          f"(AD ratio {strongest['AD_Ratio']:.2f})")
    print(f"Weakest breadth month: {weakest['Month'].strftime('%Y-%m')} "
          f"(AD ratio {weakest['AD_Ratio']:.2f})")


if __name__ == "__main__":
    main()
