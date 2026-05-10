import streamlit as st
import pandas as pd
import mysql.connector
import plotly.express as px

# --- PAGE CONFIG ---
st.set_page_config(page_title="EjoHeza Dashboard", layout="wide")

# --- DATABASE CONNECTION ---
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",      # Your MySQL username
        password="Rootpass",  # Your MySQL password
        database="ejoheza_db"
    )

def run_query(query):
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("EjoHeza Navigation")
page = st.sidebar.selectbox("Go to", ["Executive Summary", "Data Quality", "Regional Analysis"])

# --- HEADER ---
st.title("🛡️ EjoHeza Performance Dashboard")
st.markdown("Real-time monitoring of pension scheme health and saver behavior.")

# --- LOAD DATA FOR KPIs ---
total_members = run_query("SELECT COUNT(*) as count FROM members")['count'][0]
total_savings = run_query("SELECT SUM(amount) as sum FROM contributions")['sum'][0]
mismatches = run_query("""
    SELECT COUNT(*) as count FROM (
        SELECT a.member_id FROM accounts a 
        JOIN contributions c ON a.member_id = c.member_id 
        GROUP BY a.member_id, a.reported_balance 
        HAVING ABS(a.reported_balance - SUM(c.amount)) > (a.reported_balance * 0.1)
    ) as t
""")['count'][0]

# --- DASHBOARD PAGES ---
if page == "Executive Summary":
    # Row 1: KPI Cards
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Members", f"{total_members:,}")
    col2.metric("Total Fund Value", f"RWF {total_savings:,.0f}")
    col3.metric("Data Integrity Alerts", mismatches, delta="-5%", delta_color="inverse")

    # Row 2: Monthly Trends (Plotly Line Chart)
    st.subheader("Monthly Contribution Trends")
    trend_query = "SELECT date, amount FROM contributions"
    df_trends = run_query(trend_query)
    df_trends['date'] = pd.to_datetime(df_trends['date'])
    df_monthly = df_trends.set_index('date').resample('ME').sum().reset_index()
    
    fig_line = px.line(df_monthly, x='date', y='amount', title="Savings Velocity Over Time", template="plotly_white")
    st.plotly_chart(fig_line, use_container_width=True)

    # Row 3: Demographics
    st.subheader("Demographic Breakdown")
    demo_query = """
        SELECT age, gender FROM members m 
        JOIN contributions c ON m.member_id = c.member_id
    """
    df_demo = run_query(demo_query)
    # Binning in Python for flexibility
    df_demo['age_group'] = pd.cut(df_demo['age'], bins=[0,25,35,45,60,100], labels=['<25','25-35','35-45','45-60','60+'])
    demo_summary = df_demo.groupby(['age_group', 'gender']).size().reset_index(name='Frequency')
    
    fig_bar = px.bar(demo_summary, x='age_group', y='Frequency', color='gender', barmode='group')
    st.plotly_chart(fig_bar, use_container_width=True)

elif page == "Data Quality":
    st.subheader("Accounts with Balance Discrepancies")
    st.write("The following accounts show a variance > 10% between reported balance and transaction history.")
    mismatch_detail = run_query("""
        SELECT a.member_id, a.reported_balance, SUM(c.amount) as actual_total
        FROM accounts a
        JOIN contributions c ON a.member_id = c.member_id
        GROUP BY a.member_id, a.reported_balance
        HAVING ABS(a.reported_balance - SUM(c.amount)) > (a.reported_balance * 0.1)
    """)
    st.dataframe(mismatch_detail, use_container_width=True)

elif page == "Regional Analysis":
    st.subheader("Inactivity Rate by Region")
    # This replicates your "30% Inactivity" SQL logic
    regional_query = """
        SELECT region, 
        COUNT(member_id) as total,
        SUM(CASE WHEN last_date < '2024-01-01' THEN 1 ELSE 0 END) as inactive
        FROM (
            SELECT m.member_id, m.region, MAX(c.date) as last_date
            FROM members m
            LEFT JOIN contributions c ON m.member_id = c.member_id
            GROUP BY m.member_id, m.region
        ) t GROUP BY region
    """
    df_reg = run_query(regional_query)
    df_reg['Inactivity %'] = (df_reg['inactive'] / df_reg['total']) * 100
    
    fig_reg = px.bar(df_reg, x='region', y='Inactivity %', color='Inactivity %', 
                     color_continuous_scale='Reds', title="Regional Churn Risk")
    st.plotly_chart(fig_reg, use_container_width=True)