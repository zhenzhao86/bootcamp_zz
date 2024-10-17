import streamlit as st

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