"""
DATA PREPROCESSING & WAREHOUSE INTEGRATION PIPELINE
IISER TVM Mess DWBI Project – Varsha 2025

---------------------------------------------------
WAREHOUSE CREATION (DONE IN MYSQL - DOCUMENTED HERE)
---------------------------------------------------

-- Dimension Tables
CREATE TABLE dim_date (
    date_id INT AUTO_INCREMENT PRIMARY KEY,
    full_date DATE UNIQUE,
    day INT,
    month INT,
    year INT,
    day_name VARCHAR(10),
    is_weekend BOOLEAN
);

CREATE TABLE dim_vendor (
    vendor_id INT AUTO_INCREMENT PRIMARY KEY,
    vendor_name VARCHAR(255) UNIQUE
);

CREATE TABLE dim_mess_unit (
    mess_unit_id INT AUTO_INCREMENT PRIMARY KEY,
    mess_unit_name VARCHAR(50) UNIQUE
);

-- Fact Table
CREATE TABLE fact_expense (
    expense_id INT AUTO_INCREMENT PRIMARY KEY,
    date_id INT,
    vendor_id INT,
    mess_unit_id INT,
    amount DECIMAL(12,2),
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
    FOREIGN KEY (vendor_id) REFERENCES dim_vendor(vendor_id),
    FOREIGN KEY (mess_unit_id) REFERENCES dim_mess_unit(mess_unit_id)
);

---------------------------------------------------
PYTHON ROLE
---------------------------------------------------
Python is used ONLY to:
1. Extract data from the warehouse
2. Clean and standardize text fields
3. Remove invalid records
4. Prepare analysis-ready datasets

No warehouse creation or loading is done here.
"""

import pandas as pd
import mysql.connector

# -------------------------------------------------
# 1. Connect to MySQL Data Warehouse
# -------------------------------------------------

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="..........",
    database="mess_dw"
)

# -------------------------------------------------
# 2. Extract Transaction-Level Data
# -------------------------------------------------

query = """
SELECT
    d.full_date,
    v.vendor_name,
    m.mess_unit_name,
    f.amount
FROM fact_expense f
JOIN dim_date d ON f.date_id = d.date_id
JOIN dim_vendor v ON f.vendor_id = v.vendor_id
JOIN dim_mess_unit m ON f.mess_unit_id = m.mess_unit_id
"""

df = pd.read_sql(query, conn)

# -------------------------------------------------
# 3. Handle Missing Values
# -------------------------------------------------
# Missing values here represent INCOMPLETE TRANSACTIONS.
# Imputation is NOT appropriate for identifiers or monetary values.
# Hence, such records are removed.

df = df.dropna(subset=[
    "full_date",
    "vendor_name",
    "mess_unit_name",
    "amount"
])

# -------------------------------------------------
# 4. Remove Invalid Expense Records
# -------------------------------------------------

df = df[df["amount"] > 0]

# -------------------------------------------------
# 5. Standardize Text Fields
# -------------------------------------------------

df["vendor_name"] = (
    df["vendor_name"]
    .str.strip()
    .str.upper()
)

df["mess_unit_name"] = (
    df["mess_unit_name"]
    .str.strip()
    .str.upper()
)

# -------------------------------------------------
# 6. Normalize Known Naming Variations
# -------------------------------------------------

df["mess_unit_name"] = df["mess_unit_name"].replace({
    "CDH 1": "CDH-1",
    "CDH I": "CDH-1",
    "CDH-01": "CDH-1",
    "CDH 2": "CDH-2",
    "CDH II": "CDH-2",
    "CDH-02": "CDH-2",
    "CAFE-1": "CAFE",
    "CAFE 1": "CAFE",
    "CAFÉ": "CAFE"
})

# -------------------------------------------------
# 7. Date Formatting
# -------------------------------------------------

df["full_date"] = pd.to_datetime(df["full_date"])

# -------------------------------------------------
# 8. Final Clean Dataset
# -------------------------------------------------

df = df.sort_values("full_date").reset_index(drop=True)

# -------------------------------------------------
# 9. Close Connection
# -------------------------------------------------

conn.close()


