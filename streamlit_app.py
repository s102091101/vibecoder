import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Crypto FIRE Calculator", layout="centered")
st.title("🚀 Crypto FIRE Calculator — With Net CGT and Scenario Graph")

st.write("Estimate your crypto retirement date and expected annual income under three scenarios—including net income after Irish Capital Gains Tax withdrawals. See results visually across scenarios.")

col1, col2 = st.columns(2)
with col1:
    age = st.number_input("Your Current Age", min_value=18, max_value=99, value=40, step=1)
with col2:
    retire_year = st.number_input("Target Retirement Year", min_value=2025, max_value=2100, value=2035, step=1)

crypto_balance = st.number_input("Current Crypto Balance (€)", min_value=0.0, value=100000.0, step=1000.0, format="%.2f")
current_year = 2025  # Adjust as needed

scenarios = {
    "Optimistic": 0.10,
    "Moderate": 0.06,
    "Conservative": 0.03
}
withdrawal_rate = 0.04
cgt_rate = 0.33

if st.button("Calculate"):
    years = int(retire_year - current_year)
    if years < 0:
        st.error("Retirement year must be after current year.")
    else:
        st.subheader("Retirement Projections")
        results = []
        for name, growth_rate in scenarios.items():
            portfolio = crypto_balance * ((1 + growth_rate) ** years)
            fire_gross_annual = portfolio * withdrawal_rate
            fire_net_annual = fire_gross_annual * (1 - cgt_rate)
            fire_net_monthly = fire_net_annual / 12
            results.append({
                "Scenario": name,
                "Portfolio at Retirement (€)": portfolio,
                "Gross Yearly FIRE (€)": fire_gross_annual,
                "Net Yearly FIRE (€)": fire_net_annual,
                "Net Monthly FIRE (€)": fire_net_monthly,
                "Age at FIRE": int(age + years),
            })
        df_results = pd.DataFrame(results)
        df_show = df_results.copy()
        for col in ["Portfolio at Retirement (€)", "Gross Yearly FIRE (€)", "Net Yearly FIRE (€)", "Net Monthly FIRE (€)"]:
            df_show[col] = df_show[col].apply(lambda x: f"€{x:,.0f}")
        st.table(df_show)

        # Scenario chart (grouped bar)
        fig, ax = plt.subplots(figsize=(8,5))
        x = range(len(scenarios))
        ax.bar(x, df_results["Portfolio at Retirement (€)"], width=0.35, label="Portfolio (€)")
        ax.bar([i + 0.35 for i in x], df_results["Net Monthly FIRE (€)"], width=0.35, color="orange", label="Net Monthly FIRE Income (€)")
        ax.set_xticks([i + 0.175 for i in x])
        ax.set_xticklabels(df_results["Scenario"])
        ax.set_ylabel("EUR")
        ax.set_title("Crypto FIRE Scenarios: Portfolio & Net Monthly Income")
        ax.legend()
        st.pyplot(fig)

st.markdown("""
---
- **Portfolio at Retirement** grows by compounding at each scenario’s rate.
- **Net FIRE Income** calculates after 33% Irish Capital Gains Tax on gains.
- The classic 4% “safe withdrawal” rule helps plan sustainable withdrawals.
""")
