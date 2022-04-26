SELECT
    tick,
    model_name,
    AVG(ABS(CAST(TRIM(label, '"') AS DECIMAL) - prediction)) AS mae,
    COUNT(*) AS n
FROM ticks t
CROSS JOIN labelled_predictions lp
WHERE lp.label_created_at < t.tick
AND lp.label_created_at >= t.prev_tick
GROUP BY tick, model_name
