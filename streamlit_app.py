import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Crypto FIRE Calculator", layout="centered")
st.title("Crypto FIRE Calculator")

# --- Add this at the top after .title() or wherever you want a FIRE-style banner ---

st.markdown(
    """
    <div style="display: flex; align-items: center; justify-content: center; font-size:3em; gap:18px; margin-top:10px; margin-bottom:10px;">

        Crypto FIRE Journey
    
    </div>
    <div style="display: flex; align-items: center; justify-content: center; font-size:1.6em; gap:16px;">
       
       Retire Early • Burn Bright • Slay Risk
   
    </div>
    """,
    unsafe_allow_html=True
)

# --- Insert themed images ---
image_files = [
    "fire.png",
    "firebtc.png",
    "fireltc.png",
    "fireeth.png",
    "firexrp.png"
]

columns = st.columns(len(image_files))
for idx, (col, img) in enumerate(zip(columns, image_files)):
    with col:
        if img == "fire.png":
            st.image(img, width=65, caption="General FIRE")
        elif img == "firebtc.png":
            st.image(img, width=65, caption="Bitcoin FIRE")
        elif img == "fireltc.png":
            st.image(img, width=65, caption="Litecoin FIRE")
        elif img == "fireeth.png":
            st.image(img, width=65, caption="Ethereum FIRE")
        elif img == "firexrp.png":
            st.image(img, width=65, caption="XRP FIRE")

st.write("""
Estimate your crypto retirement income using dynamic growth models, compared with your personal FIRE target.
This tool now includes advanced Bitcoin valuation signals: Stock-to-Flow (S2F), Rainbow Chart, and Pi Cycle Top.
All results forecast your portfolio and net withdrawal for your selected retirement year and ten years later, including Irish CGT (33%).
""")

# User inputs
st.header("Basic Information and Spending")
col1, col2 = st.columns(2)
with col1:
    age = st.number_input("Current Age", min_value=18, max_value=99, value=40)
with col2:
    retire_year = st.number_input("Target Retirement Year", min_value=2025, max_value=2100, value=2035)

st.header("Weekly Spending")
weekly_exp = st.number_input(
    "Weekly Expenditure (€)",
    value=1000.0,
    step=10.0,
    help="Based on CSO average household budget (2025)"
)

annual_expenses = weekly_exp * 52
fire_number = annual_expenses * 25
fire_monthly_requirement = annual_expenses / 12

st.markdown(f"""
**Annual Expenses:** €{annual_expenses:,.0f}  
**FIRE Number (Expenses × 25):** €{fire_number:,.0f}  
**Required Net Monthly FIRE Income:** €{fire_monthly_requirement:,.0f}
""")

# Portfolio
st.header("Portfolio Holdings")
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

def calculate_fire_year(start_value, growth_rate, fire_target, start_year, start_age):
    year = start_year
    age = start_age
    value = start_value
    while year <= 2100:
        if value >= fire_target:
            return year, age
        value *= (1 + growth_rate)
        year += 1
        age += 1
    return None, None

