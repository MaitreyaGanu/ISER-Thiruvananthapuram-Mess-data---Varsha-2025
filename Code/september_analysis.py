import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# Database connection
# -----------------------------
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="..........",   # replace if needed
    database="mess_dw"
)

# -----------------------------
# SQL query: August 2025 totals
# -----------------------------
query = """
SELECT 
    d.full_date,
    SUM(f.amount) AS total_expense
FROM fact_expense f
JOIN dim_date d ON f.date_id = d.date_id
WHERE MONTH(d.full_date) = 9
  AND YEAR(d.full_date) = 2025
GROUP BY d.full_date
ORDER BY d.full_date;
"""

df_august = pd.read_sql(query, conn)
conn.close()

# -----------------------------
# Plot: Date vs Total Expense
# -----------------------------
plt.figure(figsize=(10, 5))
plt.plot(df_august["full_date"], df_august["total_expense"], marker="o")
plt.title("Daily Total Mess Expense — September 2025")
plt.xlabel("Date")
plt.ylabel("Total Expense (Rs.)")
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.show()

# -----------------------------
# Optional: print table output
# -----------------------------
print("\nDAILY TOTAL EXPENSE (AUGUST 2025):")
print(df_august)
