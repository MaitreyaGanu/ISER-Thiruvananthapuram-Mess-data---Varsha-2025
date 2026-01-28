import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------------
# CONNECT TO MYSQL
# -----------------------------------
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="..........",
    database="mess_dw"
)

print("Connected to MySQL successfully")

# -----------------------------------
# LOAD NOVEMBER 2025 DATA ONLY
# -----------------------------------
query = """
SELECT
    d.full_date,
    m.mess_unit_name,
    f.amount
FROM fact_expense f
JOIN dim_date d ON f.date_id = d.date_id
JOIN dim_mess_unit m ON f.mess_unit_id = m.mess_unit_id
WHERE MONTH(d.full_date) = 11
  AND YEAR(d.full_date) = 2025
"""

df = pd.read_sql(query, conn)

# -----------------------------------
# MAP MESS GROUP
# -----------------------------------
def map_mess_group(mess):
    if mess in ["CDH-1", "CDH-2"]:
        return "MAIN_MESS"
    elif mess == "CAFE":
        return "CAFE"
    else:
        return "UNKNOWN"

df["mess_group"] = df["mess_unit_name"].apply(map_mess_group)

# Remove UNKNOWN explicitly (safety)
df = df[df["mess_group"] != "UNKNOWN"]

# -----------------------------------
# DAILY TOTAL EXPENSE
# -----------------------------------
daily_df = (
    df.groupby("full_date")["amount"]
      .sum()
      .reset_index()
)

print("\nDAILY TOTAL EXPENSE (NOVEMBER 2025):")
print(daily_df)

# -----------------------------------
# AVERAGE DAILY EXPENSE
# -----------------------------------
avg_daily_expense = daily_df["amount"].mean()
print("\nAVERAGE DAILY EXPENSE:")
print(avg_daily_expense)

# -----------------------------------
# HIGH WASTAGE DAYS
# -----------------------------------
high_wastage_days = daily_df[daily_df["amount"] > avg_daily_expense]

print("\nHIGH WASTAGE DAYS:")
print(high_wastage_days)

# -----------------------------------
# ESTIMATED WASTAGE (100 kg/day baseline)
# -----------------------------------
daily_df["estimated_wastage_kg"] = (
    daily_df["amount"] / avg_daily_expense
) * 100

print("\nDAILY EXPENSE WITH ESTIMATED WASTAGE:")
print(daily_df)

# -----------------------------------
# MESS GROUP COMPARISON
# -----------------------------------
group_summary = (
    df.groupby("mess_group")["amount"]
      .mean()
      .reset_index()
)

group_summary["estimated_wastage_kg"] = (
    group_summary["amount"] / avg_daily_expense
) * 100

print("\nAVERAGE DAILY EXPENSE BY MESS GROUP:")
print(group_summary)

# -----------------------------------
# PLOTS
# -----------------------------------

# Daily Expense Trend
plt.figure()
plt.plot(daily_df["full_date"], daily_df["amount"])
plt.xticks(rotation=45)
plt.xlabel("Date")
plt.ylabel("Total Expense (Rs.)")
plt.title("Daily Total Expense – November 2025")
plt.tight_layout()
plt.show()

# Estimated Wastage Trend
plt.figure()
plt.plot(daily_df["full_date"], daily_df["estimated_wastage_kg"])
plt.xticks(rotation=45)
plt.xlabel("Date")
plt.ylabel("Estimated Wastage (kg)")
plt.title("Estimated Daily Food Wastage – November 2025")
plt.tight_layout()
plt.show()

# Main Mess vs Cafe Wastage
plt.figure()
plt.bar(
    group_summary["mess_group"],
    group_summary["estimated_wastage_kg"]
)
plt.xlabel("Mess Group")
plt.ylabel("Estimated Wastage (kg)")
plt.title("Estimated Food Wastage: Main Mess vs Café (November 2025)")
plt.tight_layout()
plt.show()
