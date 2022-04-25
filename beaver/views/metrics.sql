SELECT
    AVG(ABS(CAST(label AS DECIMAL) - prediction)) AS mae
FROM labelled_predictions
GROUP BY model_name
