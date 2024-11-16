import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from prophet import Prophet
import matplotlib.pyplot as plt

# Load and preprocess data function
@st.cache_data
def load_data(file):
    df = pd.read_excel(file)
    df.columns = df.columns.str.strip()
    return df

# Function to detect anomalies
def detect_anomalies(df):
    model = IsolationForest(contamination=0.05, random_state=42)
    df['Anomaly'] = model.fit_predict(df[['Bill Amount']])
    anomalies = df[df['Anomaly'] == -1]
    return anomalies

# Forecast future revenue
def forecast_revenue(df):
    df['Date'] = pd.to_datetime(df['Date'])
    revenue_data = df[['Date', 'Bill Amount']].rename(columns={"Date": "ds", "Bill Amount": "y"})
    model = Prophet()
    model.fit(revenue_data)
    future = model.make_future_dataframe(periods=30)  # Forecast for next 30 days
    forecast = model.predict(future)
    return forecast

# Main summary page
def main_summary(df):
    st.header("Financial Data Summary")
    st.write("### Dataset Overview")
    st.write(df.head())

    # Forecast revenue
    if 'Date' in df.columns and 'Bill Amount' in df.columns:
        forecast = forecast_revenue(df)
        st.write("### Revenue Forecast for Next Month")
        fig, ax = plt.subplots()
        ax.plot(forecast['ds'], forecast['yhat'], label="Predicted Revenue")
        ax.set_title("Revenue Forecast")
        ax.set_xlabel("Date")
        ax.set_ylabel("Revenue")
        st.pyplot(fig)

# Partner-specific details page
def partner_details(df):
    st.header("Partner-Specific Financial Details")
    partners = df['Partner'].unique()
    selected_partner = st.selectbox("Select a Partner", options=partners)
    partner_data = df[df['Partner'] == selected_partner]

    # Detect anomalies for selected partner
    anomalies = detect_anomalies(partner_data)
    st.write("### Anomalies in Partner Data")
    st.write(anomalies[['Date', 'Bill Amount']])

    # Plot billing trends
    if 'Date' in partner_data.columns and 'Bill Amount' in partner_data.columns:
        fig, ax = plt.subplots()
        ax.plot(partner_data['Date'], partner_data['Bill Amount'], label='Bill Amount')
        ax.set_title(f"Billing Trends for {selected_partner}")
        ax.set_xlabel("Date")
        ax.set_ylabel("Bill Amount")
        st.pyplot(fig)

# Transaction records page
def transaction_records(df):
    st.header("Transaction Records")
    st.write("Filter transactions based on date range or specific partner details.")

    # Display transactions
    st.write(df)

# Main application function
def main():
    st.sidebar.title("Navigation")
    pages = {
        "Main Summary": main_summary,
        "Partner-Specific Details": partner_details,
        "Transaction Records": transaction_records
    }

    uploaded_file = st.sidebar.file_uploader("Upload your Excel file", type="xlsx")
    if uploaded_file:
        df = load_data(uploaded_file)
        page = st.sidebar.radio("Go to", list(pages.keys()))
        pages[page](df)
    else:
        st.sidebar.write("Please upload a file to proceed.")

if __name__ == "__main__":
    main()
