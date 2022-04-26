WITH RECURSIVE dates(tick) AS (
    -- HACK: dates shouldn't hardcoded
    VALUES(DATETIME('2022-04-25'))
    UNION ALL
    SELECT DATETIME(tick, '+1 minute')
    FROM dates
    WHERE tick < '2022-06-30'
),
since AS (SELECT MIN(created_at) AS since FROM labels),
until AS (SELECT DATETIME(MAX(created_at), '+1 minute') AS until FROM labels)

SELECT tick, DATETIME(tick, '-1 minute') AS prev_tick
FROM dates, since, until
WHERE dates.tick >= since.since
AND dates.tick <= until.until
