"""
Computes derived metrics from the cleaned data: average trade size,
implied average traded price per share (used as a sanity check against
known price levels), and market concentration among the top 10. Saves
output/most_active_analysis.csv and prints a summary.
"""

import os
import pandas as pd

from config import CLEANED_FILE, OUTPUT_DIR


def main():
    df = pd.read_csv(CLEANED_FILE)
    totals = pd.read_csv(os.path.join(OUTPUT_DIR, "market_totals.csv"))

    # Turnover is in Rs crore; convert to Rs for per-trade / per-share math.
    turnover_rs = df["Turnover (₹ cr.)"] * 1e7
    traded_qty_shares = df["Traded Quantity (Lakh Shares)"] * 1e5

    df["AvgTradeSizeRs"] = turnover_rs / df["No. of Trades"]
    df["ImpliedAvgPriceRs"] = turnover_rs / traded_qty_shares

    df = df.sort_values("Turnover (₹ cr.)", ascending=False).reset_index(drop=True)

    out_path = os.path.join(OUTPUT_DIR, "most_active_analysis.csv")
    df.to_csv(out_path, index=False)

    top_ten_row = totals[totals["Security"].str.contains("Top Ten", case=False)]
    market_total_row = totals[totals["Security"].str.upper() == "TOTAL"]

    top_ten_turnover = top_ten_row["Turnover (₹ cr.)"].iloc[0]
    market_turnover = market_total_row["Turnover (₹ cr.)"].iloc[0]
    top_ten_share = top_ten_row["Share in Total Turnover(%)"].iloc[0]

    top_ten_trades = top_ten_row["No. of Trades"].iloc[0]
    market_trades = market_total_row["No. of Trades"].iloc[0]

    print(f"Saved {len(df)} securities to {out_path}\n")
    print(f"Month: August 2026")
    print(f"Top 10 securities' turnover: Rs {top_ten_turnover:,.0f} crore "
          f"({top_ten_share:.2f}% of NSE-wide turnover of Rs {market_turnover:,.0f} crore)")
    print(f"Top 10 securities' trade count: {top_ten_trades:,.0f} "
          f"({top_ten_trades / market_trades:.2%} of {market_trades:,.0f} total trades)")
    print(f"\nAverage trade size across all NSE trades that month: "
          f"Rs {(market_turnover * 1e7 / market_trades):,.0f}")
    print(f"Average trade size across the top 10 alone: "
          f"Rs {(top_ten_turnover * 1e7 / top_ten_trades):,.0f}")
    print("\nPer-security detail:")
    print(df[["Security", "Turnover (₹ cr.)", "AvgTradeSizeRs", "ImpliedAvgPriceRs"]]
          .to_string(index=False, float_format=lambda x: f"{x:,.2f}"))


if __name__ == "__main__":
    main()
