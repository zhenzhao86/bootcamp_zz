import streamlit as st
from affordability_calculator import affordability_calculator
from about_us import about_us
from methodology import methodology
from utils import password_protect


# Password protect the app
if not password_protect():
    st.stop()

# Sidebar Navigation
st.sidebar.title("Navigation")
option = st.sidebar.selectbox(
    "Choose a page", 
    ["Main", "Affordability Calculator", "General Query on HDB", "About Us", "Methodology"]
)

# Main Page Content
if option == "Main":
    st.title("HDB Resale Market Information Platform")
    
    with st.expander("IMPORTANT NOTICE:"):
        st.write("""
        This web application is a prototype developed for educational purposes only.
        The information provided here is NOT intended for real-world usage and should not be relied upon 
        for making any decisions, especially those related to financial, legal, or healthcare matters.

        Furthermore, please be aware that the LLM may generate inaccurate or incorrect information. 
        You assume full responsibility for how you use any generated output.

        Always consult with qualified professionals for accurate and personalized advice.
        """)

# Housing Affordability Calculator Page
elif option == "Affordability Calculator":
    affordability_calculator()

# General Query Page
elif option == "General Query on HDB":
    general_query()

# About Us Page
elif option == "About Us":
    about_us()

# Methodology Page
elif option == "Methodology":
    methodology()
