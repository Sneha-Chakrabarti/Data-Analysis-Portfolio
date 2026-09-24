"""
Runs each analysis*.sql file in sql/ against funding_clean and saves
each result set to output/<query_name>.csv. Prints row counts so the
console output confirms every query returned something.
"""

import os
import sqlite3
import csv
import glob

from config import DB_PATH, SQL_DIR, OUTPUT_DIR


def run_query_file(conn, path):
    with open(path) as f:
        sql = f.read()
    cur = conn.execute(sql)
    columns = [d[0] for d in cur.description]
    rows = cur.fetchall()
    return columns, rows


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    query_files = sorted(glob.glob(f"{SQL_DIR}/*_analysis_*.sql"))
    for path in query_files:
        name = os.path.splitext(os.path.basename(path))[0]
        columns, rows = run_query_file(conn, path)

        out_path = os.path.join(OUTPUT_DIR, f"{name}.csv")
        with open(out_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            writer.writerows(rows)

        print(f"{name}: {len(rows)} rows -> {out_path}")

    conn.close()


if __name__ == "__main__":
    main()
