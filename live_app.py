import pandas as pd
import streamlit as st
import duckdb
import os

# --- Streamlit App Setup ---
st.set_page_config(page_title="Mandi Arbitrage Engine", layout="wide")
st.title("🚛 Cross-market Arbitrage Spread")
st.markdown("Analyze price discrepancies across all reporting Mandis for a specific date.")

agri_file = "live_data.json"

# Check if data exists before running the app
if not os.path.exists(agri_file):
    st.error(f"Data file '{agri_file}' not found. Please run 'python fetch_data.py' first.")
    st.stop()

conn = duckdb.connect()

@st.cache_data
def get_commodities():
    query = f"SELECT DISTINCT commodity FROM read_json_auto('{agri_file}') ORDER BY commodity"
    return conn.execute(query).df()['commodity'].tolist()

st.sidebar.header("1. Select commodity")
try:
    commodities = get_commodities()
    selected_commodity = st.sidebar.selectbox("Commodity", commodities)
except Exception as e:
    st.error(f"Error loading data. Details: {e}")
    st.stop()

@st.cache_data
def get_available_dates(commodity):
    query = f"""
    SELECT CAST(strptime(arrival_date, '%d/%m/%Y') AS DATE) AS Date
    FROM read_json_auto('{agri_file}')
    WHERE commodity = '{commodity}'
    GROUP BY Date
    HAVING COUNT(DISTINCT market) > 1
    ORDER BY Date DESC
    """
    return conn.execute(query).df()['Date'].tolist()

available_dates = get_available_dates(selected_commodity)

if not available_dates:
    st.warning("No data found for this commodity, or not enough markets to compare (need at least 2).")
else:
    st.sidebar.header("2. Select Trading Date")
    selected_date = st.sidebar.selectbox("Date", available_dates)

    @st.cache_data
    def load_market_spread(commodity, date):
        query = f"""
        SELECT 
            market, 
            state, 
            min_price, 
            max_price, 
            modal_price
        FROM read_json_auto('{agri_file}')
        WHERE commodity = '{commodity}' 
          AND CAST(strptime(arrival_date, '%d/%m/%Y') AS DATE) = '{date}'
        ORDER BY CAST(modal_price AS FLOAT) ASC
        """
        return conn.execute(query).df()

    df_spread = load_market_spread(selected_commodity, selected_date)

    # Convert prices to numeric
    df_spread['modal_price'] = pd.to_numeric(df_spread['modal_price'])

    if len(df_spread) < 2:
        st.warning(f"Only {len(df_spread)} market(s) reported {selected_commodity} on {selected_date}. Cannot calculate arbitrage.")
        st.dataframe(df_spread)
    else:
        # Metrics
        cheapest_row = df_spread.iloc[0]
        most_expensive_row = df_spread.iloc[-1]
        max_profit = most_expensive_row['modal_price'] - cheapest_row['modal_price']

        # Top Summary
        st.subheader(f"Arbitrage Summary for {selected_commodity} on {selected_date}")
        col1, col2, col3 = st.columns(3)
        col1.metric("Buy (Lowest Price)", f"₹{cheapest_row['modal_price']}", cheapest_row['market'], delta_color="inverse")
        col2.metric("Sell (Highest Price)", f"₹{most_expensive_row['modal_price']}", most_expensive_row['market'])
        col3.metric("Max Gross Margin", f"₹{max_profit}", "Profit per Quintal")

        # Chart
        st.subheader("Price Comparison Across All Markets")
        st.bar_chart(df_spread.set_index('market')['modal_price'])

        # Detailed Table
        st.subheader("Potential Arbitrage Routes")
        st.markdown(f"**Baseline:** Buying at the cheapest market ({cheapest_row['market']} at ₹{cheapest_row['modal_price']})")
        
        df_spread['Potential_Profit'] = df_spread['modal_price'] - cheapest_row['modal_price']
        df_routes = df_spread[['market', 'state', 'modal_price', 'Potential_Profit']].copy()
        df_routes = df_routes.sort_values(by='Potential_Profit', ascending=False)
        
        st.dataframe(
            df_routes.style.highlight_max(subset=['Potential_Profit'], color='lightgreen'), 
            use_container_width=True
        )