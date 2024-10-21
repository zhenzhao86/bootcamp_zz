import streamlit as st
import pandas as pd

def affordability_calculator():
    st.title("HDB Resale Housing Affordability Calculator")
    
    # Collect user inputs
    income = st.number_input("Enter your monthly household income", min_value=0)
    savings = st.number_input("Enter your total savings (CPF + cash)", min_value=0)
    debts = st.number_input("Enter your monthly debts (e.g., loans)", min_value=0)
    loan_tenure = st.number_input("Enter the loan tenure in years", min_value=1, max_value=30)

    # Assumed interest rate and loan eligibility
    interest_rate = 0.025
    max_loan = (income - debts) * 12 * loan_tenure * (1 - interest_rate)

    # Affordable house price calculation
    affordable_price = max_loan + savings
    
    # Show the result
    if st.button("Calculate Affordability"):
        st.write(f"Based on your inputs, you can afford an HDB resale flat worth approximately ${affordable_price:,.2f}.")
