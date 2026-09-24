-- Monthly deal count and disclosed funding total, for the trend chart.
SELECT
  substr(date_clean, 1, 7) AS year_month,
  COUNT(*) AS deal_count,
  ROUND(SUM(amount_usd)) AS total_disclosed_usd
FROM funding_clean
WHERE date_clean IS NOT NULL
GROUP BY year_month
ORDER BY year_month;
