import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Crypto FIRE Calculator", layout="centered")
st.title("Crypto FIRE Calculator — FIRE Number + Forecasts")

st.write(
    """
    Estimate your crypto retirement income using dynamic growth models compared to your personal FIRE target.
    This tool forecasts values for your selected retirement year and a date 10 years later.
    It includes Irish CGT (33%) and calculates whether you're FIRE ready based on your current spending.
    """
)

# === Inputs ===
st.header("🧮 Basic Information and Spending")
col1, col2 = st.columns(2)
with col1:
    age = st.number_input("Your Current Age", min_value=18, max_value=99, value=40)
with col2:
    retire_year = st.number_input("Target Retirement Year", min_value=2025, max_value=2100, value=2035)

st.header("💸 Weekly Spending")
weekly_exp = st.number_input(
    "Weekly Expenditure (€)",
    value=1000.0,
    step=10.0,
    help="Based on CSO average household budget (2025)"
)

# === FIRE Number & Expenses ===
annual_expenses = weekly_exp * 52
fire_number = annual_expenses * 25
fire_monthly_requirement = fire_number / 12

st.markdown(f"""
**Annual Expenses:** €{annual_expenses:,.0f}  
**FIRE Number (Expenses × 25):** €{fire_number:,.0f}  
**Required Net Monthly FIRE Income:** €{fire_monthly_requirement:,.0f}
""")

# === Portfolio Inputs ===
st.header("📊 Portfolio Holdings")
col1, col2 = st.columns(2)
with col1:
    btc_units = st.number_input("BTC held", min_value=0.0, value=0.5)
    eth_units = st.number_input("ETH held", min_value=0.0, value=5.0)
with col2:
    xrp_units = st.number_input("XRP held", min_value=0.0, value=10000.0)
    ltc_units = st.number_input("LTC held", min_value=0.0, value=25.0)

eur_savings = st.number_input("Traditional EUR Savings (Optional)", min_value=0.0, value=0.0)

units_held = {
    "BTC": btc_units,
    "ETH": eth_units,
    "XRP": xrp_units,
    "LTC": ltc_units
}

# Constants
current_year = 2025
years_to_retire = retire_year - current_year
years_10_later = years_to_retire + 10
age_at_retire = age + years_to_retire
age_10_years = age_at_retire + 10
conversion_rate = 0.86  # USD to EUR
withdrawal_rate = 0.04
cgt_rate = 0.33
trad_growth = 0.06

current_prices = {
    "BTC": 65000,
    "ETH": 3500,
    "XRP": 0.5,
    "LTC": 80
}

forecast_prices_2040 = {
    "Conservative": {"BTC": 247794, "ETH": 4592, "XRP": 76, "LTC": 237},
    "Moderate":     {"BTC": 850000, "ETH": 92704, "XRP": 100, "LTC": 926},
    "Optimistic":   {"BTC": 2320693, "ETH": 117501, "XRP": 1456, "LTC": 2955}
}

def projected_price(coin, forecast_2040_value, year):
    n = 2040 - 2025
    r = (forecast_2040_value / current_prices[coin]) ** (1 / n) - 1
    years = year - 2025
    return current_prices[coin] * (1 + r) ** years

def compute_trad_projection(value, years):
    final = value * ((1 + trad_growth) ** years)
    income = final * withdrawal_rate * (1 - cgt_rate)
    return final, income

# === Compute ===
if st.button("Calculate FIRE Scenarios"):
    results = []

    # Total balance in EUR now
    current_value = sum(units_held[c] * current_prices[c] for c in units_held)
    full_balance_now = current_value + eur_savings

    # Traditional projection - Retirement
    trad_value_ret, trad_income_ret = compute_trad_projection(full_balance_now, years_to_retire)
    results.append({
        "Scenario": "Traditional (6%)",
        "Year": retire_year,
        "Age": age_at_retire,
        "Portfolio (€)": trad_value_ret,
        "Net FIRE Income (€)": trad_income_ret,
        "Net Monthly (€)": trad_income_ret / 12
    })

    # Traditional - 10 years later
    trad_value_10, trad_income_10 = compute_trad_projection(trad_value_ret, 10)
    results.append({
        "Scenario": "Traditional (6%)",
        "Year": retire_year + 10,
        "Age": age_10_years,
        "Portfolio (€)": trad_value_10,
        "Net FIRE Income (€)": trad_income_10,
        "Net Monthly (€)": trad_income_10 / 12
    })

    # Crypto Scenarios
    for label, prices_2040 in forecast_prices_2040.items():
        # Estimate price at retirement
        price_retire = {
            coin: projected_price(coin, prices_2040[coin], retire_year)
            for coin in units_held
        }
        value_usd = sum(units_held[c] * price_retire[c] for c in units_held)
        value_eur = value_usd * conversion_rate
        income_now = value_eur * withdrawal_rate * (1 - cgt_rate)

        results.append({
            "Scenario": f"{label} Crypto",
            "Year": retire_year,
            "Age": age_at_retire,
            "Portfolio (€)": value_eur,
            "Net FIRE Income (€)": income_now,
            "Net Monthly (€)": income_now / 12
        })

        # 10 years later projection using 6% traditional growth
        value_10 = value_eur * ((1 + trad_growth) ** 10)
        income_10 = value_10 * withdrawal_rate * (1 - cgt_rate)

        results.append({
            "Scenario": f"{label} Crypto",
            "Year": retire_year + 10,
            "Age": age_10_years,
            "Portfolio (€)": value_10,
            "Net FIRE Income (€)": income_10,
            "Net Monthly (€)": income_10 / 12
        })

    # Convert results to DataFrame
    df = pd.DataFrame(results)

    # Format for table
    df_fmt = df.copy()
    for col in ["Portfolio (€)", "Net FIRE Income (€)", "Net Monthly (€)"]:
        df_fmt[col] = df_fmt[col].apply(lambda x: f"€{x:,.0f}")
    st.subheader("Results Table")
    st.table(df_fmt.set_index(["Scenario", "Year"]))

    # === Chart ===
    st.subheader("Net Monthly FIRE Income vs Required FIRE Target")
    x_labels = df["Scenario"] + " (" + df["Year"].astype(str) + ")"
    x = np.arange(len(x_labels))
    fig, ax = plt.subplots(figsize=(11, 6))
    bar = ax.bar(x, df["Net Monthly (€)"], color="blue")
    ax.axhline(fire_monthly_requirement, color="red", linestyle="--", linewidth=2,
               label=f"Required FIRE Income: €{fire_monthly_requirement:,.0f}/mo")
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, rotation=45, ha="right")
    ax.set_ylabel("Net Monthly FIRE Income (€)")
    ax.set_title("FIRE Income by Scenario With Target Threshold")
    ax.legend()
    plt.tight_layout()
    st.pyplot(fig)

st.markdown("""
---
This tool compares your projected FIRE income against your personal FIRE number.

- **FIRE Number** is calculated using your weekly expenses × 52 × 25.
- **Forecasts** are updated for your retirement year and reflect crypto growth between now and 2040.
- **Includes 33% CGT on withdrawals** per Irish tax treatment.
- All figures are inflation-agnostic and presented in today’s euros.

This is not financial advice — but a helpful planning tool for exploring FIRE paths.
""")
