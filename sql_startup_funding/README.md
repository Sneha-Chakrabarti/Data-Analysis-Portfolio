# Indian Startup Funding (2015-2020): SQL Data Cleaning and Analysis

Cleans and analyzes a real, publicly available record of 3,044 Indian
startup funding deals using SQL as the primary tool, not just Python:
lookup-table-based standardization, a recursive CTE, and derived
analytical views, all written as plain SQL files and run against a
local SQLite database.

## What this project shows

- Real SQL, not just SELECT/WHERE: staging tables, lookup-table joins
  for value standardization, `CASE` expressions for parsing and
  validation, `NULLIF` chains for missing-value handling, and a
  recursive CTE to split multi-value text cells
- Treating cleaning as falsifiable: every standardization decision was
  checked against its own output, and two mistakes in my own first
  pass are disclosed below rather than hidden
- Distinguishing a genuine trend from a data-coverage artifact, and
  flagging a probable data-entry error instead of quietly excluding it

## Data source

A public GitHub mirror of the Kaggle "Indian Startup Funding" dataset
(originally compiled from trak.in), covering startup funding deals from
January 2015 to mid-2020:
https://github.com/ShowRounak/Indian-Startup-Analysis-Dashborad-Using-Streamlit/blob/main/startup_funding.csv.
Stored as-downloaded at `data/startup_funding_raw.csv`.

## Repository structure

```
sql-startup-funding/
  config.py                file paths
  01_load_raw.py             loads the raw CSV into SQLite, fixes 2 encoding artifacts
  02_clean.py                 runs sql/01_clean.sql, prints a cleaning summary
  03_run_analysis.py           runs every sql/*_analysis_*.sql file, exports CSVs
  visualize.py                  generates the figures below
  requirements.txt
  sql/
    01_clean.sql                lookup tables + funding_clean table
    02_analysis_yearly.sql
    03_analysis_industries.sql
    04_analysis_cities.sql
    05_analysis_investment_types.sql
    06_analysis_top_startups.sql
    07_analysis_top_investors.sql
    08_analysis_monthly_trend.sql
  data/startup_funding_raw.csv   raw source file
  output/                        SQLite database, query CSVs, figures
```

## Setup

```bash
git clone <your-repo-url>
cd sql-startup-funding
pip install -r requirements.txt
```

## Usage

```bash
python 01_load_raw.py      # data/startup_funding_raw.csv -> output/startup_funding.db (raw_funding table)
python 02_clean.py         # runs sql/01_clean.sql -> funding_clean table
python 03_run_analysis.py  # runs sql/*_analysis_*.sql -> output/*.csv
python visualize.py        # output/*.csv -> output/figures/*.png
```

Every step after loading is plain SQL executed from Python via the
standard library `sqlite3` module; the `.sql` files in `sql/` are
readable and runnable on their own against `output/startup_funding.db`
with any SQLite client.

## What was actually wrong with the raw data

- **Literal escape sequences saved as text, not real characters.**
  Some cells contain the literal 8-character text `\xc2\xa0` (should
  have been a non-breaking space) and others the literal 3-character
  text `\n` (should have been a line break). Both are almost certainly
  the result of a Python `str()` call leaking its own escape
  representation into a CSV export somewhere upstream. 192 instances
  fixed at ingestion, before either reaches SQL.
- **The literal text "nan" used as a missing-value marker** (not a
  true NULL) in 6 columns, 171 to 2,064 affected rows depending on the
  column, again consistent with a pandas `NaN` being stringified before
  export. Converted to real NULL in SQL via `NULLIF`.
- **113 raw city spellings** for what standardizes down to 68 real
  locations: misspellings (Ahemadabad, Ahemdabad), renamed/alternate
  spellings (Bangalore vs Bengaluru, Gurgaon vs Gurugram), and
  multi-location cells ("Bangalore / Palo Alto") needing the primary
  location extracted. Also country-level placeholders ("India", "US",
  "N/A") that are not cities at all, mapped to NULL rather than left
  looking like real locations.
