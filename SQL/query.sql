use nha_db;
CREATE TABLE financial_year (
    id INT AUTO_INCREMENT PRIMARY KEY,
    financial_year VARCHAR(20) NOT NULL
);

CREATE TABLE item (
    id INT AUTO_INCREMENT PRIMARY KEY,
    items_name VARCHAR(255) NOT NULL
);

CREATE TABLE budget (
    id INT AUTO_INCREMENT PRIMARY KEY,
    financial_year_id INT,
    total_budget DECIMAL(15, 2),
    budget_month VARCHAR(20),
    budget_used DECIMAL(15, 2),
    budget_used_upto_june DECIMAL(15, 2),
    reporting_month_last_day DATE,
    remaining_budget DECIMAL(15, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (financial_year_id) REFERENCES financial_year(id)
);

CREATE TABLE procurement (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_name VARCHAR(255),
    units INT,
    expenditure DECIMAL(15, 2)
);

CREATE TABLE repair_maintenance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_name VARCHAR(255),
    unit_in_house INT,
    units_externals INT,
    hours_spend_in_house DECIMAL(10, 2),
    days_externals DECIMAL(10, 2),
    expenditure DECIMAL(15, 2),
    item_total DECIMAL(15, 2),
    percentage_of_an_item DECIMAL(5, 2),
    avg_cost_per_unit DECIMAL(10, 2),
    total_unit_repaired_in_house INT,
    total_unit_repaired_external INT
);