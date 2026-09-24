"""
Cleans the raw NSE Most Active Securities monthly report: padded
headers, Indian-style numbering, and separates the 10 individual
securities from the two summary rows ("TOTAL of Top Ten Securities" and
"TOTAL"). Saves output/most_active_cleaned.csv (10 securities) and
output/market_totals.csv (the 2 summary rows).
"""

import os
import pandas as pd

from config import RAW_FILE, CLEANED_FILE, OUTPUT_DIR

NUMERIC_COLS = [
    "No. of Trades", "Traded Quantity (Lakh Shares)", "Turnover (₹ cr.)",
    "Average Daily Turnover (₹ cr.)", "Share in Total Turnover(%)",
]


def clean_indian_number(series: pd.Series) -> pd.Series:
    cleaned = series.astype(str).str.strip().str.replace(",", "", regex=False)
    return pd.to_numeric(cleaned, errors="coerce")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df = pd.read_csv(RAW_FILE, encoding="utf-8-sig")
    df.columns = [c.strip() for c in df.columns]
    df["Security"] = df["Security"].astype(str).str.strip()

    for col in NUMERIC_COLS:
        df[col] = clean_indian_number(df[col])

    is_summary = df["Security"].str.upper().str.startswith("TOTAL")
    securities = df[~is_summary].reset_index(drop=True)
    totals = df[is_summary].reset_index(drop=True)

    securities.to_csv(CLEANED_FILE, index=False)
    totals.to_csv(os.path.join(OUTPUT_DIR, "market_totals.csv"), index=False)

    print(f"Cleaned {len(securities)} securities, saved to {CLEANED_FILE}")
    print(f"Saved {len(totals)} summary rows to output/market_totals.csv")
    print(securities[["Security", "Turnover (₹ cr.)", "Share in Total Turnover(%)"]])


if __name__ == "__main__":
    main()
