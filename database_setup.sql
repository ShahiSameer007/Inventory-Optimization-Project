-- These commands are used in pgadmin to setup postgres database schemas and insert the data

-- 1. Inventory Data Table
CREATE TABLE inventory_data (
    product_id INTEGER PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    current_stock INTEGER NOT NULL,
    reorder_quantity NUMERIC(10, 2) NOT NULL, 
    unit_cost NUMERIC(10, 2) NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL,
    low_stock_threshold NUMERIC(10, 2) NOT NULL
);
-- 2. Audit Log Table
CREATE TABLE psoe_audit_log (
    log_id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES inventory_data(product_id), -- Links back to the product
    order_quantity NUMERIC(10, 2) NOT NULL,
    budget_cost NUMERIC(10, 2) NOT NULL,
    order_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) NOT NULL
);

ALTER TABLE psoe_audit_log 
ADD COLUMN run_type VARCHAR(50) NOT NULL DEFAULT 'OPTIMIZED';

-- 3. Import the Data from CSV
COPY inventory_data (product_id, product_name, current_stock, reorder_quantity, unit_cost, unit_price, low_stock_threshold)
    FROM 'D:\PSOE_Project\datasets\psoe_data_cleaned.csv'
    DELIMITER ','
    CSV HEADER;

SELECT * FROM inventory_data LIMIT 5;