-- ============================================================
-- 01_clean.sql
-- Cleans raw_funding into a single analysis-ready table,
-- funding_clean, plus two lookup tables used to standardize
-- city and funding-round spellings.
-- ============================================================

-- ---------- City name lookup ----------
-- The raw city field has 113 distinct values for what is really
-- far fewer real locations: misspellings (Ahemadabad, Ahemdabad),
-- alternate/renamed spellings (Bangalore vs Bengaluru, Gurgaon vs
-- Gurugram), an encoding-artifact leftover space, and country-level
-- placeholders (India, US, USA, N/A) that are not cities at all.
DROP TABLE IF EXISTS city_lookup;
CREATE TABLE city_lookup (
  raw_city   TEXT PRIMARY KEY,
  clean_city TEXT  -- NULL means "not a real city" (country name, N/A, etc.)
);

INSERT INTO city_lookup (raw_city, clean_city) VALUES
  ('Ahemadabad', 'Ahmedabad'),
  ('Ahemdabad', 'Ahmedabad'),
  ('Bangalore', 'Bengaluru'),
  ('Bhubneswar', 'Bhubaneswar'),
  ('Gurgaon', 'Gurugram'),
  ('Kolkatta', 'Kolkata'),
  ('Kormangala', 'Bengaluru'),
  ('Nw Delhi', 'New Delhi'),
  ('New Delhi, Bengaluru', 'New Delhi'),
  ('N/A', NULL),
  ('India', NULL),
  ('US', NULL),
  ('USA', NULL);

-- ---------- Funding-round / investment-type lookup ----------
-- Same idea for InvestmentnType: "Seed", "Seed Round", "Seed Funding"
-- and "Seed Funding Round" are the same thing described four ways;
-- "pre-series A", "Pre-series A" and "Pre-Series A" are the same
-- round with three different capitalizations.
DROP TABLE IF EXISTS investment_type_lookup;
CREATE TABLE investment_type_lookup (
  raw_type   TEXT PRIMARY KEY,
  clean_type TEXT
);

INSERT INTO investment_type_lookup (raw_type, clean_type) VALUES
  ('Seed Round', 'Seed'),
  ('Seed Funding', 'Seed'),
  ('Seed Funding Round', 'Seed'),
  ('Seed funding', 'Seed'),
  ('Angel Round', 'Angel'),
  ('Angel Funding', 'Angel'),
  ('pre-series A', 'Pre-Series A'),
  ('Pre-series A', 'Pre-Series A'),
  ('pre-Series A', 'Pre-Series A'),
  ('Private Equity Round', 'Private Equity'),
  ('Venture Round', 'Venture'),
  ('Venture - Series Unknown', 'Venture'),
  ('Single Venture', 'Venture'),
  ('Corporate Round', 'Corporate'),
  ('Maiden Round', 'Unspecified'),
  ('Funding Round', 'Unspecified'),
  ('Bridge Round', 'Bridge'),
  -- Combined seed+angel rounds: several spacing/slash variants plus
  -- one "Angle" typo, all collapsed to one canonical label.
  ('Seed/ Angel Funding', 'Seed / Angel Funding'),
  ('Seed / Angel Funding', 'Seed / Angel Funding'),
  ('Seed/Angel Funding', 'Seed / Angel Funding'),
  ('Angel / Seed Funding', 'Seed / Angel Funding'),
  ('Seed / Angle Funding', 'Seed / Angel Funding');

