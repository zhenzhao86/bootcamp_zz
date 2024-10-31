import streamlit as st
import pandas as pd
import openai

def load_and_preprocess_data():
    # Load all CSV files in the data folder (same as in general_query)
    all_files = glob.glob(os.path.join("data", "*.csv"))
    df_list = [pd.read_csv(file) for file in all_files]
    df = pd.concat(df_list, ignore_index=True)
    
    # Data cleaning and transformation
    df['month'] = pd.to_datetime(df['month'], format='%Y-%m')
    df['resale_price'] = pd.to_numeric(df['resale_price'], errors='coerce')
    return df

def affordability_calculator(df):
    st.title("HDB Resale Housing Affordability Calculator")
    
    # Collect user inputs
    income = st.number_input("Enter your monthly household income (SGD)", min_value=0)
    savings = st.number_input("Enter your total savings (CPF + cash) (SGD)", min_value=0)
    debts = st.number_input("Enter your monthly debts (e.g., loans) (SGD)", min_value=0)
    loan_tenure = st.number_input("Enter the loan tenure in years", min_value=1, max_value=30)
    target_town = st.selectbox("Select the town for the target flat", df['town'].unique())
    flat_type = st.selectbox("Select flat type", df['flat_type'].unique())
    
    # Loan and affordability calculations
    interest_rate = 0.025
    max_loan = (income - debts) * 12 * loan_tenure * (1 - interest_rate)
    affordable_price = max_loan + savings

    # Calculate average price of target flat in the selected town
    target_df = df[(df['town'] == target_town) & (df['flat_type'] == flat_type)]
    avg_resale_price = target_df['resale_price'].mean()

    if st.button("Calculate Affordability"):
        if pd.isna(avg_resale_price):
            st.write("No data available for the selected flat type and town.")
        else:
            st.write(f"Average resale price for a {flat_type} flat in {target_town}: ${avg_resale_price:,.2f}")
            st.write(f"Based on your inputs, you can afford a flat worth approximately ${affordable_price:,.2f}.")

            # Determine affordability and display result
            if affordable_price >= avg_resale_price:
                st.success("Congratulations! You can afford this flat based on your inputs.")
            else:
                st.warning("The target flat may not be affordable based on your inputs.")

    # Optionally, provide LLM assistance for further questions
    user_query = st.text_input("Ask a question about affordability in your situation")
    if user_query:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an assistant that answers questions based on housing data prices and affordability. "
                        "You have access to a pandas DataFrame called 'df' that contains information "
                        "about HDB resale transactions, including columns for 'town', 'flat_type', 'resale_price', "
                        "and 'floor_area_sqm'. You can query the DataFrame using Python pandas syntax to filter, aggregate, "
                        "or analyze data as needed to answer the user's queries about affordability."
                    )
                },
                {"role": "user", "content": f"Use the data to help answer: {user_query}"}
            ]
        )
        st.write(response['choices'][0]['message']['content'])

# Load data and run the calculator
df = load_and_preprocess_data()
affordability_calculator(df)
