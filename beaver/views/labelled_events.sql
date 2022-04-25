SELECT
    l.loop_id,
    l.created_at AS label_created_at,
    l.content AS label,
    e.content AS event
FROM labels l
LEFT JOIN events e ON l.loop_id = e.loop_id
