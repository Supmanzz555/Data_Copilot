-- Login activity with customer details
SELECT 
    l.id,
    l.customer_id,
    l.last_login,
    l.login_count,
    c.name as customer_name,
    c.email as customer_email,
    c.region,
    CASE 
        WHEN l.last_login >= CURRENT_DATE - INTERVAL '30 days' THEN 'Active'
        WHEN l.last_login >= CURRENT_DATE - INTERVAL '90 days' THEN 'At Risk'
        ELSE 'Churned'
    END as activity_status
FROM logins l
LEFT JOIN customers c ON l.customer_id = c.id
