"""
Runs sql/01_clean.sql against the database built by 01_load_raw.py,
producing the funding_clean table. Prints a short before/after summary.
"""

import sqlite3

from config import DB_PATH, SQL_DIR


def main():
    conn = sqlite3.connect(DB_PATH)
    with open(f"{SQL_DIR}/01_clean.sql") as f:
        conn.executescript(f.read())
    conn.commit()

    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM funding_clean")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM funding_clean WHERE is_date_valid = 0")
    bad_dates = cur.fetchone()[0]

    cur.execute("SELECT COUNT(DISTINCT city_primary_raw) FROM funding_clean")
    raw_cities = cur.fetchone()[0]
    cur.execute("SELECT COUNT(DISTINCT city) FROM funding_clean WHERE city IS NOT NULL")
    clean_cities = cur.fetchone()[0]

    cur.execute("SELECT COUNT(DISTINCT investment_type_primary) FROM funding_clean")
    raw_types = cur.fetchone()[0]
    cur.execute("SELECT COUNT(DISTINCT investment_type) FROM funding_clean WHERE investment_type IS NOT NULL")
    clean_types = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM funding_clean WHERE is_amount_disclosed = 0")
    undisclosed = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM funding_clean WHERE is_name_a_url = 1")
    url_names = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM funding_clean WHERE is_multi_location = 1")
    multi_loc = cur.fetchone()[0]

    print(f"funding_clean built: {total} rows\n")
    print(f"Unparseable dates (left NULL, not guessed): {bad_dates}")
    print(f"Distinct raw city spellings: {raw_cities} -> distinct clean cities: {clean_cities}")
    print(f"Distinct raw investment types: {raw_types} -> distinct clean types: {clean_types}")
    print(f"Rows with no disclosed amount: {undisclosed} ({undisclosed/total:.1%})")
    print(f"Rows where the startup 'name' is actually a URL: {url_names}")
    print(f"Rows with more than one location listed: {multi_loc}")

    conn.close()


if __name__ == "__main__":
    main()
