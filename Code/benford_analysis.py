import mysql.connector
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import chisquare, chi2

# -------------------------------
# CONNECT TO MYSQL
# -------------------------------
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="..........",
    database="mess_dw"
)

print("Connected to MySQL successfully")

# -------------------------------
# LOAD EXPENSE DATA
# (Vendor-level payments across Varsha 2025)
# -------------------------------
query = """
SELECT amount
FROM fact_expense
WHERE amount > 0
"""

df = pd.read_sql(query, conn)

# -------------------------------
# EXTRACT FIRST DIGITS
# -------------------------------
df["first_digit"] = df["amount"].astype(str).str.replace('.', '', regex=False).str.lstrip('0').str[0]
df = df[df["first_digit"].isin(list("123456789"))]
df["first_digit"] = df["first_digit"].astype(int)

# -------------------------------
# OBSERVED FREQUENCIES
# -------------------------------
observed_counts = df["first_digit"].value_counts().sort_index()
total_observations = observed_counts.sum()

# -------------------------------
# EXPECTED BENFORD FREQUENCIES
# -------------------------------
digits = np.arange(1, 10)
benford_probs = np.log10(1 + 1 / digits)
expected_counts = benford_probs * total_observations

# -------------------------------
# CHI-SQUARE GOODNESS-OF-FIT TEST
# -------------------------------
chi_stat, p_value = chisquare(
    f_obs=observed_counts.values,
    f_exp=expected_counts
)

alpha = 0.05
df_chi = len(digits) - 1
critical_value = chi2.ppf(1 - alpha, df_chi)

# -------------------------------
# PRINT STATISTICAL RESULTS
# -------------------------------
print("\n--- BENFORD'S LAW CHI-SQUARE TEST (5% SIGNIFICANCE) ---")
print(f"Total observations: {total_observations}")
print(f"Chi-square statistic: {chi_stat:.4f}")
print(f"Degrees of freedom: {df_chi}")
print(f"Critical value (α = 0.05): {critical_value:.4f}")
print(f"P-value: {p_value:.4f}")

if chi_stat < critical_value:
    print("Result: No statistically significant deviation from Benford's Law.")
    print("Interpretation: Expense data appears naturally distributed.")
else:
    print("Result: Statistically significant deviation detected.")
    print("Interpretation: Data may warrant further forensic audit.")

# -------------------------------
# PREPARE DATAFRAME FOR DISPLAY
# -------------------------------
benford_df = pd.DataFrame({
    "Digit": digits,
    "Observed_Count": observed_counts.values,
    "Expected_Count": expected_counts.round(2),
    "Observed_%": (observed_counts.values / total_observations * 100).round(2),
    "Expected_%": (benford_probs * 100).round(2)
})

print("\nObserved vs Expected Frequencies:")
print(benford_df)

# -------------------------------
# PLOT BENFORD DISTRIBUTION
# -------------------------------
plt.figure(figsize=(8, 5))
plt.plot(digits, benford_probs * 100, marker='o', label="Benford Expected", linewidth=2)
plt.bar(digits, benford_df["Observed_%"], alpha=0.7, label="Observed")

plt.xlabel("First Digit")
plt.ylabel("Percentage Frequency")
plt.title("Benford's Law Analysis of Mess Expenditure Data")
plt.xticks(digits)
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.6)

plt.tight_layout()
plt.show()

# -------------------------------
# CLOSE CONNECTION
# -------------------------------
conn.close()
