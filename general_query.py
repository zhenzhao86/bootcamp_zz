import openai
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
import numpy as np  # Added missing import for numpy

# Initialize the OpenAI client
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

    # Convert string values in relevant columns to lowercase and handle NaNs
    string_columns = ['town', 'flat_type', 'block', 'street_name', 'flat_model']
    for column in string_columns:
        df[column] = df[column].fillna('').str.lower()  # Fill NaNs and convert to lowercase

    # Ensure that the DataFrame has proper string types
    df['flat_type'] = df['flat_type'].astype(str)
    df['town'] = df['town'].astype(str)

    return df


# Step 2: Define functions to handle specific queries
def average_resale_price(df, flat_type=None, year=None, town=None, area_range=None):
    filtered_df = df.copy()
    filtered_df.fillna('', inplace=True)

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

    if filtered_df.empty:
        return "No records found matching the criteria."

    avg_price = filtered_df['resale_price'].mean()
    return f"The average resale price is SGD {avg_price:,.2f}."


def plot_resale_price_trend(df, flat_type=None, year=None, town=None):
    filtered_df = df.copy()
    filtered_df.fillna('', inplace=True)

    if flat_type:
        filtered_df = filtered_df[filtered_df['flat_type'].str.lower() == flat_type.lower()]
    if year:
        filtered_df = filtered_df[filtered_df['month'].dt.year == year]
    if town:
        filtered_df = filtered_df[filtered_df['town'].str.lower() == town.lower()]

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

def process_ai_response_with_dataframe_queries(ai_response, data):
    """Processes the AI response and executes DataFrame queries."""
    while "[QUERY]" in ai_response and "[/QUERY]" in ai_response:
        start = ai_response.index("[QUERY]") + len("[QUERY]")
        end = ai_response.index("[/QUERY]")
        query = ai_response[start:end].strip()

        # Debugging output
        st.write("AI Response:", ai_response)
        st.write("Extracted Query:", query)

        if not query:
            return "Error: No query provided to evaluate."

        try:
            query = query.replace('df', 'data')
            result = eval(query, {"data": data})  # Pass 'data' as a variable in the eval context
            
            # Format the result based on its type
            if isinstance(result, pd.DataFrame):
                result_str = f"\n{result.head(1).to_string()}\n...(showing first row of dataframe)"
            elif isinstance(result, pd.Series):
                result_str = f"\n{result.head(1).to_string()}\n...(showing first row of series)"
            elif isinstance(result, np.ndarray):
                result_str = str(result)
            else:
                result_str = str(result)

        except Exception as e:
            return f"Error executing query: {str(e)}"

        # Replace the original [QUERY]...[/QUERY] part with the actual result string
        ai_response = ai_response.replace(f"[QUERY]{query}[/QUERY]", result_str)

    return ai_response

def general_query():
    """Handles the user input for general queries on the HDB resale market."""
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
    st.write("E.g., What is the average resale price for 3-room flats in Bedok in 2020?")
    st.write("E.g., What is the price trend from 2020 to 2023?")

    if st.button("Submit"):
        try: 
            llm_prompt = f"""(
                You are an assistant for analyzing HDB resale housing data in Singapore. 
                You have access to a pandas DataFrame called 'df' that contains information about HDB resale transactions over the years. 
                The columns in the DataFrame are: {', '.join(df.columns)}
                You can query the DataFrame df using Python pandas syntax to filter, aggregate, or analyze data as needed to answer the user's queries. 
                Here is a summary of the data: {data_summary}. 

                When matching user queries, remember to look for substrings instead of exact matches. 
                Use the following format in your response: [QUERY]data.your_pandas_query_here[/QUERY]. 
                For example, to calculate average resale price, use: [QUERY]data['resale_price'].mean()[/QUERY]. 

                Do not assign variable names to your query. e.g. don't assign data_2020 = query.
                Use DataFrame queries when needed to provide accurate and specific answers.
                Use separate [QUERY] blocks if multiple steps are required and explain step by step.

                Based on this data, answer the following query from the user: {user_query}.
            )"""

            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": llm_prompt},
                    {"role": "user", "content": user_query}
                ]
            )

            llm_response = response['choices'][0]['message']['content']
            st.write(llm_response)

            # Execute DataFrame queries in the response (in QUERY blocks)
            final_response = process_ai_response_with_dataframe_queries(llm_response, df)
            st.write(final_response)

        except Exception as e:
            st.error(f"Error processing the query: {e}")

# Run the general query function in Streamlit app
if __name__ == "__main__":
    general_query()