if st.button("Calculate FIRE Scenarios"):
    results = []
    current_value = sum(units_held[c] * current_prices[c] for c in units_held)
    full_balance_now = current_value + eur_savings

    # Traditional scenario
    trad_value_ret, trad_income_ret = compute_trad_projection(full_balance_now, years_to_retire)
    results.append({
        "Scenario": "Traditional (6%)",
        "Year": retire_year,
        "Age": age_at_retire,
        "Portfolio (€)": trad_value_ret,
        "Net FIRE Income (€)": trad_income_ret,
        "Net Monthly (€)": trad_income_ret / 12
    })
    trad_value_10, trad_income_10 = compute_trad_projection(trad_value_ret, 10)
    results.append({
        "Scenario": "Traditional (6%)",
        "Year": retire_year + 10,
        "Age": age_10_years,
        "Portfolio (€)": trad_value_10,
        "Net FIRE Income (€)": trad_income_10,
        "Net Monthly (€)": trad_income_10 / 12
    })

    # Crypto scenarios
    for label, prices_2040 in forecast_prices_2040.items():
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

    df = pd.DataFrame(results)

    # Calculate FIRE year (from current year/balance, not just retirement)
    st.subheader("Year You Reach Your FIRE Target")
    fire_results = []
    scenario_growth_rates = {
        "Traditional (6%)": trad_growth,
    }
    for label, prices_2040 in forecast_prices_2040.items():
        rates = []
        for coin in units_held:
            price_2040 = prices_2040[coin]
            price_now = current_prices[coin]
            r = (price_2040 / price_now) ** (1 / (2040-2025)) - 1
            rates.append(r)
        avg_rate = np.mean(rates)
        scenario_growth_rates[f"{label} Crypto"] = avg_rate

    scenario_initials = {
        "Traditional (6%)": full_balance_now,
    }
    for label, prices_2040 in forecast_prices_2040.items():
        value_now = sum(units_held[c] * current_prices[c] for c in units_held) * conversion_rate + eur_savings
        scenario_initials[f"{label} Crypto"] = value_now

    for scenario, growth in scenario_growth_rates.items():
        fire_year, fire_age = calculate_fire_year(
            start_value=scenario_initials[scenario],
            growth_rate=growth,
            fire_target=fire_number,
            start_year=current_year,
            start_age=age
        )
        fire_results.append({
            "Scenario": scenario,
            "FIRE Attained Year": fire_year if fire_year else "Not reached",
            "Age at FIRE": fire_age if fire_age else "N/A",
            "Starting Year": current_year
        })

    fire_df = pd.DataFrame(fire_results)
    st.table(fire_df.set_index("Scenario"))

    # Format for table
    df_fmt = df.copy()
    for col in ["Portfolio (€)", "Net FIRE Income (€)", "Net Monthly (€)"]:
        df_fmt[col] = df_fmt[col].apply(lambda x: f"€{x:,.0f}")
    st.subheader("Results Table")
    st.table(df_fmt.set_index(["Scenario", "Year"]))

    # Visual: Net Monthly FIRE Income against FIRE requirement
    st.subheader("Net Monthly FIRE Income vs. Required Target")
    x_labels = df["Scenario"] + " (" + df["Year"].astype(str) + ")"
    x = np.arange(len(x_labels))
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.bar(x, df["Net Monthly (€)"], color="blue")
    ax.axhline(fire_monthly_requirement, color="red", linestyle="--", linewidth=2,
               label=f"Required Monthly FIRE Income: €{fire_monthly_requirement:,.0f}")
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, rotation=45, ha="right")
    ax.set_ylabel("Net Monthly FIRE Income (€)")
    ax.set_title("FIRE Income by Scenario with Target Threshold")
    ax.legend()
    plt.tight_layout()
    st.pyplot(fig)

# --- Bitcoin Signal Analysis Section ---
st.header("Advanced Bitcoin Valuation Models")

st.subheader("Stock-to-Flow Model (S2F)")
st.write("""
The Stock-to-Flow model estimates Bitcoin's value based on scarcity — the ratio of existing supply to new supply mined annually.
It historically provides price zones for market cycles and helps indicate undervaluation or overvaluation relative to stock availability.
""")

st.subheader("Rainbow Chart")
st.write("""
The Rainbow Chart uses a logarithmic regression band to show historical BTC price zones from 'fire sale' to 'maximum bubble'.
It gives context on whether current prices are below or above historical norms.
""")

st.subheader("Pi Cycle Top Indicator")
st.write("""
The Pi Cycle Top is an on-chain indicator combining two moving averages that historically signals Bitcoin market cycle tops.
It warns of likely bear markets following market peaks.
""")

# --- PDF export guidance ---

st.header("Export Your Report to PDF")

st.write("""
To save your results and charts:  
- Use your browser's “Print to PDF” function, or press “Ctrl+P” / “Cmd+P” while your results are displayed to save a full summary of your FIRE planning report, tables, charts, and Bitcoin signal notes.
- For optimal PDF appearance, hide Streamlit sidebar and use a modern browser.
""")

st.markdown("""
---
This app combines dynamic crypto and traditional asset scenario planning, advanced Bitcoin signals, and clear FIRE milestone tracking.  
Results are for planning and illustration purposes—always review major financial decisions with qualified advisors.
""")
