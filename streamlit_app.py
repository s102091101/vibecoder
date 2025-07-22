import streamlit as st

st.set_page_config(page_title="Crypto FIRE Calculator", layout="centered")

st.title("🚀 Crypto FIRE Calculator")

st.write("Estimate your crypto retirement date and income using three different growth scenarios. Enter your details below:")

# User Inputs
col1, col2 = st.columns(2)
with col1:
    age = st.number_input("Your Current Age", min_value=18, max_value=99, value=40, step=1)
with col2:
    retire_year = st.number_input("Target Retirement Year", min_value=2025, max_value=2100, value=2035, step=1)

crypto_balance = st.number_input("Current Crypto Balance (€)", min_value=0.0, value=100000.0, step=1000.0, format="%.2f")
current_year = 2025  # Update if you're using a different current year

# Scenario settings
scenarios = {
    "Optimistic": 0.10,
    "Moderate": 0.06,
    "Conservative": 0.03
}
withdrawal_rate = 0.04

if st.button("Calculate"):
    years = int(retire_year - current_year)
    if years < 0:
        st.error("Retirement year must be greater than or equal to the current year.")
    else:
        st.subheader("Retirement Projections")
        results = []
        for name, growth_rate in scenarios.items():
            portfolio = crypto_balance * ((1 + growth_rate) ** years)
            fire_annual = portfolio * withdrawal_rate
            fire_monthly = fire_annual / 12
            results.append({
                "Scenario": name,
                "Portfolio at Retirement (€)": f"{portfolio:,.2f}",
                "FIRE Yearly Income (€)": f"{fire_annual:,.2f}",
                "FIRE Monthly Income (€)": f"{fire_monthly:,.2f}",
                "Age at FIRE": f"{age + years}",
            })
        st.table(results)

st.markdown("""
---
**How it works:**  
- "Portfolio at Retirement" is your starting balance compounded annually at the listed growth rate for each scenario.
- "FIRE Income" is calculated using the classic 4% safe withdrawal rule.
- Your age at FIRE is your current age plus the years until your target retirement.

_Always review results with a financial advisor before making retirement decisions._
""")
