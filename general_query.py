import openai
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
import re
import numpy as np  # Added missing import for numpy

# Initialize the OpenAI client (Optional)
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Step 1: Load and preprocess data
def load_and_preprocess_data():
    all_files = glob.glob(os.path.join("data", "*.csv"))
    df_list = [pd.read_csv(file) for file in all_files]
    df = pd.concat(df_list, ignore_index=True)

    # Convert all string columns to lowercase
    df.columns = df.columns.str.lower()  # Change column names to lowercase
    df['month'] = pd.to_datetime(df['month'], format='%Y-%m')
    df['resale_price'] = pd.to_numeric(df['resale_price'], errors='coerce')
    df['floor_area_sqm'] = pd.to_numeric(df['floor_area_sqm'], errors='coerce')
    df['remaining_lease_years'] = df['remaining_lease'].str.extract(r'(\d+)').astype(float)
    df['lease_commence_date'] = pd.to_datetime(df['lease_commence_date'], format='%Y').dt.year

    # Convert string values in relevant columns to lowercase
    df['town'] = df['town'].str.lower()
    df['flat_type'] = df['flat_type'].str.lower()
    df['block'] = df['block'].str.lower()
    df['street_name'] = df['street_name'].str.lower()
    df['flat_model'] = df['flat_model'].str.lower()

    return df

# Step 2: Define functions to handle specific queries
def average_resale_price(df, flat_type=None, year=None, town=None, area_range=None):
    filtered_df = df.copy()
    
    # Apply filters only if the parameters are provided
    if flat_type:
        filtered_df = filtered_df[filtered_df['flat_type'].str.contains(flat_type, na=False)]
    if year:
        filtered_df = filtered_df[filtered_df['month'].dt.year == year]
    if town:
        filtered_df = filtered_df[filtered_df['town'].str.contains(town, na=False)]
    if area_range:
        filtered_df = filtered_df[
            (filtered_df['floor_area_sqm'] >= area_range[0]) & 
            (filtered_df['floor_area_sqm'] <= area_range[1])
        ]

    # Debugging output: show the filtered DataFrame
    st.write("Filtered DataFrame for average resale price calculation:")
    st.write(filtered_df)

    if filtered_df.empty:
        return "No records found matching the criteria."

    # Check for NaN values in resale_price
    if filtered_df['resale_price'].isna().all():
        return "All resale prices are unavailable for the selected criteria."

    avg_price = filtered_df['resale_price'].mean()

    return f"The average resale price is SGD {avg_price:,.2f}."

def plot_resale_price_trend(df, flat_type=None, year=None, town=None):
    # Filter the DataFrame based on the parameters provided
    filtered_df = df.copy()
    
    if flat_type:
        filtered_df = filtered_df[filtered_df['flat_type'].str.lower() == flat_type.lower()]
    if year:
        filtered_df = filtered_df[filtered_df['month'].dt.year == year]
    if town:
        filtered_df = filtered_df[filtered_df['town'].str.lower() == town.lower()]

    # Group by month and calculate average resale price
    monthly_trend = filtered_df.groupby(filtered_df['month'].dt.to_period('M'))['resale_price'].mean()
    monthly_trend.index = monthly_trend.index.to_timestamp()
    
    fig, ax = plt.subplots()
    monthly_trend.plot(ax=ax, color='blue', title="Average Resale Price Trend Over Time")
    ax.set_xlabel("Month")
    ax.set_ylabel("Average Resale Price (SGD)")
    
    st.pyplot(fig)

def extract_data_summary(df):
    """Extracts a summary of the DataFrame for context."""
    summary = {
        "Total Records": df.shape[0],
        "Unique Towns": df['town'].nunique(),
        "Unique Flat Types": df['flat_type'].nunique(),
        "Average Resale Price": df['resale_price'].mean(),
        "Average Floor Area (sqm)": df['floor_area_sqm'].mean(),
        "Latest Record Date": df['month'].max().date(),
        "Earliest Record Date": df['month'].min().date(),
    }
    return summary

# This function takes a response containing DataFrame queries, executes the queries,
# and replaces the placeholders in the response with the results.

