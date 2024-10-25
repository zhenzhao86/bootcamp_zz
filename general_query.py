import openai
import pandas as pd
import os
import streamlit as st

# You can replace this with the actual API key after signing up
openai.api_key = st.secrets.api_key

# Function to load and concatenate all CSV files in the data folder
def load_data():
    # Use glob to find all CSV files in the "data" folder
    all_files = glob.glob(os.path.join("data", "*.csv"))
    
    # List to hold each CSV file as a DataFrame
    df_list = []
    
    # Read each file and append it to the list
    for file in all_files:
        df = pd.read_csv(file)
        df_list.append(df)
    
    # Concatenate all DataFrames in the list into a single DataFrame
    combined_df = pd.concat(df_list, ignore_index=True)
    
    # Preprocess data
    combined_df['month'] = pd.to_datetime(combined_df['month'], format='%Y-%m')  # Convert month to datetime
    combined_df['lease_commence_date'] = pd.to_datetime(combined_df['lease_commence_date'], format='%Y')  # Convert lease start to datetime
    combined_df['storey_range'] = combined_df['storey_range'].astype(str)  # Ensure storey range is string
    combined_df['flat_type'] = combined_df['flat_type'].astype(str)  # Ensure flat type is string
    
    return combined_df


# Analysis functions
def calculate_average_price(df):
    avg_price = df['resale_price'].mean()
    return f"The average resale price is ${avg_price:.2f}"

def plot_price_trend(df):
    # Monthly average resale price trend
    trend_df = df.groupby(df['month'].dt.to_period('M')).resale_price.mean()
    trend_df.index = trend_df.index.to_timestamp()
    
    fig, ax = plt.subplots()
    trend_df.plot(ax=ax, color='blue')
    ax.set_title('Average HDB Resale Price Over Time')
    ax.set_xlabel('Month')
    ax.set_ylabel('Average Resale Price ($)')
    st.pyplot(fig)

def plot_flat_type_distribution(df):
    # Flat type distribution
    fig, ax = plt.subplots()
    df['flat_type'].value_counts().plot(kind='bar', ax=ax, color='green')
    ax.set_title('Distribution of HDB Flat Types')
    ax.set_xlabel('Flat Type')
    ax.set_ylabel('Count')
    st.pyplot(fig)

def general_query():
    st.title("General Query on HDB Resale Market")
    
    # Load the dataset
    df = load_data()
    
    user_query = st.text_input("Enter your query about HDB resale trends, prices, or flat types:")
    
    if st.button("Submit"):
        if user_query:
            # Determine user query type and process accordingly
            if "average resale price" in user_query.lower():
                st.write(calculate_average_price(df))
            
            elif "price trend" in user_query.lower() or "housing trends" in user_query.lower():
                st.write("Here is the average resale price trend over time:")
                plot_price_trend(df)
            
            elif "flat type distribution" in user_query.lower():
                st.write("Here is the distribution of different flat types in the dataset:")
                plot_flat_type_distribution(df)
            
            else:
                # Use OpenAI for complex or unspecified queries
                response = openai.ChatCompletion.create(
                    model="gpt-4",  # or "gpt-3.5-turbo"
                    messages=[
                        {"role": "system", "content": "You are an HDB resale assistant specializing in the Singapore housing market. Use the data provided to give accurate information on HDB resale prices and trends."},
                        {"role": "user", "content": f"Answer this query based on HDB resale data: {user_query}"}
                    ],
                    max_tokens=200
                )
                st.write(response['choices'][0]['message']['content'])
        else:
            st.write("Please enter a query.")
