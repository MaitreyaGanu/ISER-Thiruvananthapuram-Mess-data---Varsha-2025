import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt

# --------------------------------
# CONNECT TO MYSQL
# --------------------------------
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="..........",
    database="mess_dw"
)

print("Connected to MySQL successfully")

# --------------------------------
# LOAD OCTOBER 2025 DATA ONLY
# --------------------------------
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
WHERE MONTH(d.full_date) = 10
  AND YEAR(d.full_date) = 2025
ORDER BY d.full_date
"""

df = pd.read_sql(query, conn)

# --------------------------------
# MAP MESS GROUP
# --------------------------------
def map_mess_group(mess):
    if mess in ["CDH-1", "CDH-2"]:
        return "MAIN_MESS"
    elif mess == "CAFE":
        return "CAFE"
    else:
        return "UNKNOWN"

df["mess_group"] = df["mess_unit_name"].apply(map_mess_group)

# REMOVE UNKNOWN (ADMIN / CASH VOUCHERS)
df = df[df["mess_group"] != "UNKNOWN"]

print("\nMess group mapping:")
print(df[["mess_unit_name", "mess_group"]].drop_duplicates())

# --------------------------------
# DAILY TOTAL EXPENSE
# --------------------------------
daily_expense = (
    df.groupby("full_date")["amount"]
      .sum()
      .reset_index()
)

print("\nDAILY TOTAL EXPENSE:")
print(daily_expense)

# --------------------------------
# AVERAGE DAILY EXPENSE (MONTH)
# --------------------------------
avg_daily_expense = daily_expense["amount"].mean()
print("\nAVERAGE DAILY EXPENSE:")
print(avg_daily_expense)

# --------------------------------
# HIGH WASTAGE DAYS (ABOVE AVERAGE)
# --------------------------------
high_wastage_days = daily_expense[
    daily_expense["amount"] > avg_daily_expense
]

print("\nHIGH WASTAGE DAYS:")
print(high_wastage_days)

# --------------------------------
# ESTIMATED WASTAGE (PROXY)
# --------------------------------
daily_expense["estimated_wastage_kg"] = (
    daily_expense["amount"] / avg_daily_expense
) * 100

print("\nDAILY EXPENSE WITH ESTIMATED WASTAGE:")
print(daily_expense)

# --------------------------------
# AVERAGE DAILY EXPENSE BY MESS GROUP
# --------------------------------
group_summary = (
    df.groupby("mess_group")["amount"]
      .mean()
      .reset_index()
)

print("\nAVERAGE DAILY EXPENSE BY MESS GROUP:")
print(group_summary)

# --------------------------------
# ESTIMATED WASTAGE BY MESS GROUP
# --------------------------------
group_summary["estimated_wastage_kg"] = (
    group_summary["amount"] / avg_daily_expense
) * 100

print("\nESTIMATED WASTAGE BY MESS GROUP:")
print(group_summary)

# --------------------------------
# PLOT 1: DATE vs TOTAL EXPENSE
# --------------------------------
plt.figure(figsize=(8,4))
plt.plot(
    daily_expense["full_date"],
    daily_expense["amount"],
    marker="o"
)
plt.xlabel("Date")
plt.ylabel("Total Expense (₹)")
plt.title("October 2025: Daily Total Mess Expense")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# --------------------------------
# PLOT 2: DATE vs ESTIMATED WASTAGE
# --------------------------------
plt.figure(figsize=(8,4))
plt.plot(
    daily_expense["full_date"],
    daily_expense["estimated_wastage_kg"],
    marker="o"
)
plt.xlabel("Date")
plt.ylabel("Estimated Wastage (kg)")
plt.title("October 2025: Estimated Daily Food Wastage")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# --------------------------------
# PLOT 3: BAR PLOT – ESTIMATED WASTAGE
# MAIN MESS vs CAFE
# --------------------------------
plt.figure(figsize=(6,4))
plt.bar(
    group_summary["mess_group"],
    group_summary["estimated_wastage_kg"]
)
plt.xlabel("Mess Group")
plt.ylabel("Estimated Wastage (kg/day)")
plt.title("October 2025: Estimated Food Wastage – Main Mess vs Café")
plt.tight_layout()
plt.show()
