-- Yearly deal count, total disclosed funding, and disclosure rate.
-- Rows with an unparseable date (8 of 3044) are excluded here since
-- they cannot be assigned to a year.
SELECT
  substr(date_clean, 1, 4) AS year,
  COUNT(*) AS deal_count,
  SUM(is_amount_disclosed) AS disclosed_deal_count,
  ROUND(SUM(is_amount_disclosed) * 100.0 / COUNT(*), 1) AS disclosure_rate_pct,
  ROUND(SUM(amount_usd)) AS total_disclosed_usd
FROM funding_clean
WHERE date_clean IS NOT NULL
GROUP BY year
ORDER BY year;