-- ---------- Cleaned, analysis-ready table ----------
DROP TABLE IF EXISTS funding_clean;
CREATE TABLE funding_clean AS
WITH base AS (
  SELECT
    sr_no,

    -- ----- Date -----
    -- Keep only dates that match a genuine DD/MM/YYYY pattern (10
    -- characters, slashes in the right places, both slash-separated
    -- parts numeric-looking). 8 of 3044 rows fail this (typos like
    -- "05/072018" or "12/05.2015") and are left NULL rather than
    -- guessed at.
    CASE
      WHEN length(date_raw) = 10
        AND substr(date_raw, 3, 1) = '/'
        AND substr(date_raw, 6, 1) = '/'
      THEN substr(date_raw, 7, 4) || '-' || substr(date_raw, 4, 2) || '-' || substr(date_raw, 1, 2)
      ELSE NULL
    END AS date_clean,
    date_raw,

    -- ----- Startup name -----
    -- Fix the curly apostrophe (U+2019) to a plain one for consistent
    -- grouping; flag rows where the "name" is actually a URL, since
    -- that is a genuine data-entry problem worth surfacing rather
    -- than silently keeping or fixing.
    trim(replace(startup_name_raw, char(8217), '''')) AS startup_name,
    CASE WHEN lower(trim(startup_name_raw)) LIKE 'http%' THEN 1 ELSE 0 END AS is_name_a_url,

    -- ----- Categorical text fields -----
    -- The source leaks the literal text "nan" for missing values in
    -- several columns (171 to 2064 rows depending on column); treat
    -- that, and blank strings, as NULL. industry_vertical is free
    -- text with 800+ distinct raw values, too many to build a full
    -- lookup table for, but the exact-match case/hyphen duplicates of
    -- "e-commerce" alone were large enough to distort a top-10 chart
    -- (186 + 61 + 29 + 12 + 8 + 3 rows spread across six spellings of
    -- the same word), so that one case is normalized explicitly.
    -- Broader industry-text standardization is out of scope here; see
    -- the README limitations section.
    CASE
      WHEN lower(replace(replace(trim(industry_vertical_raw), '-', ''), ' ', '')) = 'ecommerce'
      THEN 'E-Commerce'
      ELSE NULLIF(NULLIF(trim(industry_vertical_raw), ''), 'nan')
    END AS industry_vertical,
    NULLIF(NULLIF(trim(subvertical_raw), ''), 'nan') AS subvertical,
    NULLIF(NULLIF(trim(investors_name_raw), ''), 'nan') AS investors_name,
    NULLIF(NULLIF(trim(remarks_raw), ''), 'nan') AS remarks,

    -- ----- City -----
    -- First treat the source's literal "nan"/blank placeholders as
    -- true missing, same as the other text columns, then take the
    -- text before the first separator ('/', '&', or ',') as the
    -- primary location; flag rows that named more than one location.
    trim(
      substr(
        NULLIF(NULLIF(trim(city_raw), ''), 'nan'), 1,
        CASE
          WHEN instr(city_raw, '/') > 0 OR instr(city_raw, '&') > 0 OR instr(city_raw, ',') > 0
          THEN min(
            CASE WHEN instr(city_raw, '/') > 0 THEN instr(city_raw, '/') ELSE length(city_raw) + 1 END,
            CASE WHEN instr(city_raw, '&') > 0 THEN instr(city_raw, '&') ELSE length(city_raw) + 1 END,
            CASE WHEN instr(city_raw, ',') > 0 THEN instr(city_raw, ',') ELSE length(city_raw) + 1 END
          ) - 1
          ELSE length(city_raw)
        END
      )
    ) AS city_primary_raw,
    CASE WHEN instr(city_raw, '/') > 0 OR instr(city_raw, '&') > 0 OR instr(city_raw, ',') > 0
         THEN 1 ELSE 0 END AS is_multi_location,

    -- ----- Investment type -----
    NULLIF(NULLIF(trim(investment_type_raw), ''), 'nan') AS investment_type_primary,

    -- ----- Amount -----
    -- "undisclosed", "unknown", blank and NULL all mean the same
    -- thing here (amount not disclosed); everything else is a
    -- lakh-comma-formatted or plain number, sometimes with a
    -- trailing "+". Strip commas and the trailing "+", then cast.
    CASE
      WHEN amount_usd_raw IS NULL THEN NULL
      WHEN lower(trim(amount_usd_raw)) IN ('', 'nan', 'undisclosed', 'unknown', 'n/a') THEN NULL
      ELSE CAST(
        REPLACE(REPLACE(REPLACE(trim(amount_usd_raw), ',', ''), '+', ''), ' ', '')
        AS REAL
      )
    END AS amount_usd

  FROM raw_funding
)
SELECT
  b.sr_no,
  b.date_clean,
  b.date_raw,
  CASE WHEN b.date_clean IS NULL THEN 0 ELSE 1 END AS is_date_valid,
  b.startup_name,
  b.is_name_a_url,
  b.industry_vertical,
  b.subvertical,
  b.city_primary_raw,
  CASE WHEN cl.raw_city IS NOT NULL THEN cl.clean_city ELSE b.city_primary_raw END AS city,
  b.is_multi_location,
  b.investors_name,
  b.investment_type_primary,
  CASE WHEN itl.raw_type IS NOT NULL THEN itl.clean_type ELSE b.investment_type_primary END AS investment_type,
  b.amount_usd,
  CASE WHEN b.amount_usd IS NULL THEN 0 ELSE 1 END AS is_amount_disclosed,
  b.remarks
FROM base b
LEFT JOIN city_lookup cl ON cl.raw_city = b.city_primary_raw
LEFT JOIN investment_type_lookup itl ON itl.raw_type = b.investment_type_primary;
