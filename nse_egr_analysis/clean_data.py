"""
Cleans the raw NSE EGR historical data export. NSE exports use Indian
numbering (lakh-style commas, e.g. "1,58,982.00") for every numeric
column and list dates newest first, both of which need fixing before
any analysis. Saves output/egr_cleaned.csv.
"""

import os
import pandas as pd

from config import RAW_FILE, CLEANED_FILE, OUTPUT_DIR

NUMERIC_COLS = [
    "Prev Close", "Open Price", "High Price", "Low Price",
    "Last Price", "Close Price", "Total Traded Quantity",
    "Value", "No. Of Trades",
]


def clean_indian_number(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.replace(",", "", regex=False)
        .astype(float)
    )


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df = pd.read_csv(RAW_FILE, encoding="utf-8-sig")
    df.columns = [c.strip() for c in df.columns]

    for col in NUMERIC_COLS:
        df[col] = clean_indian_number(df[col])

    df["Date"] = pd.to_datetime(df["Date"], format="%d-%b-%Y")
    df = df.sort_values("Date").reset_index(drop=True)

    df.to_csv(CLEANED_FILE, index=False)
    print(f"Cleaned {len(df)} rows, saved to {CLEANED_FILE}")
    print(df.head())


if __name__ == "__main__":
    main()
