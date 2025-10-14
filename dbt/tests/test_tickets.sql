-- Ensure tickets reference valid customers
select t.id
from {{ ref('tickets') }} t
left join {{ ref('customers') }} c on t.customer_id = c.id
where c.id is null
