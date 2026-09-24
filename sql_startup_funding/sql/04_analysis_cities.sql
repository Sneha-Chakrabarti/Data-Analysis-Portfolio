-- Top 15 cities by total disclosed funding, using the standardized
-- city column (city_lookup applied, primary location extracted from
-- multi-location entries).
SELECT
  city,
  COUNT(*) AS deal_count,
  SUM(is_amount_disclosed) AS disclosed_deal_count,
  ROUND(SUM(amount_usd)) AS total_disclosed_usd
FROM funding_clean
WHERE city IS NOT NULL
GROUP BY city
ORDER BY total_disclosed_usd DESC
LIMIT 15;
