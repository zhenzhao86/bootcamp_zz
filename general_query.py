import openai
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import glob
import os

# Initialize OpenAI API key
openai.api_key = st.secrets.api_key

# Step 1: Load and preprocess data
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
def average_resale_price(df, flat_type=None, year=None, town=None, area_range=None):
    filtered_df = df.copy()
    
    if flat_type:
        filtered_df = filtered_df[filtered_df['flat_type'].str.lower() == flat_type.lower()]
    if year:
        filtered_df = filtered_df[filtered_df['month'].dt.year == year]
    if town:
        filtered_df = filtered_df[filtered_df['town'].str.lower() == town.lower()]
    if area_range:
        filtered_df = filtered_df[
            (filtered_df['floor_area_sqm'] >= area_range[0]) & 
            (filtered_df['floor_area_sqm'] <= area_range[1])
        ]

    avg_price = filtered_df['resale_price'].mean()
    return f"The average resale price is SGD {avg_price:,.2f}."

def plot_resale_price_trend(df):
    monthly_trend = df.groupby(df['month'].dt.to_period('M'))['resale_price'].mean()
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

# Step 3: Define main function to handle general queries
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
    st.write("E.g., What is the average resale price for 5-room flats in 2020?")

    if st.button("Submit"):
        # Directly handle specific queries
        try:
            if "average resale price" in user_query.lower():
                # Extract parameters from the user query
                flat_type = None
                year = None
                town = None
                area_range = None
                
                # Example extraction logic (this can be expanded for robustness)
                if "room flats" in user_query.lower():
                    flat_type = user_query.split(" ")[2]  # Assuming structure "average resale price for X-room flats"
                if "in" in user_query.lower():
                    town = user_query.split("in")[-1].strip()
                if "between" in user_query.lower():
                    area_range = [int(s) for s in user_query.split() if s.isdigit()]
                
                if year_query := next((s for s in user_query.split() if s.isdigit()), None):
                    year = int(year_query)

                response = average_resale_price(df, flat_type, year, town, area_range)
                st.write(response)
                
            elif "price trend" in user_query.lower():
                plot_resale_price_trend(df)
                
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
                                "or analyze data as needed to answer the user's queries. "
                                f"Here is a summary of the data: {data_summary}."
                            )
                        },
                        {"role": "user", "content": f"Use the HDB resale data provided to answer: {user_query}"}
                    ]
                )
                # Updated way to retrieve the response
                st.write(response["choices"][0]["message"]["content"])

        except Exception as e:
            st.error(f"Error processing the query: {e}")

# Run the general query function in Streamlit app
if __name__ == "__main__":
    general_query()
