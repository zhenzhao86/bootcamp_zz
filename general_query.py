import openai
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
import re  # Regular expression module
import numpy as np  # For handling numerical operations

# Initialize the OpenAI client
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Step 1: Load and preprocess data
def load_and_preprocess_data():
    all_files = glob.glob(os.path.join("data", "*.csv"))
    df_list = [pd.read_csv(file) for file in all_files]
    df = pd.concat(df_list, ignore_index=True)

    # Convert all string columns to lowercase
    df.columns = df.columns.str.lower()
    df['month'] = pd.to_datetime(df['month'], format='%Y-%m')
    df['resale_price'] = pd.to_numeric(df['resale_price'], errors='coerce')
    df['floor_area_sqm'] = pd.to_numeric(df['floor_area_sqm'], errors='coerce')
    df['remaining_lease_years'] = df['remaining_lease'].str.extract(r'(\d+)').astype(float)
    df['lease_commence_date'] = pd.to_datetime(df['lease_commence_date'], format='%Y').dt.year

    string_columns = ['town', 'flat_type', 'block', 'street_name', 'flat_model']
    for column in string_columns:
        df[column] = df[column].fillna('').str.lower()

    df['flat_type'] = df['flat_type'].astype(str)
    df['town'] = df['town'].astype(str)

    return df


# Function to process OpenAI's response with queries within [QQ] blocks
def process_ai_response_with_dataframe_queries(ai_response, data):
    while "[QQ]" in ai_response and "[/QQ]" in ai_response:
        start = ai_response.index("[QQ]") + len("[QQ]")
        end = ai_response.index("[/QQ]")
        query = ai_response[start:end].strip()

        if not query:
            return "Error: No query provided to evaluate."

        query = query.split('=')[-1].strip()

        try:
            result = eval(query, {"df": data})
            if isinstance(result, pd.DataFrame):
                result_str = f"\n{result.head(1).to_string()}\n...(showing first row of dataframe)"
            elif isinstance(result, pd.Series):
                result_str = f"\n{result.head(1).to_string()}\n...(showing first row of series)"
            elif isinstance(result, np.ndarray):
                result_str = str(result)
            else:
                result_str = str(result)

            ai_response = ai_response.replace(f"[QQ]{query}[/QQ]", result_str)
        except Exception as e:
            return f"Error executing query: {str(e)}"

    return ai_response


def process_query(df, user_query, data_summary):
    try: 
        llm_prompt = f"""
            You are an assistant for analyzing HDB resale housing data in Singapore. 
            You have access to a pandas DataFrame called 'df' that contains information about HDB resale transactions over the years. 
            The columns in the DataFrame are: {', '.join(df.columns)}
            Here is a summary of the data: {data_summary}. 
            
            Use the following format in your response: [QQ]df.your_pandas_query[/QQ]. 
            For example, to calculate average resale price, use: [QQ]df['resale_price'].mean()[/QQ]. 
            The 'month' column is a datetime object. Handle it properly. E.g. To filter 2020, use [QQ]df[df['month'].dt.year == 2020][/QQ]

            DO NOT assign variable names to your query.
            Answer the following query from the user: {user_query}.
        """

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": llm_prompt},
                {"role": "user", "content": user_query}
            ]
        )

        llm_response = response.choices[0].message.content
        final_response = process_ai_response_with_dataframe_queries(llm_response, df)
        return final_response

    except Exception as e:
        return f"Error processing the query: {e}"


def general_query():
    st.title("General Query on HDB Resale Market")

    df = load_and_preprocess_data()
    st.write("Data loaded successfully with the following columns:")
    st.write(df.head())

    data_summary = extract_data_summary(df)
    user_query = st.text_input("Enter your query about HDB resale trends or prices:")
    submit_button = st.button("Submit")

    if submit_button and user_query:
        response = process_query(df, user_query, data_summary)
        if "Error executing query" in response:
            st.error("There was an issue processing your query. Please try again with a different question.")
        else:
            st.write("Response:")
            st.write(response)
