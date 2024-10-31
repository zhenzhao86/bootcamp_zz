import openai
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
import re

# Initialize OpenAI API key
openai.api_key = st.secrets.api_key
client = OpenAI(api_key=os.getenv(st.secrets.api_key))


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

def general_query():
    st.title("General Query on HDB Resale Market")
    
    # Load and preprocess the data
    df = load_and_preprocess_data()
    st.write("Data loaded successfully with the following columns:")
    st.write(df.head())

    # Extract data summary
    data_summary = extract_data_summary(df)
    st.write("Data Summary:")
    st.write(data_summary)

    user_query = st.text_input("Enter your query about HDB resale trends or prices:")
    user_query = user_query.lower()
    st.write("E.g., What is the average resale price for 5-room flats in 2020?")
    st.write("E.g., What is the average resale price for 3-room flats in bedok in 2020?")
    st.write("E.g., What price trend from 2020 to 2023?")

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
                
            # Prepare the prompt for the LLM
            llm_prompt = (
                "You are an assistant for analyzing HDB resale housing data in Singapore. "
                "You have access to a pandas DataFrame called 'df' that contains information "
                "about HDB resale transactions, including columns for 'month', 'town', 'flat_type', "
                "'block', 'street_name', 'storey_range', 'floor_area_sqm', 'flat_model', "
                "'lease_commence_date', 'remaining_lease_years', and 'resale_price'. "
                "You can query the DataFrame using Python pandas syntax to filter, aggregate, "
                "or analyze data as needed to answer the user's queries. "
                f"Here is the HDB resale data in df: {df}."
                f"Here is a summary of the data: {data_summary}. "
                f"Based on this data, please answer the following query: {user_query}."
                "When matching user queries, remember to look for substrings instead of exact matches."
            )

            # Pass the prompt to the LLM using the new API interface
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": llm_prompt},
                    {"role": "user", "content": user_query}
                ]
            )

            # Output the LLM response
            st.write(response['choices'][0]['message']['content'])

        except Exception as e:
            st.error(f"Error processing the query: {e}")

# Run the general query function in Streamlit app
if __name__ == "__main__":
    general_query()