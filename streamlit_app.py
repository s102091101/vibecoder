import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Crypto FIRE Calculator", layout="centered")
st.title("🚀 Crypto FIRE Calculator — Dynamic & Year-Aware")

st.write(
    """
    Estimate your crypto retirement income under traditional asset scenarios and dynamic crypto forecasts.
    Forecast values scale based on your chosen retirement year, and include net FIRE income after 33% Irish CGT.
    """
)

# === USER INPUTS ===
st.header("👤 User Inputs")
col1, col2 = st.columns(2)
with col1:
    age = st.number_input("Your Current Age", min_value=18, max_value=100, value=40)
with col2:
    retire_year = st.number_input("Target Retirement Year", min_value=2025, max_value=2100, value=2035)

current_year = 2025
years_to_retire = retire_year - current_year
years_10_later = years_to_retire + 10
age_at_fire = age + years_to_retire
age_10_later = age_at_fire + 10

# === CRYPTO HOLDINGS ===
st.header("💰 Your Crypto Holdings")
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

# === EUROS / OTHER SAVINGS ===
eur_savings = st.number_input("Traditional EUR Savings (Optional)", min_value=0.0, value=0.0)

# === SETTINGS ===
withdrawal_rate = 0.04
cgt_rate = 0.33
eur_usd = 0.86

# === PRICES ===

# Approximate current prices (as of 2025)
current_prices = {
    "BTC": 65000,
    "ETH": 3500,
    "XRP": 0.5,
    "LTC": 80
}

# Forecast prices for 2040
forecast_prices_2040 = {
    "Conservative": {"BTC": 247794, "ETH": 4592, "XRP": 76, "LTC": 237},
    "Moderate": {"BTC": 850000, "ETH": 92704, "XRP": 100, "LTC": 926},
    "Optimistic": {"BTC": 2320693, "ETH": 117501, "XRP": 1456, "LTC": 2955}
}

# Function to compute price at any future year using compound growth
def get_projected_price(coin, forecast_price_2040, target_year):
    r = (forecast_price_2040 / current_prices[coin]) ** (1 / (2040 - current_year)) - 1
    future_years = target_year - current_year
    return current_prices[coin] * (1 + r) ** future_years

# Traditional asset growth rate (e.g., stocks, 6%)
trad_growth = 0.06

if st.button("📊 Calculate"):
    results = []

    # Estimate total portfolio now
    portfolio_now = sum(current_prices[coin] * units_held[coin] for coin in units_held)
    total_now = portfolio_now + eur_savings

    # === Traditional Scenario ===
    def compute_traditional_value(start, years):
        value = start * ((1 + trad_growth) ** years)
        gross = value * withdrawal_rate
        net = gross * (1 - cgt_rate)
        return value, net

    # Retirement
    portfolio_trad_retire, net_retire = compute_traditional_value(total_now, years_to_retire)
    # 10 years later
    portfolio_trad_10, net_10 = compute_traditional_value(portfolio_trad_retire, 10)

    results.append({
        "Scenario": "Traditional (6%/yr)",
        "Year": retire_year,
        "Age": age_at_fire,
        "Portfolio (€)": portfolio_trad_retire,
        "Net FIRE Income (€)": net_retire,
        "Net Monthly (€)": net_retire / 12
    })
    results.append({
        "Scenario": "Traditional (6%/yr)",
        "Year": retire_year + 10,
        "Age": age_10_later,
        "Portfolio (€)": portfolio_trad_10,
        "Net FIRE Income (€)": net_10,
        "Net Monthly (€)": net_10 / 12
    })

    # === Crypto Scenarios ===
    for scenario in forecast_prices_2040:
        # Estimate price per coin at retirement year
        dynamic_prices = {
            coin: get_projected_price(coin, forecast_prices_2040[scenario][coin], retire_year)
            for coin in units_held
        }
        dynamic_value = sum(units_held[c] * dynamic_prices[c] for c in dynamic_prices) * eur_usd
        net_crypto = dynamic_value * withdrawal_rate * (1 - cgt_rate)

        results.append({
            "Scenario": f"{scenario} Crypto",
            "Year": retire_year,
            "Age": age_at_fire,
            "Portfolio (€)": dynamic_value,
            "Net FIRE Income (€)": net_crypto,
            "Net Monthly (€)": net_crypto / 12
        })

        # 10 Years Later
        dynamic_value_10 = dynamic_value * ((1 + trad_growth) ** 10)
        net_crypto_10 = dynamic_value_10 * withdrawal_rate * (1 - cgt_rate)

        results.append({
            "Scenario": f"{scenario} Crypto",
            "Year": retire_year + 10,
            "Age": age_10_later,
            "Portfolio (€)": dynamic_value_10,
            "Net FIRE Income (€)": net_crypto_10,
            "Net Monthly (€)": net_crypto_10 / 12
        })

    df = pd.DataFrame(results)
    df_display = df.copy()
    format_cols = ["Portfolio (€)", "Net FIRE Income (€)", "Net Monthly (€)"]
    for col in format_cols:
        df_display[col] = df_display[col].apply(lambda x: f"€{x:,.0f}")

    st.subheader("📋 Results Table")
    st.table(df_display.set_index(["Scenario", "Year"]))

    # === Chart ===
    st.subheader("📈 Visual Comparison")
    fig, ax = plt.subplots(figsize=(10, 6))
    x_labels = df["Scenario"] + " (" + df["Year"].astype(str) + ")"
    x = np.arange(len(x_labels))
    ax.bar(x, df["Net Monthly (€)"], color="orange")
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, rotation=45, ha="right")
    ax.set_ylabel("Net Monthly FIRE (€)")
    ax.set_title("Net Monthly FIRE Income by Scenario and Year")
    st.pyplot(fig)

st.markdown("""
---
✅ **Dynamic Crypto Forecasting**  
Coin prices for your retirement year are estimated as a % of 2040 prices, based on compound annual growth.

✅ **Traditional Scenario (6%)**  
Treats your current wealth as growing like a steady index fund.

✅ **Net Income**  
All monthly and annual FIRE figures are net of 33% Capital Gains Tax in Ireland.

📘 *Forecasts based on research for BTC, ETH, XRP, and LTC price targets in 2040.*
""")
