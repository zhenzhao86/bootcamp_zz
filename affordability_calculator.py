import streamlit as st
import pandas as pd
import openai
import glob  # Import glob to locate CSV files
import os

def load_and_preprocess_data():
    # Load all CSV files in the data folder (same as in general_query)
    all_files = glob.glob(os.path.join("data", "*.csv"))
    df_list = [pd.read_csv(file) for file in all_files]
    df = pd.concat(df_list, ignore_index=True)
    
    # Data cleaning and transformation
    df['month'] = pd.to_datetime(df['month'], format='%Y-%m')
    df['resale_price'] = pd.to_numeric(df['resale_price'], errors='coerce')
    
    # Filter data for 2023 and 2024
    df = df[df['month'].dt.year.isin([2023, 2024])]
    return df

def affordability_calculator():
    st.title("HDB Resale Housing Affordability Calculator")
    st.image("image/hdb_afford.jpg", width=200, caption="Housing Calculator")
    st.write("This feature will consider recent flats (in 2023-2024) of your selected type in the selected town.")
    df = load_and_preprocess_data()
    
    # Collect user inputs
    income = st.number_input("Enter your monthly household income (SGD)", min_value=0)
    savings = st.number_input("Enter your total savings (CPF + cash) (SGD)", min_value=0)
    debts = st.number_input("Enter your monthly debts (e.g., loans) (SGD)", min_value=0)
    loan_tenure = st.number_input("Enter the loan tenure you expect to take (in years)", min_value=1, max_value=30)
    target_town = st.selectbox("Select the town for the target flat", df['town'].unique())
    flat_type = st.selectbox("Select flat type", df['flat_type'].unique())
    
    # Loan and affordability calculations using HDB loan
    interest_rate = 0.026
    max_loan = (income - debts) * 12 * loan_tenure * (1 - interest_rate)
    affordable_price = max_loan + savings

    # Filtered data for target flat type and town
    target_df = df[(df['town'] == target_town) & (df['flat_type'] == flat_type)]
    avg_resale_price = target_df['resale_price'].mean()

    if st.button("Calculate Affordability"):
        if pd.isna(avg_resale_price):
            st.write("No data available for the selected flat type and town.")
        else:
            st.write(f"Average resale price for a {flat_type} flat in {target_town} (from 2023-2024): ${avg_resale_price:,.2f}")
            st.write(f"Based on your inputs, you can afford a flat worth approximately ${affordable_price:,.2f}.")

            # Determine affordability and display result
            if affordable_price >= avg_resale_price:
                st.success("Congratulations! You can afford this flat based on your inputs, assuming an HDB loan of 2.6%. Please wait (~30s) while we give you more personalized advice...")
            else:
                st.warning("The target flat may not be affordable based on your inputs, assuming an HDB loan of 2.6%. Please wait (~30s) while we give you more personalized advice...")

            # Generate personalized advice using LLM
            user_query = (
                f"My monthly income is ${income}, with total savings of ${savings}, and monthly debts of ${debts}. "
                f"I want to buy a {flat_type} in {target_town}. The average price is around ${avg_resale_price:.2f}. "
                f"I can afford up to ${affordable_price:.2f}. Can you give me advice on how I could afford this flat?"
            )
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a financial advisor specializing in housing affordability. "
                            "Provide advice based on the user's monthly income, savings, debts, loan tenure, "
                            "target town, flat type, and the average resale price of the chosen flat. "
                            "Consider strategies such as increasing savings, adjusting the loan tenure, or other approaches "
                            "that may help the user afford the desired flat."
                        )
                    },
                    {"role": "user", "content": user_query}
                ]
            )
            st.write(response['choices'][0]['message']['content'])
