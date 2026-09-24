"""
Cleans the raw NSE Bulk Deals export: padded headers, Indian-style
numbering in quantity and price columns, and a "-" placeholder in
Remarks. Saves output/bulk_deals_cleaned.csv.
"""

import os
import pandas as pd

from config import RAW_FILE, CLEANED_FILE, OUTPUT_DIR


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

    df["Quantity Traded"] = clean_indian_number(df["Quantity Traded"])
    df["Trade Price / Wght. Avg. Price"] = clean_indian_number(df["Trade Price / Wght. Avg. Price"])
    df["Value"] = df["Quantity Traded"] * df["Trade Price / Wght. Avg. Price"]

    df["Date"] = pd.to_datetime(df["Date"], format="%d-%b-%Y")
    df = df.sort_values(["Date", "Symbol", "Client Name"]).reset_index(drop=True)

    df.to_csv(CLEANED_FILE, index=False)
    print(f"Cleaned {len(df)} rows, saved to {CLEANED_FILE}")
    print(f"Date range: {df['Date'].min().date()} to {df['Date'].max().date()}")
    print(f"Unique symbols: {df['Symbol'].nunique()}, unique clients: {df['Client Name'].nunique()}")


if __name__ == "__main__":
    main()
