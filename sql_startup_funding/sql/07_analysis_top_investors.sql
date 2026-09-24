-- Investor cells often list several co-investors in one string, e.g.
-- "Mumbai Angels, Ravikanth Reddy". This recursive CTE splits each
-- cell on commas so each investor is counted once per deal they
-- participated in, rather than the combined string being treated as
-- one investor. Limitation: a few cells use "X and Y" instead of a
-- comma before the last name (e.g. "Sabre Partners and Neoplux");
-- those two remain joined as one token, since a comma-only split
-- cannot separate them. Left as-is rather than guessed at with a
-- fragile string match on "and", which would incorrectly split any
-- investor whose own name contains that word.
--
-- "Undisclosed" / "Undisclosed Investors" (in a few different
-- capitalizations) is a placeholder meaning no investor was named,
-- not a real investor, and is excluded from this ranking rather than
-- counted as though it were a single very active investor.
WITH RECURSIVE split(sr_no, investor, rest) AS (
  SELECT
    sr_no,
    '',
    investors_name || ','
  FROM funding_clean
  WHERE investors_name IS NOT NULL

  UNION ALL

  SELECT
    sr_no,
    trim(substr(rest, 1, instr(rest, ',') - 1)),
    substr(rest, instr(rest, ',') + 1)
  FROM split
  WHERE rest <> ''
)
SELECT
  investor,
  COUNT(*) AS deal_count
FROM split
WHERE investor <> ''
  AND lower(investor) NOT IN ('undisclosed', 'undisclosed investors')
GROUP BY investor
ORDER BY deal_count DESC
LIMIT 20;
