import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------
# CONNECT TO MYSQL
# ---------------------------------
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="...........",
    database="mess_dw"
)

print("Connected to MySQL successfully")

# ---------------------------------
# LOAD DECEMBER 2025 DATA
# ---------------------------------
query = """
SELECT
    d.full_date,
    m.mess_unit_name,
    v.vendor_name,
    f.amount
FROM fact_expense f
JOIN dim_date d ON f.date_id = d.date_id
JOIN dim_mess_unit m ON f.mess_unit_id = m.mess_unit_id
JOIN dim_vendor v ON f.vendor_id = v.vendor_id
WHERE MONTH(d.full_date) = 12
  AND YEAR(d.full_date) = 2025
"""

df = pd.read_sql(query, conn)

# ---------------------------------
# MAP MESS GROUPS
# ---------------------------------
def map_mess_group(mess):
    if mess in ["CDH-1", "CDH-2"]:
        return "MAIN_MESS"
    elif mess == "CAFE":
        return "CAFE"
    else:
        return "UNKNOWN"

df["mess_group"] = df["mess_unit_name"].apply(map_mess_group)

# Remove UNKNOWN
df = df[df["mess_group"] != "UNKNOWN"]

# ---------------------------------
# DAILY TOTAL EXPENSE
# ---------------------------------
daily_df = (
    df.groupby("full_date")["amount"]
    .sum()
    .reset_index()
    .sort_values("full_date")
)

print("\nDAILY TOTAL EXPENSE:")
print(daily_df)

# ---------------------------------
# AVERAGE DAILY EXPENSE
# ---------------------------------
avg_daily_expense = daily_df["amount"].mean()
print("\nAVERAGE DAILY EXPENSE:")
print(avg_daily_expense)

# ---------------------------------
# HIGH WASTAGE DAYS
# ---------------------------------
high_wastage_days = daily_df[daily_df["amount"] > avg_daily_expense]

print("\nHIGH WASTAGE DAYS:")
print(high_wastage_days)

# ---------------------------------
# ESTIMATED WASTAGE (PROXY)
# ---------------------------------
daily_df["estimated_wastage_kg"] = (
    daily_df["amount"] / avg_daily_expense
) * 100

print("\nDAILY EXPENSE WITH ESTIMATED WASTAGE:")
print(daily_df)

# ---------------------------------
# MESS vs CAFE COMPARISON
# ---------------------------------
group_avg = (
    df.groupby("mess_group")["amount"]
    .mean()
    .reset_index()
)

group_avg["estimated_wastage_kg"] = (
    group_avg["amount"] / avg_daily_expense
) * 100

print("\nAVERAGE DAILY EXPENSE BY MESS GROUP:")
print(group_avg)

# ---------------------------------
# PLOT 1: DAILY TOTAL EXPENSE vs DATE
# ---------------------------------
plt.figure(figsize=(10,5))
plt.plot(daily_df["full_date"], daily_df["amount"], marker='o')
plt.xticks(rotation=45)
plt.xlabel("Date")
plt.ylabel("Total Expense (Rs.)")
plt.title("Daily Total Mess Expense — December 2025")
plt.tight_layout()
plt.show()

# ---------------------------------
# PLOT 2: ESTIMATED WASTAGE — MAIN MESS vs CAFE
# ---------------------------------
plt.figure(figsize=(6,4))
plt.bar(
    group_avg["mess_group"],
    group_avg["estimated_wastage_kg"]
)
plt.xlabel("Mess Group")
plt.ylabel("Estimated Wastage (kg/day)")
plt.title("Estimated Food Wastage: Main Mess vs Café (December 2025)")
plt.tight_layout()
plt.show()