- **53 raw funding-round labels for roughly 35 real categories**:
  case variants ("pre-series A" / "Pre-series A" / "Pre-Series A"),
  wording variants ("Seed Round" / "Seed Funding" / "Seed Funding
  Round"), a typo ("Seed / Angle Funding"), and the `\n`-artifact
  version of "Seed Funding" that only became mergeable once the
  encoding fix above ran first.
- **8 unparseable dates** (typos like `05/072018`, `12/05.2015`). Left
  NULL rather than guessed at.
- **The amount field mixes numbers with "undisclosed", "unknown",
  blank, and a trailing "+"** on some values, and uses Indian
  lakh-comma grouping throughout (e.g. `3,90,00,00,000`).
- **Investor cells list multiple co-investors in one string**
  ("Mumbai Angels, Ravikanth Reddy"), which would undercount individual
  investor activity if left unsplit.
- **No exact duplicate rows** were found (checked, not assumed).

## Two mistakes caught in my own cleaning, not just the source data

1. My first version of the city standardization used `COALESCE(lookup
   value, raw value)`. That silently undid the "India" / "US" / "N/A"
   to NULL mappings, because `COALESCE` falls back to the raw value
   whenever the lookup value is NULL, which is exactly what those
   mappings return. A row with no lookup match and a row correctly
   mapped to NULL looked identical to `COALESCE`. Fixed by checking
   whether a lookup row existed at all (`CASE WHEN lookup.key IS NOT
   NULL THEN lookup.value ELSE raw_value END`) rather than by the
   value it produced.
2. The industry field originally left `eCommerce` (186 rows),
   `ECommerce` (61), `E-Commerce` (29), `E-commerce` (12), `Ecommerce`
   (8) and `ecommerce` (3) as six separate categories, which fragmented
   what should have been the top industry across the top-10 chart.
   Caught by looking at the actual chart output, not just the query
   result. Fixed with a narrow, explicit rule (case/hyphen-insensitive
   exact match on "ecommerce" only, not a broad fuzzy merge of
   anything containing the word).

## Results

- **3,044 deals, 2015 to mid-2020.** Deal count peaks in 2016 (993
  deals) and falls sharply after: 687 in 2017, 309 in 2018, 111 in
  2019, 7 in a partial 2020. This is very likely incomplete data
  collection in later periods rather than a real 90 percent collapse
  in startup funding activity, visible directly in the monthly trend
  (a steady year-on-year decline, not a sudden drop at a specific
  policy or market event). Treated as a coverage caveat, not a finding
  about the market.
- **Amount-disclosure rate rose while deal count fell**: 69.8% of 2015
  deals disclosed an amount, versus 94.6% of 2019 deals. Combined with
  the point above, the later years in this dataset likely capture a
  smaller number of larger, better-documented deals rather than the
  full market.
- **Top industry by disclosed funding: E-Commerce, $8.26B** across 299
  deals (after merging the six spelling variants above), ahead of
  Consumer Internet ($6.25B, 941 deals) and Transportation ($3.92B,
  only 4 deals, see the flag below).
- **Top city: Bengaluru, $18.81B disclosed across 851 deals**, more
  than 3.5 times Mumbai in second place ($4.96B). Bengaluru's total
  includes the flagged Rapido outlier below; without it, Bengaluru
  would still lead but by a smaller margin.
- **Top individual investors by deal count**: Sequoia Capital (72),
  Accel Partners (69), Kalaari Capital (50), SAIF Partners (48), Blume
  Ventures (47), each counted once per deal via the comma-split, with
  "Undisclosed Investors" explicitly excluded as a placeholder rather
  than left in as though it were a single very active investor.
- **A likely data-entry error, disclosed rather than deleted**: Rapido
  Bike Taxi shows a single $3.9B round on 27 Aug 2019
  (`3,90,00,00,000` in the source). Real-world Rapido funding rounds
  in that period were reported in the tens of millions of dollars, not
  billions; this is almost certainly a stray digit group in the
  original data entry. The row is kept in `funding_clean` and included
  in every query as-is (an analyst does not get to unilaterally alter
  a source record without a documented reason), but it is called out
  here because it materially inflates both the Transportation industry
  total and Bengaluru's city total above.

See `output/figures/`:
1. `yearly_deals_disclosure.png`: deal count (bars) and disclosure
   rate (line) by year, 2015-2019
2. `top_industries.png`: top 10 industries by disclosed funding
3. `top_cities.png`: top 10 cities by disclosed funding
4. `monthly_trend.png`: monthly deal count, showing the gradual
   decline referenced above

## Limitations

- `industry_vertical` is free text with over 800 distinct raw values;
  only the exact-match e-commerce duplication was standardized. Many
  smaller categories almost certainly have their own unmerged spelling
  variants that were not large enough to distort a top-10 chart and so
  were not chased down individually.
- The investor comma-split does not handle cells that join the last
  two names with "and" instead of a comma (e.g. "Sabre Partners and
  Neoplux" stays joined). A regex-capable database (PostgreSQL, MySQL)
  could handle this more completely than SQLite's string functions.
- Startup name variants (e.g. "Flipkart" and "Flipkart.com" appear as
  separate rows in the top-startups query) were not merged; doing so
  reliably would need fuzzy matching rather than the exact-match
  approach used elsewhere in this project.

## Possible extensions

- Fuzzy-match startup name variants (Flipkart / Flipkart.com) using a
  string-similarity function
- Extend the investor split to handle "and"-joined lists with a proper
  regex-capable database
- Cross-reference the flagged Rapido figure and any other outliers
  against a second funding-data source to confirm or correct them

## License

MIT
