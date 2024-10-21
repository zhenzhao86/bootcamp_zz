import streamlit as st

import streamlit as st
import pandas as pd
import requests

# Function to display the About Us page
def about_us():
    st.title("About Us")
    st.write("""
    ## Project Scope
    This project aims to provide citizens with seamless access to information regarding buying HDB flats in the resale market.

    ## Objectives
    - Consolidate information from multiple trustworthy sources.
    - Facilitate understanding through interactive engagements.
    - Customize information presentation based on user inputs.

    ## Data Sources
    - HDB Official Website
    - Government Resources
    - Real Estate Data APIs

    ## Features
    - Step-by-step guidance on the buying process.
    - FAQ section for common queries.
    - Data visualizations for market trends.
    """)

# Function to display the Methodology page
def methodology():
    st.title("Methodology")
    st.write("""
    ## Data Flows and Implementation Details
    This section outlines the data flow and implementation details for our application.
    
    - **Data Collection**: Data is collected from official sources and APIs.
    - **Data Processing**: Data is processed to present it in a user-friendly format.
    - **User Interaction**: Users interact with the application to retrieve tailored information.

    ## Flowchart
    Below is a flowchart illustrating the process flow for each use case in the application.
    """)

    # You can use Streamlit's `st.image` to display a flowchart image
    st.image("flowchart.png")  # Ensure you have a flowchart image in your project directory





# Sample data - Replace this with actual data or data fetching logic
steps = [
    "Step 1: Check your eligibility",
    "Step 2: Choose a resale flat",
    "Step 3: Apply for HDB loan",
    "Step 4: Complete the purchase"
]

faqs = {
    "What is the minimum downpayment?": "The minimum downpayment is 25% of the purchase price.",
    "How long does the buying process take?": "The process typically takes around 3-6 months."
}pip install streamlit

def main():
    st.title("Buying an HDB Flat in the Resale Market")
    st.write("Welcome! This app will help you navigate the buying process.")

    # Display steps
    st.subheader("Steps to Buy an HDB Flat")
    for step in steps:
        st.write(step)

    # FAQ Section
    st.subheader("Frequently Asked Questions")
    for question, answer in faqs.items():
        st.write(f"**{question}**: {answer}")

    # User Input for Custom Queries
    user_query = st.text_input("Ask your question about buying an HDB flat:")
    if user_query:
        response = faqs.get(user_query, "I'm sorry, I don't have that information.")
        st.write(response)


# Main function to set up the app
def main():
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", ["Home", "About Us", "Methodology"])

    if selection == "Home":
        st.title("Buying an HDB Flat in the Resale Market")
        st.write("Welcome! This app will help you navigate the buying process.")
        # Existing content for the home page

    elif selection == "About Us":
        about_us()

    elif selection == "Methodology":
        methodology()

if __name__ == "__main__":
    main()
