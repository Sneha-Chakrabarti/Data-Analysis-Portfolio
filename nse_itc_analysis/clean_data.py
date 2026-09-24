"""
Cleans the raw NSE security-wise price-volume export for ITC. NSE exports
use Indian numbering (lakh-style commas), pad column headers and string
fields with extra whitespace, list dates newest first, and use "-" for
missing delivery data on some days. Saves output/itc_cleaned.csv.
"""

import os
import pandas as pd

from config import RAW_FILE, CLEANED_FILE, OUTPUT_DIR

NUMERIC_COLS = [
    "Prev Close", "Open Price", "High Price", "Low Price", "Last Price",
    "Close Price", "Average Price", "Total Traded Quantity", "Turnover ₹",
    "No. of Trades", "Deliverable Qty", "% Dly Qt to Traded Qty",
]


def clean_indian_number(series: pd.Series) -> pd.Series:
    cleaned = series.astype(str).str.strip().replace("-", pd.NA)
    cleaned = cleaned.str.replace(",", "", regex=False)
    return pd.to_numeric(cleaned, errors="coerce")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df = pd.read_csv(RAW_FILE, encoding="utf-8-sig")
    df.columns = [c.strip() for c in df.columns]

    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.strip()

    for col in NUMERIC_COLS:
        df[col] = clean_indian_number(df[col])

    df["Date"] = pd.to_datetime(df["Date"], format="%d-%b-%Y")
    df = df.sort_values("Date").reset_index(drop=True)

    df.to_csv(CLEANED_FILE, index=False)
    n_missing_delivery = df["Deliverable Qty"].isna().sum()
    print(f"Cleaned {len(df)} rows, saved to {CLEANED_FILE}")
    print(f"Rows with missing delivery data: {n_missing_delivery}")
    print(df.head())


if __name__ == "__main__":
    main()
