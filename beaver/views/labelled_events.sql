SELECT
    l.loop_id,
    l.content AS label,
    e.content AS event
FROM labels l
LEFT JOIN events e ON l.loop_id = e.loop_id
