#!/usr/bin/env python3
"""
MySQL Human Resources Database Setup
Database: human_resources_db
Description: Base de datos de recursos humanos con empleados y nómina
"""

from sqlalchemy import create_engine, Column, Integer, String, Numeric, Date, DateTime, ForeignKey, Index, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import date, datetime

# MySQL connection details (from datasources.yaml)
MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_DATABASE = "mydatabase"
MYSQL_USER = "myuser"
MYSQL_PASSWORD = "mypassword"

Base = declarative_base()

# Define models
class Employee(Base):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    role = Column(String(50), nullable=False)
    department = Column(String(50))
    hire_date = Column(Date)
    email = Column(String(100))
    status = Column(Enum('active', 'inactive', 'on_leave'), default='active')
    created_at = Column(DateTime, default=datetime.now)

    payroll_records = relationship("Payroll", back_populates="employee")

    __table_args__ = (
        Index('idx_employees_department', 'department'),
        Index('idx_employees_status', 'status'),
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}
    )


class Payroll(Base):
    __tablename__ = 'payroll'

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey('employees.id', ondelete='CASCADE'), nullable=False)
    salary = Column(Numeric(10, 2), nullable=False)
    bonus = Column(Numeric(10, 2), default=0.00)
    deductions = Column(Numeric(10, 2), default=0.00)
    payment_date = Column(Date, nullable=False)
    payment_period = Column(String(20))
    notes = Column(Text)

    employee = relationship("Employee", back_populates="payroll_records")

    __table_args__ = (
        Index('idx_payroll_employee_id', 'employee_id'),
        Index('idx_payroll_payment_date', 'payment_date'),
        {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8mb4'}
    )


# Sample employees data
EMPLOYEES_DATA = [
    {'name': 'Alice Johnson', 'role': 'Software Engineer', 'department': 'Engineering', 'hire_date': date(2022, 1, 15), 'email': 'alice.johnson@company.com', 'status': 'active'},
    {'name': 'Bob Smith', 'role': 'Product Manager', 'department': 'Product', 'hire_date': date(2021, 6, 20), 'email': 'bob.smith@company.com', 'status': 'active'},
    {'name': 'Carol Williams', 'role': 'Designer', 'department': 'Design', 'hire_date': date(2023, 3, 10), 'email': 'carol.williams@company.com', 'status': 'active'},
    {'name': 'David Brown', 'role': 'Senior Engineer', 'department': 'Engineering', 'hire_date': date(2020, 8, 5), 'email': 'david.brown@company.com', 'status': 'active'},
    {'name': 'Eva Martinez', 'role': 'HR Manager', 'department': 'Human Resources', 'hire_date': date(2021, 11, 12), 'email': 'eva.martinez@company.com', 'status': 'active'},
    {'name': 'Frank Garcia', 'role': 'Sales Representative', 'department': 'Sales', 'hire_date': date(2022, 9, 18), 'email': 'frank.garcia@company.com', 'status': 'active'},
    {'name': 'Grace Lee', 'role': 'Marketing Specialist', 'department': 'Marketing', 'hire_date': date(2023, 1, 25), 'email': 'grace.lee@company.com', 'status': 'active'},
    {'name': 'Henry Davis', 'role': 'DevOps Engineer', 'department': 'Engineering', 'hire_date': date(2021, 4, 30), 'email': 'henry.davis@company.com', 'status': 'active'},
    {'name': 'Iris Rodriguez', 'role': 'QA Engineer', 'department': 'Engineering', 'hire_date': date(2022, 7, 14), 'email': 'iris.rodriguez@company.com', 'status': 'on_leave'},
    {'name': 'Jack Wilson', 'role': 'Finance Analyst', 'department': 'Finance', 'hire_date': date(2020, 12, 1), 'email': 'jack.wilson@company.com', 'status': 'active'},
]

# Sample payroll data
PAYROLL_DATA = [
    # January 2025
    {'employee_id': 1, 'salary': 5500.00, 'bonus': 500.00, 'deductions': 350.00, 'payment_date': date(2025, 1, 31), 'payment_period': 'January 2025', 'notes': 'Regular monthly payment'},
    {'employee_id': 2, 'salary': 7000.00, 'bonus': 1000.00, 'deductions': 450.00, 'payment_date': date(2025, 1, 31), 'payment_period': 'January 2025', 'notes': 'Regular monthly payment + performance bonus'},
    {'employee_id': 3, 'salary': 4800.00, 'bonus': 0.00, 'deductions': 320.00, 'payment_date': date(2025, 1, 31), 'payment_period': 'January 2025', 'notes': 'Regular monthly payment'},
    {'employee_id': 4, 'salary': 8500.00, 'bonus': 1500.00, 'deductions': 550.00, 'payment_date': date(2025, 1, 31), 'payment_period': 'January 2025', 'notes': 'Regular monthly payment + senior bonus'},
    {'employee_id': 5, 'salary': 6500.00, 'bonus': 800.00, 'deductions': 420.00, 'payment_date': date(2025, 1, 31), 'payment_period': 'January 2025', 'notes': 'Regular monthly payment'},
    {'employee_id': 6, 'salary': 4500.00, 'bonus': 600.00, 'deductions': 300.00, 'payment_date': date(2025, 1, 31), 'payment_period': 'January 2025', 'notes': 'Regular monthly payment + sales commission'},
    {'employee_id': 7, 'salary': 5000.00, 'bonus': 0.00, 'deductions': 330.00, 'payment_date': date(2025, 1, 31), 'payment_period': 'January 2025', 'notes': 'Regular monthly payment'},
    {'employee_id': 8, 'salary': 7200.00, 'bonus': 700.00, 'deductions': 470.00, 'payment_date': date(2025, 1, 31), 'payment_period': 'January 2025', 'notes': 'Regular monthly payment'},
    {'employee_id': 9, 'salary': 5300.00, 'bonus': 0.00, 'deductions': 350.00, 'payment_date': date(2025, 1, 31), 'payment_period': 'January 2025', 'notes': 'Regular monthly payment'},
    {'employee_id': 10, 'salary': 6000.00, 'bonus': 500.00, 'deductions': 390.00, 'payment_date': date(2025, 1, 31), 'payment_period': 'January 2025', 'notes': 'Regular monthly payment'},
    # February 2025
    {'employee_id': 1, 'salary': 5500.00, 'bonus': 0.00, 'deductions': 350.00, 'payment_date': date(2025, 2, 28), 'payment_period': 'February 2025', 'notes': 'Regular monthly payment'},
    {'employee_id': 2, 'salary': 7000.00, 'bonus': 0.00, 'deductions': 450.00, 'payment_date': date(2025, 2, 28), 'payment_period': 'February 2025', 'notes': 'Regular monthly payment'},
    {'employee_id': 3, 'salary': 4800.00, 'bonus': 300.00, 'deductions': 320.00, 'payment_date': date(2025, 2, 28), 'payment_period': 'February 2025', 'notes': 'Regular monthly payment + project completion'},
    {'employee_id': 4, 'salary': 8500.00, 'bonus': 0.00, 'deductions': 550.00, 'payment_date': date(2025, 2, 28), 'payment_period': 'February 2025', 'notes': 'Regular monthly payment'},
    {'employee_id': 5, 'salary': 6500.00, 'bonus': 0.00, 'deductions': 420.00, 'payment_date': date(2025, 2, 28), 'payment_period': 'February 2025', 'notes': 'Regular monthly payment'},
    {'employee_id': 6, 'salary': 4500.00, 'bonus': 1200.00, 'deductions': 300.00, 'payment_date': date(2025, 2, 28), 'payment_period': 'February 2025', 'notes': 'Regular monthly payment + high sales commission'},
    {'employee_id': 7, 'salary': 5000.00, 'bonus': 400.00, 'deductions': 330.00, 'payment_date': date(2025, 2, 28), 'payment_period': 'February 2025', 'notes': 'Regular monthly payment + campaign success'},
    {'employee_id': 8, 'salary': 7200.00, 'bonus': 0.00, 'deductions': 470.00, 'payment_date': date(2025, 2, 28), 'payment_period': 'February 2025', 'notes': 'Regular monthly payment'},
    {'employee_id': 9, 'salary': 5300.00, 'bonus': 0.00, 'deductions': 350.00, 'payment_date': date(2025, 2, 28), 'payment_period': 'February 2025', 'notes': 'On leave - partial payment'},
    {'employee_id': 10, 'salary': 6000.00, 'bonus': 0.00, 'deductions': 390.00, 'payment_date': date(2025, 2, 28), 'payment_period': 'February 2025', 'notes': 'Regular monthly payment'},
]


def main():
    """Main function to populate MySQL"""
    print("=" * 60)
    print("MySQL Human Resources Database Setup")
    print("=" * 60)

    engine = None
    Session = None
    session = None

    try:
        # Create engine and connect to MySQL
        print(f"\nConnecting to MySQL at {MYSQL_HOST}:{MYSQL_PORT}...")
        connection_string = f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
        engine = create_engine(connection_string)
        print("✓ Connected successfully")

        # Drop and create all tables
        print("\nDropping existing tables if they exist...")
        Base.metadata.drop_all(engine)
        print("✓ Tables dropped")

        print("\nCreating tables...")
        Base.metadata.create_all(engine)
        print("✓ Tables created successfully")

        # Create session
        Session = sessionmaker(bind=engine)
        session = Session()

        # Insert sample employees
        print("\nInserting sample employees...")
        employees = [Employee(**data) for data in EMPLOYEES_DATA]
        session.add_all(employees)
        session.flush()  # Flush to get IDs
        print(f"✓ Inserted {len(employees)} employees")

        # Insert sample payroll
        print("Inserting sample payroll records...")
        payroll_records = [Payroll(**data) for data in PAYROLL_DATA]
        session.add_all(payroll_records)
        print(f"✓ Inserted {len(payroll_records)} payroll records")

        # Commit all changes
        session.commit()

        # Verify data
        print("\n" + "=" * 60)
        print("Data Verification")
        print("=" * 60)

        employees_count = session.query(Employee).count()
        print(f"Employees count: {employees_count}")

        payroll_count = session.query(Payroll).count()
        print(f"Payroll records count: {payroll_count}")

        # Show sample data
        print("\nSample employees (first 5):")
        for emp in session.query(Employee).limit(5):
            print(f"  - ID: {emp.id}, Name: {emp.name}, Role: {emp.role}, Dept: {emp.department}, Status: {emp.status}")

        print("\nSample payroll (first 5):")
        for payroll in session.query(Payroll).join(Employee).limit(5):
            print(f"  - ID: {payroll.id}, Employee: {payroll.employee.name}, Salary: ${payroll.salary}, Bonus: ${payroll.bonus}, Period: {payroll.payment_period}")

        # Show summary by department
        print("\nEmployees by department:")
        results = session.query(
            Employee.department,
            func.count(Employee.id).label('count')
        ).group_by(Employee.department)\
         .order_by(func.count(Employee.id).desc())\
         .all()

        for row in results:
            print(f"  - {row[0]}: {row[1]} employees")

        # Show payroll summary
        print("\nPayroll summary:")
        results = session.query(
            Payroll.payment_period,
            func.count(Payroll.id).label('num_payments'),
            func.sum(Payroll.salary + Payroll.bonus - Payroll.deductions).label('total_net')
        ).group_by(Payroll.payment_period)\
         .order_by(Payroll.payment_date)\
         .all()

        for row in results:
            print(f"  - {row[0]}: {row[1]} payments, Total net: ${row[2]:,.2f}")

        print("\n" + "=" * 60)
        print("✓ MySQL population completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        if session:
            session.rollback()
        return 1
    finally:
        if session:
            session.close()
        if engine:
            engine.dispose()

    return 0


if __name__ == "__main__":
    exit(main())
