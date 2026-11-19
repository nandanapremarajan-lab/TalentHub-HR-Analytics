-- TalentHub relational schema (PostgreSQL), designed to 3NF.
DROP VIEW IF EXISTS vw_department_attrition;
DROP TABLE IF EXISTS application_stage_log, exits, employees, interviews, applications, candidates, positions, departments CASCADE;

CREATE TABLE departments (
    department_id SERIAL PRIMARY KEY,
    department_name VARCHAR(80) NOT NULL UNIQUE
);

CREATE TABLE positions (
    position_id SERIAL PRIMARY KEY,
    department_id INT NOT NULL REFERENCES departments(department_id),
    position_title VARCHAR(100) NOT NULL,
    job_level INT CHECK (job_level BETWEEN 1 AND 5),
    UNIQUE(department_id, position_title)
);

CREATE TABLE candidates (
    candidate_id INT PRIMARY KEY,
    candidate_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    highest_education VARCHAR(80),
    experience_years INT CHECK (experience_years >= 0),
    source_channel VARCHAR(50) NOT NULL
);

CREATE TABLE applications (
    application_id INT PRIMARY KEY,
    candidate_id INT NOT NULL REFERENCES candidates(candidate_id),
    position_id INT NOT NULL REFERENCES positions(position_id),
    application_date DATE NOT NULL,
    current_stage VARCHAR(30) NOT NULL
      CHECK (current_stage IN ('Applied','Screening','Interview','Offered','Hired','Rejected')),
    stage_updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE interviews (
    interview_id INT PRIMARY KEY,
    application_id INT NOT NULL REFERENCES applications(application_id),
    interview_round INT NOT NULL CHECK (interview_round >= 1),
    interview_type VARCHAR(30) NOT NULL,
    interview_result VARCHAR(20) NOT NULL CHECK (interview_result IN ('Pass','Fail','Pending')),
    interview_date DATE NOT NULL
);

CREATE TABLE employees (
    employee_id INT PRIMARY KEY,
    department_id INT NOT NULL REFERENCES departments(department_id),
    position_id INT NOT NULL REFERENCES positions(position_id),
    age INT CHECK (age BETWEEN 18 AND 70),
    gender VARCHAR(20),
    monthly_income NUMERIC(12,2) CHECK (monthly_income >= 0),
    job_satisfaction INT CHECK (job_satisfaction BETWEEN 1 AND 4),
    environment_satisfaction INT CHECK (environment_satisfaction BETWEEN 1 AND 4),
    overtime VARCHAR(3) CHECK (overtime IN ('Yes','No')),
    years_at_company INT CHECK (years_at_company >= 0),
    total_working_years INT CHECK (total_working_years >= 0),
    attrition VARCHAR(3) NOT NULL CHECK (attrition IN ('Yes','No'))
);

CREATE TABLE exits (
    exit_id SERIAL PRIMARY KEY,
    employee_id INT NOT NULL UNIQUE REFERENCES employees(employee_id),
    exit_type VARCHAR(30) NOT NULL,
    source_label VARCHAR(40) NOT NULL DEFAULT 'Kaggle Attrition label'
);

CREATE TABLE application_stage_log (
    log_id BIGSERIAL PRIMARY KEY,
    application_id INT NOT NULL REFERENCES applications(application_id),
    old_stage VARCHAR(30),
    new_stage VARCHAR(30) NOT NULL,
    changed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Trigger: records every change to application stage.
CREATE OR REPLACE FUNCTION log_application_stage_change()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.current_stage IS DISTINCT FROM NEW.current_stage THEN
        INSERT INTO application_stage_log(application_id, old_stage, new_stage)
        VALUES (OLD.application_id, OLD.current_stage, NEW.current_stage);
        NEW.stage_updated_at = CURRENT_TIMESTAMP;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_application_stage_change
BEFORE UPDATE OF current_stage ON applications
FOR EACH ROW EXECUTE FUNCTION log_application_stage_change();

-- View: department-wise employee count and attrition rate.
CREATE VIEW vw_department_attrition AS
SELECT d.department_name,
       COUNT(e.employee_id) AS employee_count,
       COUNT(*) FILTER (WHERE e.attrition = 'Yes') AS attrition_count,
       ROUND(100.0 * COUNT(*) FILTER (WHERE e.attrition = 'Yes')
             / NULLIF(COUNT(e.employee_id),0), 2) AS attrition_rate_pct
FROM departments d
LEFT JOIN employees e ON e.department_id = d.department_id
GROUP BY d.department_id, d.department_name;
