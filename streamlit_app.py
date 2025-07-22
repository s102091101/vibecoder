import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Crypto FIRE Calculator", layout="centered")
st.title("🚀 Crypto FIRE Calculator — Dynamic Retirement & 10-Year Projections")

st.write(
    "Estimate your crypto retirement income under both traditional asset and crypto-specific forecast scenarios, for your retirement year and 10 years later. All FIRE net figures account for Irish Capital Gains Tax."
)

st.header("User Input")
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

st.header("Optional: Additional Euro Savings")
euro_balance = st.number_input("Traditional EUR Savings (Optional)", min_value=0.0, value=0.0, step=1000.0)

withdrawal_rate = 0.04
cgt_rate = 0.33
current_year = 2025

traditional_growth = 0.06  # 6% per year compounding for traditional scenario

crypto_prices_2040 = {
    "Conservative": {"BTC": 247794, "ETH": 4592, "XRP": 76, "LTC": 237},
    "Moderate":     {"BTC": 850000, "ETH": 92704, "XRP": 100, "LTC": 926},
    "Optimistic":   {"BTC": 2320693, "ETH": 117501, "XRP": 1456, "LTC": 2955}
}

# Estimate present crypto value in euro for traditional scenario
dummy_prices_now = {"BTC": 65000, "ETH": 3500, "XRP": 0.50, "LTC": 80}
total_crypto_value_now = sum(units_held[c] * dummy_prices_now[c] for c in units_held)
full_balance_now = total_crypto_value_now + euro_balance

years_to_retire = retire_year - current_year
years_10_later = years_to_retire + 10

if st.button("Calculate FIRE Scenarios"):
    if years_to_retire < 0:
        st.error("Please choose a retirement year in the future.")
    else:
        st.subheader(f"Results: Retirement in {retire_year} (Age {age + years_to_retire})")
        st.subheader(f"Projection 10 Years After FIRE: {retire_year + 10} (Age {age + years_10_later})")

        def calc_fi(balance, yrs):
            pf = balance * ((1 + traditional_growth) ** yrs)
            gross = pf * withdrawal_rate
            net = gross * (1 - cgt_rate)
            return pf, gross, net, net / 12

        trad_pf, trad_gross, trad_net, trad_monthly = calc_fi(full_balance_now, years_to_retire)
        trad10_pf, trad10_gross, trad10_net, trad10_monthly = calc_fi(trad_pf, 10)

        def crypto_port_eur(units, scenario):
            usd = sum(units[c] * crypto_prices_2040[scenario][c] for c in units)
            return usd * 0.86  # USD to EUR

        scenarios = []
        # Traditional scenario — retirement year
        scenarios.append({
            "Scenario": "Traditional Asset Growth (6%/yr)",
            "Year": retire_year,
            "Portfolio (€)": trad_pf,
            "Net Yearly FIRE (€)": trad_net,
            "Net Monthly FIRE (€)": trad_monthly,
            "Age": age + years_to_retire
        })
        # Traditional scenario — 10 years later
        scenarios.append({
            "Scenario": "Traditional Asset Growth (6%/yr)",
            "Year": retire_year + 10,
            "Portfolio (€)": trad10_pf,
            "Net Yearly FIRE (€)": trad10_net,
            "Net Monthly FIRE (€)": trad10_monthly,
            "Age": age + years_10_later
        })

        # Crypto scenarios — retirement year and 10 years later
        for label in ["Conservative", "Moderate", "Optimistic"]:
            val_eur = crypto_port_eur(units_held, label)
            gross = val_eur * withdrawal_rate
            net = gross * (1 - cgt_rate)
            # At retirement
            scenarios.append({
                "Scenario": f"Crypto {label}",
                "Year": retire_year,
                "Portfolio (€)": val_eur,
                "Net Yearly FIRE (€)": net,
                "Net Monthly FIRE (€)": net / 12,
                "Age": age + years_to_retire
            })
            # 10 years after retirement (with traditional growth assumption post-retirement)
            val_eur_10 = val_eur * ((1 + traditional_growth) ** 10)
            gross10 = val_eur_10 * withdrawal_rate
            net10 = gross10 * (1 - cgt_rate)
            scenarios.append({
                "Scenario": f"Crypto {label}",
                "Year": retire_year + 10,
                "Portfolio (€)": val_eur_10,
                "Net Yearly FIRE (€)": net10,
                "Net Monthly FIRE (€)": net10 / 12,
                "Age": age + years_10_later
            })

        df = pd.DataFrame(scenarios)
        df_formatted = df.copy()
        showcols = ["Portfolio (€)", "Net Yearly FIRE (€)", "Net Monthly FIRE (€)"]
        for col in showcols:
            df_formatted[col] = df_formatted[col].apply(lambda x: f"€{x:,.0f}")
        st.table(df_formatted.set_index(["Scenario", "Year"]))

        # Visualization
        fig, ax = plt.subplots(figsize=(12, 6))
        groups = df["Scenario"].unique()
        years = sorted(df["Year"].unique())
        width = 0.35
        x = np.arange(len(groups))
        # Plot portfolio and net monthly side-by-side for each year
        for i, yr in enumerate(years):
            dx = (i - 0.5) * width
            vals = df[df["Year"] == yr]["Portfolio (€)"]
            ax.bar(x + dx, vals, width=width, label=f"Portfolio {yr}" if i == 0 else "")
            vals_income = df[df["Year"] == yr]["Net Monthly FIRE (€)"]
            ax.bar(x + dx, vals_income, width=width, label=f"Net Monthly FIRE {yr}" if i == 1 else "", alpha=0.5)
        ax.set_xticks(x)
        ax.set_xticklabels(groups, rotation=45, ha="right")
        ax.set_ylabel("Euro (€)")
        ax.set_title("Portfolio Value and Net Monthly FIRE Income: Retirement Year vs. 10 Years Later")
        ax.legend(loc="upper left", bbox_to_anchor=(1, 1))
        plt.tight_layout()
        st.pyplot(fig)

st.markdown("""
---
### Scenario Definitions

- **Traditional Asset Growth (6%/yr):**
  - Treats your entire portfolio as if invested in a steady global index fund (6% per year).
- **Crypto Conservative:**
  - Uses cautious 2040 analyst forecasts for BTC, ETH, XRP, and LTC prices.
- **Crypto Moderate:**
  - Uses widely published consensus mid-range 2040 coin price predictions.
- **Crypto Optimistic:**
  - Uses published upper-end, bullish 2040 crypto forecasts.

All net figures reflect 4% FIRE withdrawals minus 33% Irish CGT, using 2025 forecast prices and rates. This tool is for education only, not advice.
""")


