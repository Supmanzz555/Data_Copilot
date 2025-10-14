-- Ticket fact table with enriched dimensions
SELECT 
    t.id,
    t.customer_id,
    t.product_id,
    t.category,
    t.issue,
    t.status,
    t.created_at,
    c.name as customer_name,
    c.region as customer_region,
    p.name as product_name,
    p.category as product_category,
    EXTRACT(YEAR FROM t.created_at) as year,
    EXTRACT(MONTH FROM t.created_at) as month,
    EXTRACT(DAY FROM t.created_at) as day
FROM tickets t
LEFT JOIN customers c ON t.customer_id = c.id
LEFT JOIN products p ON t.product_id = p.id
