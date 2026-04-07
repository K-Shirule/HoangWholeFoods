use HoangWholeFoods;

-- view all stores with their manager
select 
    s.st_id,
    s.branch_name,
    s.location,
    e.first_name,
    e.last_name
from store s
left join employee e on s.manager_e_id = e.e_id;


-- view all employees with their store branch
select 
    e.e_id,
    e.first_name,
    e.last_name,
    e.role,
    s.branch_name,
    e.current
from employee e
join store s on e.st_id = s.st_id
order by s.st_id, e.role;


-- count employees per store by role
select 
    s.branch_name,
    e.role,
    count(*) as total
from employee e
join store s on e.st_id = s.st_id
group by s.branch_name, e.role
order by s.branch_name, e.role;


-- view only currently active employees
select 
    e.first_name,
    e.last_name,
    e.role,
    s.branch_name,
    e.start_date
from employee e
join store s on e.st_id = s.st_id
where e.current = true
order by s.st_id;


-- view terminated employees
select 
    e.first_name,
    e.last_name,
    e.role,
    s.branch_name,
    e.start_date,
    e.end_date
from employee e
join store s on e.st_id = s.st_id
where e.current = false;


-- headcount per store (active employees only)
select 
    s.branch_name,
    count(*) as active_employees
from employee e
join store s on e.st_id = s.st_id
where e.current = true
group by s.branch_name;


-- salary stats per store
select 
    s.branch_name,
    min(e.salary)           as min_salary,
    max(e.salary)           as max_salary,
    round(avg(e.salary), 2) as avg_salary,
    sum(e.salary)           as total_payroll
from employee e
join store s on e.st_id = s.st_id
where e.current = true
group by s.branch_name;