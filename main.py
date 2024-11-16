import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import ollama

# Load and preprocess data function
@st.cache_data
def load_data(file):
    # Read the Excel file
    df = pd.read_excel(file)
    
    # Clean column names by stripping spaces
    df.columns = df.columns.str.strip()
    
    # Convert 'Date' column to datetime, handling errors
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    # Return the cleaned dataframe
    return df

# Main summary page function
def main_summary(df):
    st.header("Financial Data Summary")
    
    # Display basic dataset info
    st.write("### Basic Dataset Information")
    st.write("Number of records:", len(df))
    st.write("Available columns:", list(df.columns))
    st.write(df.head())

    # Calculate and display summary statistics
    st.write("### Overall Summary Statistics")
    total_bill = df['Bill Amount'].sum() if 'Bill Amount' in df.columns else "N/A"
    total_received = df['Received'].sum() if 'Received' in df.columns else "N/A"
    outstanding = total_bill - total_received if total_bill != "N/A" and total_received != "N/A" else "N/A"
    
    st.write(f"Total Bill Amount: {total_bill}")
    st.write(f"Total Received: {total_received}")
    st.write(f"Outstanding Amount: {outstanding}")

    # Revenue by company
    if 'Company Name' in df.columns and 'Bill Amount' in df.columns:
        st.write("### Revenue by Company")
        company_revenue = df.groupby('Company Name')['Bill Amount'].sum().sort_values(ascending=False)
        st.write(company_revenue)
        
        # Display as a bar chart
        fig, ax = plt.subplots()
        company_revenue.plot(kind='bar', ax=ax, color='#4caf50')
        ax.set_title("Revenue by Company")
        ax.set_xlabel("Company Name")
        ax.set_ylabel("Total Revenue")
        st.pyplot(fig)

# Partner-specific financial details with comparison functionality
def partner_details(df):
    st.header("Partner-Specific Financial Details")
    
    # Select multiple partners for comparison
    partners = df['Partner'].unique()
    selected_partners = st.multiselect("Select Partners", options=partners, default=partners[:2])

    for selected_partner in selected_partners:
        partner_data = df[df['Partner'] == selected_partner]
        
        total_bill = partner_data['Bill Amount'].sum()
        received_total = partner_data['Received'].sum()
        overdue = total_bill - received_total if total_bill > 0 else 0
        collection_efficiency = (received_total / total_bill) * 100 if total_bill > 0 else 0

        # Display partner's financial summary
        st.write(f"### {selected_partner}'s Summary")
        st.write(f"Total Bill Amount: {total_bill}")
        st.write(f"Total Received: {received_total}")
        st.write(f"Overdue Amount: {overdue}")
        st.write(f"Collection Efficiency: {collection_efficiency:.2f}%")
        
        # Plot partner-specific billing trends
        if 'Date' in partner_data.columns and 'Bill Amount' in partner_data.columns:
            partner_data = partner_data.sort_values(by='Date')
            partner_data['Moving Average'] = partner_data['Bill Amount'].rolling(window=3).mean()

            fig, ax = plt.subplots()
            ax.plot(partner_data['Date'], partner_data['Bill Amount'], label='Bill Amount')
            ax.plot(partner_data['Date'], partner_data['Moving Average'], label='3-Month Moving Avg', linestyle='--')
            ax.set_title(f"Billing Trends for {selected_partner}")
            ax.set_xlabel("Date")
            ax.set_ylabel("Bill Amount")
            ax.legend()
            st.pyplot(fig)

