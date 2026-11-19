-- Q1. Employee headcount and attrition by department.
SELECT * FROM vw_department_attrition ORDER BY attrition_rate_pct DESC NULLS LAST;

-- Q2. Attrition by job role.
SELECT p.position_title,
       COUNT(*) AS employees,
       COUNT(*) FILTER (WHERE e.attrition='Yes') AS leavers,
       ROUND(100.0 * COUNT(*) FILTER (WHERE e.attrition='Yes') / COUNT(*),2) AS attrition_pct
FROM employees e JOIN positions p ON e.position_id=p.position_id
GROUP BY p.position_title ORDER BY attrition_pct DESC;

-- Q3. Compare attrition for employees working overtime.
SELECT overtime, COUNT(*) AS employee_count,
       COUNT(*) FILTER (WHERE attrition='Yes') AS leavers,
       ROUND(100.0*COUNT(*) FILTER (WHERE attrition='Yes')/COUNT(*),2) AS attrition_pct
FROM employees GROUP BY overtime;

-- Q4. Attrition by tenure band.
SELECT CASE WHEN years_at_company < 2 THEN '0-1 years'
            WHEN years_at_company < 5 THEN '2-4 years'
            WHEN years_at_company < 10 THEN '5-9 years'
            ELSE '10+ years' END AS tenure_band,
       COUNT(*) AS employee_count,
       COUNT(*) FILTER (WHERE attrition='Yes') AS leavers
FROM employees GROUP BY tenure_band ORDER BY MIN(years_at_company);

-- Q5. Hiring funnel counts from the simulated recruitment dataset.
SELECT current_stage, COUNT(*) AS applications
FROM applications GROUP BY current_stage
ORDER BY CASE current_stage WHEN 'Applied' THEN 1 WHEN 'Screening' THEN 2
 WHEN 'Interview' THEN 3 WHEN 'Offered' THEN 4 WHEN 'Hired' THEN 5 ELSE 6 END;

-- Q6. Interview pass rate by interview type.
SELECT interview_type, COUNT(*) AS interviews,
       COUNT(*) FILTER (WHERE interview_result='Pass') AS passed,
       ROUND(100.0*COUNT(*) FILTER (WHERE interview_result='Pass')/COUNT(*),2) AS pass_rate_pct
FROM interviews GROUP BY interview_type HAVING COUNT(*) >= 1;

-- Q7. Positions with more than 10 applications (JOIN + HAVING).
SELECT p.position_title, COUNT(a.application_id) AS application_count
FROM positions p JOIN applications a ON p.position_id=a.position_id
GROUP BY p.position_id, p.position_title
HAVING COUNT(a.application_id) > 10 ORDER BY application_count DESC;

-- Q8. Employees earning above their department average (subquery).
SELECT e.employee_id, d.department_name, e.monthly_income
FROM employees e JOIN departments d ON e.department_id=d.department_id
WHERE e.monthly_income > (
    SELECT AVG(e2.monthly_income) FROM employees e2
    WHERE e2.department_id=e.department_id
);

-- Q9. Average job satisfaction by attrition status.
SELECT attrition, ROUND(AVG(job_satisfaction),2) AS avg_job_satisfaction
FROM employees GROUP BY attrition;

-- Q10. Employee records with both low job satisfaction and overtime.
SELECT employee_id, age, monthly_income, years_at_company, overtime, attrition
FROM employees
WHERE job_satisfaction <= 2 AND overtime='Yes'
ORDER BY attrition DESC, years_at_company;
