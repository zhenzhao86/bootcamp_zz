import openai
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import glob
import os

# Initialize OpenAI API key
# openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = st.secrets.api_key

# Step 1: Load and concatenate CSV files from the data folder
def load_and_preprocess_data():
    # Load all CSV files in the data folder
    all_files = glob.glob(os.path.join("data", "*.csv"))
    df_list = [pd.read_csv(file) for file in all_files]
    
    # Concatenate all CSV files into a single DataFrame
    df = pd.concat(df_list, ignore_index=True)
    
    # Data cleaning and transformation
    df['month'] = pd.to_datetime(df['month'], format='%Y-%m')
    df['resale_price'] = pd.to_numeric(df['resale_price'], errors='coerce')
    df['floor_area_sqm'] = pd.to_numeric(df['floor_area_sqm'], errors='coerce')
    df['remaining_lease_years'] = df['remaining_lease'].str.extract(r'(\d+)').astype(float)
    df['lease_commence_date'] = pd.to_datetime(df['lease_commence_date'], format='%Y').dt.year
    
    return df

# Step 2: Define functions to calculate average price and plot trends
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

# Step 3: Define the main function for handling general queries
def general_query():
    st.title("General Query on HDB Resale Market")
    
    # Load and preprocess the data
    df = load_and_preprocess_data()
    
    st.write("Data loaded successfully with the following columns:")
    st.write(df.head())

    user_query = st.text_input("Enter your query about HDB resale trends or prices:")
    
    if st.button("Submit"):
        if "average resale price" in user_query.lower():
            st.write(calculate_average_resale_price(df))
        
        elif "price trend" in user_query.lower():
            plot_resale_price_trend(df)
        
        else:
            # Sending the user's query to OpenAI LLM with enhanced context
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an assistant that answers questions based on housing data prices. "
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
