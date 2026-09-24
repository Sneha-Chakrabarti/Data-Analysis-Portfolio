DATA_DIR = "data"
OUTPUT_DIR = "output"
RAW_FILE = f"{DATA_DIR}/Bulk-Deals-08-09-2026-to-15-09-2026.csv"
CLEANED_FILE = f"{OUTPUT_DIR}/bulk_deals_cleaned.csv"

# A client's BUY and SELL in the same stock on the same day is classified
# as a "round trip" (market-making signature) if the smaller of the two
# quantities is at least this fraction of the larger. Below this
# threshold, or if only one side is present, it is "directional".
ROUND_TRIP_QTY_MATCH_THRESHOLD = 0.90
