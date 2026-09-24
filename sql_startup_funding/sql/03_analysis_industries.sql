-- Top 15 industry verticals by total disclosed funding.
SELECT
  industry_vertical,
  COUNT(*) AS deal_count,
  SUM(is_amount_disclosed) AS disclosed_deal_count,
  ROUND(SUM(amount_usd)) AS total_disclosed_usd
FROM funding_clean
WHERE industry_vertical IS NOT NULL
GROUP BY industry_vertical
ORDER BY total_disclosed_usd DESC
LIMIT 15;
