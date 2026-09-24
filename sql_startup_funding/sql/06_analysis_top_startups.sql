-- Top 20 startups by total disclosed funding, summed across every
-- round that startup appears with in the dataset (some startups have
-- multiple rows, one per funding round).
SELECT
  startup_name,
  COUNT(*) AS rounds_in_dataset,
  ROUND(SUM(amount_usd)) AS total_disclosed_usd
FROM funding_clean
WHERE amount_usd IS NOT NULL
GROUP BY startup_name
ORDER BY total_disclosed_usd DESC
LIMIT 20;
