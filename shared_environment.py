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
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    return df

# Main summary page function
def main_summary(df):
    st.header("Financial Data Summary")
    st.write("### Basic Dataset Information")
    st.write("Number of records:", len(df))
    st.write("Available columns:", list(df.columns))
    st.write(df.head())

    st.write("### Overall Summary Statistics")
    total_bill = df['Bill Amount'].sum() if 'Bill Amount' in df.columns else "N/A"
    total_received = df['Received'].sum() if 'Received' in df.columns else "N/A"
    outstanding = total_bill - total_received if total_bill != "N/A" and total_received != "N/A" else "N/A"
    st.write(f"Total Bill Amount: {total_bill}")
    st.write(f"Total Received: {total_received}")
    st.write(f"Outstanding Amount: {outstanding}")

# Partner comparison function
def partner_comparison(df):
    st.header("Compare Partners")

    partners = df['Partner'].unique()
    selected_partner1 = st.selectbox("Select Partner 1", options=partners)
    selected_partner2 = st.selectbox("Select Partner 2", options=[p for p in partners if p != selected_partner1])

    if selected_partner1 and selected_partner2:
        partner1_data = df[df['Partner'] == selected_partner1]
        partner2_data = df[df['Partner'] == selected_partner2]

        def calculate_metrics(data):
            total_bill = data['Bill Amount'].sum()
            received_total = data['Received'].sum()
            overdue = total_bill - received_total
            collection_efficiency = (received_total / total_bill) * 100 if total_bill > 0 else 0
            return total_bill, received_total, overdue, collection_efficiency

        p1_total, p1_received, p1_overdue, p1_efficiency = calculate_metrics(partner1_data)
        p2_total, p2_received, p2_overdue, p2_efficiency = calculate_metrics(partner2_data)

        st.write(f"### Comparison between {selected_partner1} and {selected_partner2}")
        st.write(f"{selected_partner1}:")
        st.write(f"- Total Bill Amount: {p1_total}")
        st.write(f"- Total Received: {p1_received}")
        st.write(f"- Outstanding Amount: {p1_overdue}")
        st.write(f"- Collection Efficiency: {p1_efficiency:.2f}%")

        st.write(f"{selected_partner2}:")
        st.write(f"- Total Bill Amount: {p2_total}")
        st.write(f"- Total Received: {p2_received}")
        st.write(f"- Outstanding Amount: {p2_overdue}")
        st.write(f"- Collection Efficiency: {p2_efficiency:.2f}%")

        # Comparative insights using the chatbot
        prompt = (
            f"Here is a comparison of financial metrics between partners {selected_partner1} and {selected_partner2}:\n"
            f"{selected_partner1}:\n"
            f" - Total Bill Amount: {p1_total}\n"
            f" - Total Received: {p1_received}\n"
            f" - Outstanding Amount: {p1_overdue}\n"
            f" - Collection Efficiency: {p1_efficiency:.2f}%\n\n"
            f"{selected_partner2}:\n"
            f" - Total Bill Amount: {p2_total}\n"
            f" - Total Received: {p2_received}\n"
            f" - Outstanding Amount: {p2_overdue}\n"
            f" - Collection Efficiency: {p2_efficiency:.2f}%\n\n"
            "Based on this data, provide insights on which partner has better financial performance and any other comparative insights you can deduce."
        )

        response = ollama.chat(
            model="llama3.1:latest",
            messages=[{"role": "user", "content": prompt}]
        )
        response_text = response['message']['content'].strip()
        st.write("**Chatbot Insight:**", response_text)

# Main application
def main():
    st.sidebar.title("Navigation")
    pages = {
        "Main Summary": main_summary,
        "Compare Partners": partner_comparison
    }

    uploaded_file = st.sidebar.file_uploader("Upload your Excel file", type="xlsx")
    
    if uploaded_file:
        df = load_data(uploaded_file)
        
        page = st.sidebar.radio("Go to", list(pages.keys()))
        st.sidebar.write("---")
        st.sidebar.write("Currently viewing:", page)
        
        pages[page](df)
        
# Run the application
if __name__ == "__main__":
    main()