# Financial analysis page
def financial_analysis(df):
    st.header("Firm's Financial Analysis")

    # Monthly revenue trend
    if 'Bill Amount' in df.columns and 'Date' in df.columns:
        df['Month'] = pd.to_datetime(df['Date']).dt.to_period('M')
        monthly_revenue = df.groupby('Month')['Bill Amount'].sum()
        
        fig, ax = plt.subplots()
        monthly_revenue.plot(kind='line', ax=ax, marker='o')
        ax.set_title("Monthly Revenue Trend")
        ax.set_xlabel("Month")
        ax.set_ylabel("Total Revenue")
        st.pyplot(fig)
    
    # Tax breakdown with stacked bar chart
    tax_columns = ['CGST 9%', 'SGST 9%', 'IGST 18%']
    available_taxes = [col for col in tax_columns if col in df.columns]

    if available_taxes:
        st.write("### Tax Breakdown")
        monthly_tax = df.groupby('Month')[available_taxes].sum()

        fig, ax = plt.subplots()
        monthly_tax.plot(kind='bar', stacked=True, ax=ax, color=['#6fa8dc', '#e06666', '#f6b26b'])
        ax.set_title("Tax Distribution Over Time")
        ax.set_xlabel("Month")
        ax.set_ylabel("Total Tax Amount")
        st.pyplot(fig)

    # Outstanding amount over time
    if 'Bill Amount' in df.columns and 'Received' in df.columns:
        df['Outstanding'] = df['Bill Amount'] - df['Received']
        monthly_outstanding = df.groupby('Month')['Outstanding'].sum()

        fig, ax = plt.subplots()
        monthly_outstanding.plot(kind='line', ax=ax, color='purple', marker='o')
        ax.set_title("Outstanding Amount Over Time")
        ax.set_xlabel("Month")
        ax.set_ylabel("Outstanding Amount")
        st.pyplot(fig)

# Chatbot for financial insights with comparison capability
def financial_insights_chatbot(df):
    # Extract available financial metrics from the dataset
    columns = df.columns
    total_billing = df['Bill Amount'].sum() if 'Bill Amount' in columns else "N/A"
    total_received = df['Received'].sum() if 'Received' in columns else "N/A"
    outstanding = total_billing - total_received if total_billing != "N/A" and total_received != "N/A" else "N/A"
    top_revenue_partner = df.groupby('Partner')['Bill Amount'].sum().idxmax() if 'Partner' in columns else "N/A"
    top_revenue_amount = df.groupby('Partner')['Bill Amount'].sum().max() if 'Partner' in columns else "N/A"
    cgst = df['CGST 9%'].sum() if 'CGST 9%' in columns else "N/A"
    sgst = df['SGST 9%'].sum() if 'SGST 9%' in columns else "N/A"
    igst = df['IGST 18%'].sum() if 'IGST 18%' in columns else "N/A"
    collection_efficiency = (total_received / total_billing) * 100 if total_billing != "N/A" and total_billing > 0 else "N/A"

    # Construct dynamic prompt based on available data
    user_question = st.text_input("Ask the chatbot about financial insights or comparisons between partners", "")
    if user_question:
        prompt = f"You are a financial analyst for a company dataset. Here is the financial summary based on available data:\n\n"
        
        # Add available metrics to the prompt
        if total_billing != "N/A":
            prompt += f"Total Billing Amount: {total_billing}\n"
        if total_received != "N/A":
            prompt += f"Total Received Amount: {total_received}\n"
        if outstanding != "N/A":
            prompt += f"Outstanding Amount: {outstanding}\n"
        if top_revenue_partner != "N/A" and top_revenue_amount != "N/A":
            prompt += f"Top Revenue Partner: {top_revenue_partner} with {top_revenue_amount}\n"
        if cgst != "N/A":
            prompt += f"Total CGST: {cgst}\n"
        if sgst != "N/A":
            prompt += f"Total SGST: {sgst}\n"
        if igst != "N/A":
            prompt += f"Total IGST: {igst}\n"
        if collection_efficiency != "N/A":
            prompt += f"Collection Efficiency: {collection_efficiency:.2f}%\n"

        # Append the user's question to the prompt
        prompt += f"\nNow answer this question based on the available data: {user_question}"

        # Get the response from Ollama chatbot
        response = ollama.chat(
            model="llama3.1:latest",
            messages=[{"role": "user", "content": prompt}]
        )
        response_text = response['message']['content'].strip()
        
        # Display chatbot's insight
        st.write("**Chatbot Insight:**", response_text)

# Main application
def main():
    st.sidebar.title("Navigation")
    pages = {
        "Main Summary": main_summary,
        "Partner-Specific Details": partner_details,
        "Financial Analysis": financial_analysis
    }

    uploaded_file = st.sidebar.file_uploader("Upload your Excel file", type="xlsx")
    
    if uploaded_file:
        df = load_data(uploaded_file)
        
        page = st.sidebar.radio("Go to", list(pages.keys()))
        pages[page](df)

        # Chatbot section
        st.sidebar.title("Financial Insights Chatbot")
        financial_insights_chatbot(df)
    else:
        st.write("Please upload an Excel file to continue.")

if __name__ == "__main__":
    main()
