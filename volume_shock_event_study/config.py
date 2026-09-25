DATA_DIR = "data"
RAW_DIR = f"{DATA_DIR}/raw"
OUTPUT_DIR = "output"

UNIVERSE = [
    "reliance", "tcs", "hdfcbank", "infy", "icicibank", "sbin", "itc",
    "hindunilvr", "bajfinance", "maruti", "axisbank", "kotakbank",
    "bhartiartl", "lt", "tatasteel", "ntpc", "ongc", "sunpharma",
    "titan", "asianpaint",
]

START_DATE = "2011-01-01"
END_DATE = "2026-09-18"
TRADING_DAYS = 252

# ---- Event definition ----
# A day is flagged as a volume-shock event for a stock if that day's
# volume exceeds this multiple of the trailing 60-day MEDIAN volume
# (median, not mean, since daily volume is right-skewed and a median
# is far less distorted by a handful of earlier shock days).
VOLUME_LOOKBACK = 60
VOLUME_SHOCK_MULTIPLE = 5

# Minimum trading days required between two events for the SAME stock,
# so that a multi-day volume spike is not double (or triple-, or
# quadruple-) counted as several independent events.
MIN_GAP_BETWEEN_EVENTS = 10

# Event window, in trading days relative to the event day (0 = the
# shock day itself).
PRE_WINDOW = 5
POST_WINDOW = 20

# A minimum number of trailing days of data required before a day can
# even be considered as a candidate event, so early-history days
# without a full 60-day baseline are never flagged.
MIN_HISTORY = VOLUME_LOOKBACK
