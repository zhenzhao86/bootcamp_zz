import openai
import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

# Load OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load and preprocess the data from CSV files in the "data" directory
def load_data():
    files = [f for f in os.listdir("data") if f.endswith('.csv')]
    dataframes = []
    for file in files:
        df = pd.read_csv(os.path.join("data", file))
        df['month'] = pd.to_datetime(df['month'], format='%Y-%m')
        dataframes.append(df)
    return pd.concat(dataframes, ignore_index=True)

# Load and prepare data
df = load_data()

# Function to handle data queries
def handle_query(query, df):
    response = ""

    # Check for specific keywords in the query
    if "average resale price" in query.lower():
        avg_price = df['resale_price'].mean()
        response = f"The average resale price across all records is approximately ${avg_price:,.2f}."

    elif "trends over the years" in query.lower():
        # Calculate average prices per year
        df['year'] = df['month'].dt.year
        trends = df.groupby('year')['resale_price'].mean()
        
        # Plot the trends
        plt.figure(figsize=(10, 6))
        plt.plot(trends.index, trends.values, marker='o')
        plt.title("Average Resale Price Over the Years")
        plt.xlabel("Year")
        plt.ylabel("Average Resale Price")
        st.pyplot(plt)
        
        response = "Here is the trend of average resale prices over the years."

    elif "resale prices by town" in query.lower():
        town_avg_prices = df.groupby('town')['resale_price'].mean().sort_values(ascending=False)
        
        # Display top 5 towns by average price
        response = "Top towns by average resale prices:\n" + town_avg_prices.head().to_string()

    else:
        # If query doesn't match predefined types, fallback to LLM for interpretation
        response = query_llm(query, df)
    
    return response

# Function to query OpenAI as fallback
def query_llm(query, df):
    # System message for context
    system_message = {
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
    }
    user_message = {"role": "user", "content": query}

    # Make API call
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[system_message, user_message],
        max_tokens=150
    )
    return response['choices'][0]['message']['content']

# General Query Function
def general_query():
    st.title("General Query on HDB Resale Market")
    user_query = st.text_input("Enter your query about the HDB resale process:")

    if st.button("Submit"):
        if user_query:
            # Handle the query
            response = handle_query(user_query, df)
            st.write(response)
        else:
            st.write("Please enter a query.")
