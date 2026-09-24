-- Deal count by standardized funding-round type, top 15.
SELECT
  investment_type,
  COUNT(*) AS deal_count,
  ROUND(SUM(amount_usd)) AS total_disclosed_usd
FROM funding_clean
WHERE investment_type IS NOT NULL
GROUP BY investment_type
ORDER BY deal_count DESC
LIMIT 15;
