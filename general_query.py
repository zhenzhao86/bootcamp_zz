import openai
import pandas as pd
import os
import streamlit as st

# You can replace this with the actual API key after signing up
openai.api_key = 'ysk-proj-lNJAXFgELuQFEW-lrG-GZkIqXzPPEnsDnJuS1fsCNS77z6qm9zDCX1rjopT3BlbkFJSE0kZOAonjxwhRezJoPIj840z5aQB3z-i2I563K-fGTdAXWwtuaReyXFMA'

# Function to load and combine CSV files
def load_data():
    data_folder = "data"  # Folder where your CSV files are stored
    all_data = []

    # Loop through all CSV files in the folder
    for filename in os.listdir(data_folder):
        if filename.endswith('.csv'):
            file_path = os.path.join(data_folder, filename)
            df = pd.read_csv(file_path)
            all_data.append(df)

    # Combine all DataFrames into a single DataFrame
    combined_data = pd.concat(all_data, ignore_index=True)
    return combined_data

# Function to handle user queries using the loaded data
def handle_query(data, user_query):
    # This is a simple example of filtering the DataFrame based on a user query
    result = data[data.apply(lambda row: row.astype(str).str.contains(user_query, case=False).any(), axis=1)]
    return result

def general_query():
    st.title("General Query on HDB Resale Market")
    
    # Load data from CSV files
    data = load_data()
    
    user_query = st.text_input("Enter your query about the HDB resale process:")
    
    if st.button("Submit"):
        if user_query:
            # Attempt to find relevant information from the data
            results = handle_query(data, user_query)

            if not results.empty:
                st.write("Search Results:")
                st.dataframe(results)
            else:
                # If no results found, fallback to the OpenAI API for a general response
                response = openai.Completion.create(
                    engine="text-davinci-003",  # You can use GPT-3.5 or GPT-4 depending on your preference
                    prompt=f"Based on the HDB resale market data, {user_query}",
                    max_tokens=150
                )
                st.write("OpenAI Response:")
                st.write(response.choices[0].text.strip())
        else:
            st.write("Please enter a query.")

