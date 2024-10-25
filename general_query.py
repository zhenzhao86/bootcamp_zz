import openai
import pandas as pd
import os
import streamlit as st

# You can replace this with the actual API key after signing up
openai.api_key = st.secrets.api_key

# Load and preprocess the HDB resale dataset
def load_data():
    # Load the CSV file
    df = pd.read_csv('data/Resale flat prices based on registration date from Jan-2017 onwards.csv')
    
    # Preprocessing steps
    df['month'] = pd.to_datetime(df['month'], format='%Y-%m')  # Convert month to datetime
    df['lease_commence_date'] = pd.to_datetime(df['lease_commence_date'], format='%Y')  # Convert lease start to datetime
    df['storey_range'] = df['storey_range'].astype(str)  # Ensure storey range is string
    df['flat_type'] = df['flat_type'].astype(str)  # Ensure flat type is string
    
    # Fill missing values (if any)
    df.fillna({
        'resale_price': 0,
        'remaining_lease': 'Unknown'
    }, inplace=True)

    return df

# Query the dataset based on user input
def search_data(user_query, df):
    # Simplified search logic (exact match or contains logic)
    filtered_df = df[df.apply(lambda row: row.astype(str).str.contains(user_query, case=False).any(), axis=1)]
    
    # If matching records are found
    if not filtered_df.empty:
        return filtered_df.head(5)  # Limit to the top 5 results
    else:
        return None

def general_query():
    st.title("General Query on HDB Resale Market")
    
    # Load the dataset
    df = load_data()
    
    user_query = st.text_input("Enter your query about the HDB resale process:")
    
    if st.button("Submit"):
        if user_query:
            # Search in the dataset
            result_df = search_data(user_query, df)
            
            if result_df is not None:
                # Display the search result to the user
                st.write("Here are the top matches from the HDB resale dataset:")
                st.write(result_df)
                
                # Create the prompt combining user query and search result
                combined_prompt = f"The user asked about {user_query}. Based on the HDB resale dataset: {result_df.to_dict()}, provide an accurate answer about Singapore HDB resale prices."

                # Use OpenAI API to generate a detailed response as an HDB resale assistant
                response = openai.ChatCompletion.create(
                    model="gpt-4",  # or "gpt-3.5-turbo"
                    messages=[
                        {"role": "system", "content": "You are an HDB resale assistant specializing in the Singapore housing market. Use the data provided to give accurate information on HDB resale prices and other related queries."},
                        {"role": "user", "content": combined_prompt}
                    ],
                    max_tokens=200
                )
                st.write(response['choices'][0]['message']['content'])
            else:
                st.write("No matching records found in the HDB dataset.")
        else:
            st.write("Please enter a query.")