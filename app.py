import streamlit as st
import duckdb
import pandas as pd

st.set_page_config(page_title="Mandi Arbitrage Engine", layout="wide")
st.title("🚛 Cross-Market Arbitrage Spread")
st.markdown("Analyze price discrepancies across all reporting Mandis for a specific date.")

agri = "2025.parquet"

@st.cache_data
def get_commodities():
    query = f"SELECT DISTINCT Commodity FROM '{agri}' ORDER BY Commodity"
    return duckdb.sql(query).df()['Commodity'].tolist()

st.sidebar.header("1. Select Commodity")
selected_commodity = st.sidebar.selectbox("Commodity", get_commodities())

@st.cache_data
def get_available_dates(commodity):
    # DuckDB will group the dates and only return ones with 2+ unique markets
    query = f"""
    SELECT CAST(Arrival_Date AS DATE) AS Date
    FROM '{agri}'
    WHERE Commodity = '{commodity}'
    GROUP BY CAST(Arrival_Date AS DATE)
    HAVING COUNT(DISTINCT Market) > 1
    ORDER BY Date DESC
    """
    return duckdb.sql(query).df()['Date'].tolist()

available_dates = get_available_dates(selected_commodity)

if not available_dates:
    st.warning("No data found for this commodity.")
else:
    st.sidebar.header("2. Select Trading Date")
    selected_date = st.sidebar.selectbox("Date", available_dates)

    @st.cache_data
    def load_market_spread(commodity, date):
        query = f"""
        SELECT 
            Market, 
            State, 
            Min_Price, 
            Max_Price, 
            Modal_Price
        FROM '{agri}'
        WHERE Commodity = '{commodity}' 
          AND CAST(Arrival_Date AS DATE) = '{date}'
        ORDER BY Modal_Price ASC
        """
        return duckdb.sql(query).df()

    df_spread = load_market_spread(selected_commodity, selected_date)

    if len(df_spread) < 2:
        st.warning(f"Only {len(df_spread)} market(s) reported {selected_commodity} on {selected_date}. Cannot calculate arbitrage spread.")
        st.dataframe(df_spread)
    else:
        # Calculate Arbitrage Metrics
        cheapest_row = df_spread.iloc[0]
        most_expensive_row = df_spread.iloc[-1]
        max_profit = most_expensive_row['Modal_Price'] - cheapest_row['Modal_Price']

        # Top Level Summary
        st.subheader(f"Arbitrage Summary for {selected_commodity} on {selected_date}")
        col1, col2, col3 = st.columns(3)
        col1.metric("Buy (Lowest Price)", f"₹{cheapest_row['Modal_Price']}", cheapest_row['Market'], delta_color="inverse")
        col2.metric("Sell (Highest Price)", f"₹{most_expensive_row['Modal_Price']}", most_expensive_row['Market'])
        col3.metric("Max Gross Margin", f"₹{max_profit}", "Profit per Quintal")

        # Visual Spread Comparison
        st.subheader("Price Comparison Across All Markets")
        # Streamlit bar_chart is simple, but setting Market as index makes it look good
        st.bar_chart(df_spread.set_index('Market')['Modal_Price'])

        # Detailed Profit Table
        st.subheader("Potential Arbitrage Routes")
        st.markdown(f"**Baseline:** Buying at the cheapest market ({cheapest_row['Market']} at ₹{cheapest_row['Modal_Price']})")
        
        # Calculate potential profit if sold at each market
        df_spread['Potential_Profit'] = df_spread['Modal_Price'] - cheapest_row['Modal_Price']
        
        # Format the table for the operations team
        df_routes = df_spread[['Market', 'State', 'Modal_Price', 'Potential_Profit']].copy()
        df_routes = df_routes.sort_values(by='Potential_Profit', ascending=False)
        
        st.dataframe(
            df_routes.style.highlight_max(subset=['Potential_Profit'], color='lightgreen'), 
            use_container_width=True
        )