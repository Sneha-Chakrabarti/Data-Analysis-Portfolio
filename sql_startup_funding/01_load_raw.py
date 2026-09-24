"""
Loads the raw Indian Startup Funding CSV into a SQLite staging table,
`raw_funding`, with every column kept as TEXT and values left exactly as
they appear in the source file. All substantive cleaning happens in SQL
(sql/01_clean.sql), not here.

The one exception: the source file contains a literal encoding artifact
(the two-character sequence that should be a non-breaking space was
saved as the literal text "\\xc2\\xa0" in some cells, not an actual
non-breaking space character). That is a byte-level corruption from
however the file was originally exported, not a data-cleaning decision,
so it is fixed here before the text ever reaches SQL.
"""

import os
import sqlite3
import pandas as pd

from config import RAW_CSV, DB_PATH

# Two artifacts, both literal escaped text rather than real characters:
# a non-breaking space saved as "\xc2\xa0", and a line break saved as
# "\n" (two literal backslashes + n). Both are export corruption, not
# a cleaning decision, so both are fixed before the text reaches SQL.
ENCODING_ARTIFACTS = [
    ("\\" * 2) + "xc2" + ("\\" * 2) + "xa0",
    ("\\" * 2) + "n",
]

COLUMN_RENAME = {
    "Sr No": "sr_no",
    "Date dd/mm/yyyy": "date_raw",
    "Startup Name": "startup_name_raw",
    "Industry Vertical": "industry_vertical_raw",
    "SubVertical": "subvertical_raw",
    "City  Location": "city_raw",
    "Investors Name": "investors_name_raw",
    "InvestmentnType": "investment_type_raw",
    "Amount in USD": "amount_usd_raw",
    "Remarks": "remarks_raw",
}


def main():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    with open(RAW_CSV, "r", encoding="utf-8-sig") as f:
        text = f.read()
    n_artifacts = sum(text.count(a) for a in ENCODING_ARTIFACTS)
    for artifact in ENCODING_ARTIFACTS:
        text = text.replace(artifact, " ")

    from io import StringIO
    df = pd.read_csv(StringIO(text), keep_default_na=False, dtype=str)
    df.columns = [c.strip() for c in df.columns]
    df = df.rename(columns=COLUMN_RENAME)

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("raw_funding", conn, index=False)
    conn.close()

    print(f"Loaded {len(df)} rows into raw_funding at {DB_PATH}")
    print(f"Fixed {n_artifacts} instances of the literal encoding artifact")


if __name__ == "__main__":
    main()
