import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Crypto FIRE Calculator", layout="centered")
st.title("🚀 Crypto FIRE Calculator — With Traditional & Crypto Scenario Projections")

st.write("Enter your cryptocurrency portfolio and see your potential FIRE income in 2040 under traditional and crypto-specific forecast scenarios. Includes Irish Capital Gains Tax (CGT) on withdrawals.")

st.header("User Information")
col1, col2 = st.columns(2)
with col1:
    age = st.number_input("Your Current Age", min_value=18, max_value=100, value=40, step=1)
with col2:
    retire_year = st.number_input("Target Retirement Year", min_value=2025, max_value=2100, value=2035, step=1)

st.header("Crypto Portfolio: Units Held")
col1, col2 = st.columns(2)
with col1:
    btc_units = st.number_input("BTC", min_value=0.0, value=0.5, step=0.01)
    eth_units = st.number_input("ETH", min_value=0.0, value=5.0, step=0.1)
with col2:
    xrp_units = st.number_input("XRP", min_value=0, value=10000, step=100)
    ltc_units = st.number_input("LTC", min_value=0.0, value=25.0, step=1.0)

units_held = {
    "BTC": btc_units,
    "ETH": eth_units,
    "XRP": xrp_units,
    "LTC": ltc_units
}

st.header("Optional: Add Additional Euro Savings")
euro_balance = st.number_input("Traditional EUR Savings (Optional)", min_value=0.0, value=0.0, step=1000.0)

withdrawal_rate = 0.04
cgt_rate = 0.33
current_year = 2025

traditional_growth = 0.06  # Treats whole portfolio as traditional mixed asset growth

# Crypto price scenarios (USD, 2040 forecasted)
crypto_prices_2040 = {
    "Conservative": {"BTC": 247794, "ETH": 4592, "XRP": 76, "LTC": 237},
    "Moderate":     {"BTC": 850000, "ETH": 92704, "XRP": 100, "LTC": 926},
    "Optimistic":   {"BTC": 2320693, "ETH": 117501, "XRP": 1456, "LTC": 2955}
}

years = retire_year - current_year

if st.button("Calculate FIRE Scenarios"):
    if years < 0:
        st.error("Please choose a retirement year in the future.")
    else:
        st.subheader(f"Results for Retirement in {retire_year} (Age {age + years})")

        results = []

        # Traditional asset growth scenario
        total_crypto_value_now = 0  # Give users the chance to leave some coins blank
        # Use dummy values from price APIs or a benchmark if needed

        # Estimate total euro value now for crypto balance
        dummy_prices_now = {"BTC": 65000, "ETH": 3500, "XRP": 0.50, "LTC": 80}
        for coin, units in units_held.items():
            total_crypto_value_now += units * dummy_prices_now[coin]

        full_balance_now = total_crypto_value_now + euro_balance
        trad_portfolio = full_balance_now * ((1 + traditional_growth) ** years)
        trad_gross = trad_portfolio * withdrawal_rate
        trad_net = trad_gross * (1 - cgt_rate)

        results.append({
            "Scenario": "Traditional Asset Growth (6%/yr)",
            "Portfolio at Retirement (€)": trad_portfolio,
            "Gross Yearly FIRE (€)": trad_gross,
            "Net Yearly FIRE (€)": trad_net,
            "Net Monthly FIRE (€)": trad_net / 12,
            "Age at FIRE": age + years
        })

        # Loop through crypto-defined scenarios
        for name, prices in crypto_prices_2040.items():
            usd_total = sum(units_held[coin] * prices[coin] for coin in units_held)
            eur_total = usd_total * 0.86  # Convert USD → EUR
            fire_gross = eur_total * withdrawal_rate
            fire_net = fire_gross * (1 - cgt_rate)

            results.append({
                "Scenario": f"Crypto {name} Scenario",
                "Portfolio at Retirement (€)": eur_total,
                "Gross Yearly FIRE (€)": fire_gross,
                "Net Yearly FIRE (€)": fire_net,
                "Net Monthly FIRE (€)": fire_net / 12,
                "Age at FIRE": age + years
            })

        df = pd.DataFrame(results)
        df_display = df.copy()
        for col in [
            "Portfolio at Retirement (€)",
            "Gross Yearly FIRE (€)",
            "Net Yearly FIRE (€)",
            "Net Monthly FIRE (€)"
        ]:
            df_display[col] = df_display[col].apply(lambda x: f"€{x:,.0f}")
        st.table(df_display.set_index("Scenario"))

        # 🎯 Visualization
        fig, ax = plt.subplots(figsize=(10, 6))
        x = range(len(df))
        bar1 = ax.bar(x, df["Portfolio at Retirement (€)"], width=0.4, label="Portfolio (€)")
        bar2 = ax.bar([i + 0.4 for i in x], df["Net Monthly FIRE (€)"], width=0.4, label="Net Monthly FIRE (€)", color="orange")

        ax.set_xticks([i + 0.2 for i in x])
        ax.set_xticklabels(df["Scenario"], rotation=45, ha="right")
        ax.set_ylabel("Euro (€)")
        ax.set_title("2040 Portfolio vs Monthly Net FIRE Income")
        ax.legend()
        st.pyplot(fig)

st.markdown("""
---
### 🔎 About the Scenarios

- **Traditional Asset Growth:** Your crypto is treated like stocks/bonds with 6% annual return.
- **Crypto Conservative:** Crypto grows slowly; modest 2040 BTC/XRP/ETH projections.
- **Crypto Moderate:** Based on widely published mid-range 2040 forecasts.
- **Crypto Optimistic:** Assumes crypto hits full global adoption; top of forecast range.

**Calculations:**
- Assumes 4% annual FIRE withdrawals.
- Irish CGT (33%) applied to all capital gains withdrawals.
- Prices and forecasts from major analysts as of 2025.

> *Disclaimer: This is an educational tool. Not financial advice.*
""")

