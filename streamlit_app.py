import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Crypto FIRE Calculator", layout="centered")
st.title("Crypto FIRE Calculator — Dynamic & Year-Aware")

st.write(
    "Estimate your crypto retirement income under traditional and dynamic crypto forecast scenarios. All projected values adjust to your selected retirement year, include net FIRE income after 33% Irish CGT, and show results for both your FIRE date and a decade after."
)

# User Inputs
st.header("User Inputs")
col1, col2 = st.columns(2)
with col1:
    age = st.number_input("Current Age", min_value=18, max_value=100, value=40)
with col2:
    retire_year = st.number_input("Target Retirement Year", min_value=2025, max_value=2100, value=2035)

years_to_retire = retire_year - 2025
years_10_later = years_to_retire + 10
age_at_fire = age + years_to_retire
age_10_later = age_at_fire + 10

st.header("Crypto Portfolio: Units Held")
col1, col2 = st.columns(2)
with col1:
    btc_units = st.number_input("BTC", min_value=0.0, value=0.5)
    eth_units = st.number_input("ETH", min_value=0.0, value=5.0)
with col2:
    xrp_units = st.number_input("XRP", min_value=0.0, value=10000.0)
    ltc_units = st.number_input("LTC", min_value=0.0, value=25.0)

units_held = {
    "BTC": btc_units,
    "ETH": eth_units,
    "XRP": xrp_units,
    "LTC": ltc_units
}

eur_savings = st.number_input("Traditional EUR Savings (Optional)", min_value=0.0, value=0.0)

# Parameters
withdrawal_rate = 0.04
cgt_rate = 0.33
eur_usd = 0.86

# 2025 prices (approximate)
current_prices = {
    "BTC": 65000,
    "ETH": 3500,
    "XRP": 0.5,
    "LTC": 80
}

# 2040 forecast prices per scenario
forecast_prices_2040 = {
    "Conservative": {"BTC": 247794, "ETH": 4592, "XRP": 76, "LTC": 237},
    "Moderate":     {"BTC": 850000, "ETH": 92704, "XRP": 100, "LTC": 926},
    "Optimistic":   {"BTC": 2320693, "ETH": 117501, "XRP": 1456, "LTC": 2955}
}

trad_growth = 0.06

def projected_price(coin, forecast_2040, year):
    n = 2040 - 2025
    r = (forecast_2040 / current_prices[coin]) ** (1 / n) - 1
    y = year - 2025
    return current_prices[coin] * (1 + r) ** y

if st.button("Calculate FIRE Scenarios"):
    results = []

    portfolio_now = sum(current_prices[c] * units_held[c] for c in units_held)
    total_now = portfolio_now + eur_savings

    # Traditional scenario: Portfolio growth & withdrawals
    def trad_proj(start_value, years):
        pf = start_value * ((1 + trad_growth) ** years)
        gross = pf * withdrawal_rate
        net = gross * (1 - cgt_rate)
        return pf, net

    pf_trad_retire, net_trad_retire = trad_proj(total_now, years_to_retire)
    pf_trad_10, net_trad_10 = trad_proj(pf_trad_retire, 10)

    results.append({
        "Scenario": "Traditional (6%/yr)",
        "Year": retire_year,
        "Age": age_at_fire,
        "Portfolio (€)": pf_trad_retire,
        "Net FIRE Income (€)": net_trad_retire,
        "Net Monthly (€)": net_trad_retire / 12
    })
    results.append({
        "Scenario": "Traditional (6%/yr)",
        "Year": retire_year + 10,
        "Age": age_10_later,
        "Portfolio (€)": pf_trad_10,
        "Net FIRE Income (€)": net_trad_10,
        "Net Monthly (€)": net_trad_10 / 12
    })

    # Crypto scenarios, dynamically interpolated for chosen year and +10y
    for label, price_dict in forecast_prices_2040.items():
        prices_retire = {coin: projected_price(coin, price_dict[coin], retire_year) for coin in units_held}
        value_retire = sum(units_held[c] * prices_retire[c] for c in units_held) * eur_usd
        net_retire = value_retire * withdrawal_rate * (1 - cgt_rate)

        results.append({
            "Scenario": f"{label} Crypto",
            "Year": retire_year,
            "Age": age_at_fire,
            "Portfolio (€)": value_retire,
            "Net FIRE Income (€)": net_retire,
            "Net Monthly (€)": net_retire / 12
        })

        # 10 years post-retirement, apply traditional growth to crypto final amount
        value_10 = value_retire * ((1 + trad_growth) ** 10)
        net_10 = value_10 * withdrawal_rate * (1 - cgt_rate)

        results.append({
            "Scenario": f"{label} Crypto",
            "Year": retire_year + 10,
            "Age": age_10_later,
            "Portfolio (€)": value_10,
            "Net FIRE Income (€)": net_10,
            "Net Monthly (€)": net_10 / 12
        })

    df = pd.DataFrame(results)
    df_fmt = df.copy()
    fmtcols = ["Portfolio (€)", "Net FIRE Income (€)", "Net Monthly (€)"]
    for col in fmtcols:
        df_fmt[col] = df_fmt[col].apply(lambda x: f"€{x:,.0f}")
    st.subheader("Results Table")
    st.table(df_fmt.set_index(["Scenario", "Year"]))

    st.subheader("Visual Comparison")
    x_labels = df["Scenario"] + " (" + df["Year"].astype(str) + ")"
    x = np.arange(len(x_labels))
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.bar(x, df["Net Monthly (€)"], color="royalblue")
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, rotation=45, ha="right")
    ax.set_ylabel("Net Monthly FIRE (€)")
    ax.set_title("Net Monthly FIRE Income by Scenario and Year")
    st.pyplot(fig)

st.markdown("""
---
**Scenario Notes**

- *Traditional Asset Growth*: Calculates your crypto plus euro savings as a slow/steady investment (6% a year).
- *Crypto Conservative/Moderate/Optimistic*: Coin prices for your retirement date are interpolated from 2025 to 2040 forecast values and reflect outcomes if crypto underperforms, performs at consensus, or achieves best published forecasts.
- Net FIRE withdrawals all deduct 33% Irish CGT (as of 2025).
- Results support dynamic planning for any retirement date and can be customized for additional coins or future asset types.

This tool is intended for planning and illustration purposes only, not professional investment advice.
""")
