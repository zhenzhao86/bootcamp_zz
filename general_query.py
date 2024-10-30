import openai
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import glob
import os

# Initialize OpenAI API key
openai.api_key = st.secrets.api_key

# Step 1: Load and concatenate CSV files from the data folder
def load_and_preprocess_data():
    all_files = glob.glob(os.path.join("data", "*.csv"))
    df_list = [pd.read_csv(file) for file in all_files]
    df = pd.concat(df_list, ignore_index=True)
    
    df['month'] = pd.to_datetime(df['month'], format='%Y-%m')
    df['resale_price'] = pd.to_numeric(df['resale_price'], errors='coerce')
    df['floor_area_sqm'] = pd.to_numeric(df['floor_area_sqm'], errors='coerce')
    df['remaining_lease_years'] = df['remaining_lease'].str.extract(r'(\d+)').astype(float)
    df['lease_commence_date'] = pd.to_datetime(df['lease_commence_date'], format='%Y').dt.year
    
    return df

# Step 2: Define functions to handle specific queries
def calculate_average_resale_price(df):
    avg_price = df['resale_price'].mean()
    return f"The average resale price of HDB flats is SGD {avg_price:,.2f}."

def plot_resale_price_trend(df):
    monthly_trend = df.groupby(df['month'].dt.to_period('M')).resale_price.mean()
    monthly_trend.index = monthly_trend.index.to_timestamp()
    
    fig, ax = plt.subplots()
    monthly_trend.plot(ax=ax, color='blue', title="Average Resale Price Trend Over Time")
    ax.set_xlabel("Month")
    ax.set_ylabel("Average Resale Price (SGD)")
    
    st.pyplot(fig)

# Step 3: Define main function to handle general queries
def general_query():
    st.title("General Query on HDB Resale Market")
    
    # Load and preprocess the data
    df = load_and_preprocess_data()
    st.write("Data loaded successfully with the following columns:")
    st.write(df.head())

    user_query = st.text_input("Enter your query about HDB resale trends or prices, based on the dataset above:")
    st.write("E.g. Plot the resale price trend from 2017 to 2020")

    if st.button("Submit"):
        # Directly handle queries with specific keywords
        if "average resale price" in user_query.lower():
            st.write(calculate_average_resale_price(df))
        
        elif "price trend" in user_query.lower():
            plot_resale_price_trend(df)
        
        elif "town average price" in user_query.lower():
            town_avg_prices = df.groupby('town')['resale_price'].mean().sort_values(ascending=False)
            st.write("Average resale prices by town:")
            st.write(town_avg_prices)
        
        else:
            # If no specific keyword matches, fall back to OpenAI LLM
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an assistant for analyzing HDB resale housing data in Singapore. "
                            "You have access to a pandas DataFrame called 'df' that contains information "
                            "about HDB resale transactions, including columns for 'month', 'town', 'flat_type', "
                            "'block', 'street_name', 'storey_range', 'floor_area_sqm', 'flat_model', "
                            "'lease_commence_date', 'remaining_lease_years', and 'resale_price'. "
                            "You can query the DataFrame using Python pandas syntax to filter, aggregate, "
                            "or analyze data as needed to answer the user's queries."
                        )
                    },
                    {"role": "user", "content": f"Use the HDB resale data provided to answer: {user_query}"}
                ]
            )
            st.write(response['choices'][0]['message']['content'])
