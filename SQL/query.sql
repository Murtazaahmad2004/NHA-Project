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
    total_budget INT,
    budget_month VARCHAR(20),
    budget_used INT,
    budget_used_upto_june INT,
    reporting_month_last_day DATE,
    remaining_budget INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (financial_year_id) REFERENCES financial_year(id)
);

CREATE TABLE procurement (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_name VARCHAR(255),
    units INT,
    expenditure INT
);

CREATE TABLE repair_maintenance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_name VARCHAR(255),
    unit_in_house INT,
    units_externals INT,
    hours_spend_in_house INT,
    days_externals INT,
    expenditure INT,
    item_total INT,
    percentage_of_an_item INT,
    avg_cost_per_unit INT,
    total_unit_repaired_in_house INT,
    total_unit_repaired_external INT
);

CREATE TABLE complaints (
	id INT AUTO_INCREMENT PRIMARY KEY,
    network_resolved_complaints varchar(255),
    network_pending_complaints varchar(255),
    it_resolved_complaints varchar(255),
    it_pending_complaints varchar(255),
    total_hours_spend int
);

CREATE TABLE store_items (
	id INT AUTO_INCREMENT PRIMARY KEY,
    items_name varchar(255),
    pending_dmands varchar(255),
    previous_month TEXT, 
    demands_of_previous_month int,
    issued_of_previous_month int, 
    current_month TEXT,
    demands_of_current_month int, 
    issued_of_current_month int,
    total_hours_spend int
); 

CREATE TABLE uploding (
	id INT AUTO_INCREMENT PRIMARY KEY,
    particulars varchar(255),
    reserve_person int,
    previous_month text,
    previous_month_quantity text,
    current_month text,
    current_month_quantity text,
    hoursspend int
);

CREATE TABLE software_form (
	id INT AUTO_INCREMENT PRIMARY KEY,
    activities varchar(255),
    no_of_software_under_development int,
    no_of_team_member int,
    working_hours_during_month int
);

CREATE TABLE core_software (
	id INT AUTO_INCREMENT PRIMARY KEY,
    core_software varchar(255),
    modules int
);

CREATE TABLE software_complaints (
	id INT AUTO_INCREMENT PRIMARY KEY,
    software_name varchar(255),
    description text,
    total_complaints int,
    resolved int
);

CREATE TABLE meetings (
	id INT AUTO_INCREMENT PRIMARY KEY,
    sections varchar(255),
    meetings int,
    internal int,
    external int,
    hours_spend int,
    remarks varchar(255)
);

CREATE TABLE network (
	id INT AUTO_INCREMENT PRIMARY KEY,
    item varchar(255),
    down_time int,
    up_time_percentage INT,
    remarks varchar(255)
);

CREATE TABLE pmis (
	id INT AUTO_INCREMENT PRIMARY KEY,
    total_packages int,
    monthly_progress int,
    progress_percentage INT,
    drone_video int,
    drone_video_percentage INT
);

CREATE TABLE summarize (
	id INT AUTO_INCREMENT PRIMARY KEY,
    procurement_activities varchar(255),
    current_month varchar(255),
    available_hours int,
    working_strength int,
    hours_worked int
);