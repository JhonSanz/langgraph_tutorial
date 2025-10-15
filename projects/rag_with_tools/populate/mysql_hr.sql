-- MySQL Human Resources Database Setup
-- Database: human_resources_db
-- Description: Base de datos de recursos humanos con empleados y nómina

-- Drop tables if they exist (for clean re-runs)
DROP TABLE IF EXISTS payroll;
DROP TABLE IF EXISTS employees;

-- Create employees table
CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(50) NOT NULL,
    department VARCHAR(50),
    hire_date DATE,
    email VARCHAR(100),
    status ENUM('active', 'inactive', 'on_leave') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create payroll table
CREATE TABLE payroll (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    salary DECIMAL(10, 2) NOT NULL,
    bonus DECIMAL(10, 2) DEFAULT 0.00,
    deductions DECIMAL(10, 2) DEFAULT 0.00,
    payment_date DATE NOT NULL,
    payment_period VARCHAR(20),
    notes TEXT,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert sample employees
INSERT INTO employees (name, role, department, hire_date, email, status) VALUES
    ('Alice Johnson', 'Software Engineer', 'Engineering', '2022-01-15', 'alice.johnson@company.com', 'active'),
    ('Bob Smith', 'Product Manager', 'Product', '2021-06-20', 'bob.smith@company.com', 'active'),
    ('Carol Williams', 'Designer', 'Design', '2023-03-10', 'carol.williams@company.com', 'active'),
    ('David Brown', 'Senior Engineer', 'Engineering', '2020-08-05', 'david.brown@company.com', 'active'),
    ('Eva Martinez', 'HR Manager', 'Human Resources', '2021-11-12', 'eva.martinez@company.com', 'active'),
    ('Frank Garcia', 'Sales Representative', 'Sales', '2022-09-18', 'frank.garcia@company.com', 'active'),
    ('Grace Lee', 'Marketing Specialist', 'Marketing', '2023-01-25', 'grace.lee@company.com', 'active'),
    ('Henry Davis', 'DevOps Engineer', 'Engineering', '2021-04-30', 'henry.davis@company.com', 'active'),
    ('Iris Rodriguez', 'QA Engineer', 'Engineering', '2022-07-14', 'iris.rodriguez@company.com', 'on_leave'),
    ('Jack Wilson', 'Finance Analyst', 'Finance', '2020-12-01', 'jack.wilson@company.com', 'active');

-- Insert sample payroll records
-- January 2025 payroll
INSERT INTO payroll (employee_id, salary, bonus, deductions, payment_date, payment_period, notes) VALUES
    (1, 5500.00, 500.00, 350.00, '2025-01-31', 'January 2025', 'Regular monthly payment'),
    (2, 7000.00, 1000.00, 450.00, '2025-01-31', 'January 2025', 'Regular monthly payment + performance bonus'),
    (3, 4800.00, 0.00, 320.00, '2025-01-31', 'January 2025', 'Regular monthly payment'),
    (4, 8500.00, 1500.00, 550.00, '2025-01-31', 'January 2025', 'Regular monthly payment + senior bonus'),
    (5, 6500.00, 800.00, 420.00, '2025-01-31', 'January 2025', 'Regular monthly payment'),
    (6, 4500.00, 600.00, 300.00, '2025-01-31', 'January 2025', 'Regular monthly payment + sales commission'),
    (7, 5000.00, 0.00, 330.00, '2025-01-31', 'January 2025', 'Regular monthly payment'),
    (8, 7200.00, 700.00, 470.00, '2025-01-31', 'January 2025', 'Regular monthly payment'),
    (9, 5300.00, 0.00, 350.00, '2025-01-31', 'January 2025', 'Regular monthly payment'),
    (10, 6000.00, 500.00, 390.00, '2025-01-31', 'January 2025', 'Regular monthly payment');

-- February 2025 payroll
INSERT INTO payroll (employee_id, salary, bonus, deductions, payment_date, payment_period, notes) VALUES
    (1, 5500.00, 0.00, 350.00, '2025-02-28', 'February 2025', 'Regular monthly payment'),
    (2, 7000.00, 0.00, 450.00, '2025-02-28', 'February 2025', 'Regular monthly payment'),
    (3, 4800.00, 300.00, 320.00, '2025-02-28', 'February 2025', 'Regular monthly payment + project completion'),
    (4, 8500.00, 0.00, 550.00, '2025-02-28', 'February 2025', 'Regular monthly payment'),
    (5, 6500.00, 0.00, 420.00, '2025-02-28', 'February 2025', 'Regular monthly payment'),
    (6, 4500.00, 1200.00, 300.00, '2025-02-28', 'February 2025', 'Regular monthly payment + high sales commission'),
    (7, 5000.00, 400.00, 330.00, '2025-02-28', 'February 2025', 'Regular monthly payment + campaign success'),
    (8, 7200.00, 0.00, 470.00, '2025-02-28', 'February 2025', 'Regular monthly payment'),
    (9, 5300.00, 0.00, 350.00, '2025-02-28', 'February 2025', 'On leave - partial payment'),
    (10, 6000.00, 0.00, 390.00, '2025-02-28', 'February 2025', 'Regular monthly payment');

-- Create indexes for better query performance
CREATE INDEX idx_payroll_employee_id ON payroll(employee_id);
CREATE INDEX idx_payroll_payment_date ON payroll(payment_date);
CREATE INDEX idx_employees_department ON employees(department);
CREATE INDEX idx_employees_status ON employees(status);

-- Verify data
SELECT 'Employees count' as info, COUNT(*) as count FROM employees
UNION ALL
SELECT 'Payroll records count' as info, COUNT(*) as count FROM payroll;

COMMIT;
