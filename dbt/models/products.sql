-- Product dimension with ticket metrics
SELECT 
    p.id,
    p.name,
    p.category,
    COUNT(t.id) as total_tickets,
    SUM(CASE WHEN t.status = 'open' THEN 1 ELSE 0 END) as open_tickets,
    SUM(CASE WHEN t.status = 'closed' THEN 1 ELSE 0 END) as closed_tickets
FROM products p
LEFT JOIN tickets t ON p.id = t.product_id
GROUP BY p.id, p.name, p.category