def process_ai_response_with_dataframe_queries(ai_response, data):
    # Loop through the response text as long as there are queries marked by [QUERY] and [/QUERY]
    while "[QUERY]" in ai_response and "[/QUERY]" in ai_response:
        
        # Find the start and end positions of the query within the response
        start = ai_response.index("[QUERY]") + len("[QUERY]")
        end = ai_response.index("[/QUERY]")
        
        # Extract the query text from between [QUERY] and [/QUERY] tags
        query = ai_response[start:end].strip()  # Stripping extra whitespace
        # st.write("Processing query:", query)  # Optional: Debug output

        try:
            # Execute the query on the provided DataFrame 'data' and get the result
            result = eval(query, {"df": data})

            # Format the result to make it easier to read based on its type
            if isinstance(result, pd.DataFrame):
                result_str = f"\n{result.head(1).to_string()}\n...(showing first row of dataframe)"
            elif isinstance(result, pd.Series):
                result_str = f"\n{result.head(1).to_string()}\n...(showing first row of series)"
            elif isinstance(result, np.ndarray):
                result_str = str(result)
            else:
                result_str = str(result)

            # Replace the original [QUERY]...[/QUERY] part with the actual result string
            ai_response = ai_response.replace(f"[QUERY]{query}[/QUERY]", result_str)
        
        except Exception as e:
            # Return an error message if there's an issue executing the query
            return f"Error executing query: {str(e)}"
    
    # Return the modified response with all queries replaced by their results
    return ai_response

def general_query():
    st.title("General Query on HDB Resale Market")
    
    # Load and preprocess the data
    df = load_and_preprocess_data()
    st.write("Data loaded successfully with the following columns:")
    st.write(df.head())

    # Extract data summary
    data_summary = extract_data_summary(df)

    user_query = st.text_input("Enter your query about HDB resale trends or prices:")
    user_query = user_query.lower()
    st.write("E.g., What is the average resale price for 5-room flats in 2020?")
    st.write("E.g., What is the average resale price for 3-room flats in bedok in 2020?")
    st.write("E.g., What is the price trend?")
    st.write("E.g., Which town have most transactions?")

    if st.button("Submit"):
        # Directly handle specific queries
        try:
            # Extract parameters from the user query
            flat_type = None
            year = None
            town = None

            if "average resale price" in user_query:
                # Use regex to extract the flat type, year, and town
                flat_type_match = re.search(r'(\d+\s?[-]?\s?room)', user_query)
                year_match = re.search(r'(\d{4})', user_query)
                town_match = re.search(r'(?i)\b(ang mo kio|bedok|bishan|bukit batok|bukit merah|bukit panjang|bukit timah|central area|choa chu kang|clementi|geylang|hougang|jurong east|jurong west|kallang/whampoa|marine parade|pasir ris|punggol|queenstown|sembawang|sengkang|serangoon|tampines|toa payoh|woodlands|yishun)\b', user_query)

                if flat_type_match:
                    flat_type = flat_type_match.group(0).replace('-', ' ').strip()  # Replace hyphen with space
                if year_match:
                    year = int(year_match.group(1))  # Convert matched year to int
                if town_match:
                    town = town_match.group(0).strip()  # Get the matched town

                # Debugging output
                st.write(f"Extracted flat type: {flat_type}, year: {year}, town: {town}")

                # Fetch the average resale price based on extracted parameters
                response = average_resale_price(df, flat_type, year, town)
                st.write(response)
                
            elif "price trend" in user_query:
                # Call the plot function with extracted parameters
                plot_resale_price_trend(df, flat_type, year, town)
            
            else:
                # Prepare the prompt for the LLM
                llm_prompt = f"""
                    You are an assistant for analyzing HDB resale housing data in Singapore. 
                    You have access to a pandas DataFrame called 'df' that contains information about HDB resale transactions over the years. 
                    The columns in the DataFrame are: {', '.join(df.columns)}
                    Here is a summary of the data: {data_summary}. 
                    
                    Use the following format in your response: [QUERY]df.your_pandas_query[/QUERY]. 
                    For example, to calculate average resale price, use: [QUERY]df['resale_price'].mean()[/QUERY]. 
                    The 'month' column is a datetime object. Handle it properly. E.g. To filter 2020, use [QUERY]df[df['month'].dt.year == 2020][/QUERY]

                    DO NOT assign variable names to your query.
                    Answer the following query from the user: {user_query}.
                    """


                # Pass the prompt to the LLM using the new API interface
                response = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": llm_prompt},
                        {"role": "user", "content": user_query}
                    ]
                )

                llm_response = response['choices'][0]['message']['content']

                # Output the LLM response
                final_response = process_ai_response_with_dataframe_queries(llm_response, df)

                st.write(final_response)

        except Exception as e:
            st.error(f"Error processing the query: {e}")

import re

def query_dataframe(data, query):
    try:
        # Ensure query is not None or empty before evaluating
        if query is None or query.strip() == "":
            return "Error: No query provided to evaluate."
        
        result = eval(query)
        if isinstance(result, pd.DataFrame):
            return result
        elif isinstance(result, pd.Series):
            return result
        elif isinstance(result, np.ndarray):
            return result
        else:
            return result
    except Exception as e:
        return f"Error executing query: {str(e)}"