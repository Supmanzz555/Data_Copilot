-- Customer dimension with activity metrics
SELECT 
    c.id,
    c.name,
    c.email,
    c.region,
    c.joined_date,
    l.last_login,
    l.login_count,
    COUNT(t.id) as total_tickets,
    SUM(CASE WHEN t.status = 'open' THEN 1 ELSE 0 END) as open_tickets
FROM customers c
LEFT JOIN logins l ON c.id = l.customer_id
LEFT JOIN tickets t ON c.id = t.customer_id
GROUP BY c.id, c.name, c.email, c.region, c.joined_date, l.last_login, l.login_count
