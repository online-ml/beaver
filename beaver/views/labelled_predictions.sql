SELECT
    l.loop_id,
    l.created_at AS label_created_at,
    l.content AS label,
    p.content AS prediction,
    p.model_name
FROM labels l
LEFT JOIN predictions p ON l.loop_id = p.loop_id
