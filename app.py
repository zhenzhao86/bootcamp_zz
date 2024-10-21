from utils import password_protect
import streamlit as st

# Password protect the app
if not password_protect():
    st.stop()

import streamlit as st
from affordability_calculator import affordability_calculator
from general_query import general_query
from about_us import about_us
from methodology import methodology

st.sidebar.title("Navigation")
option = st.sidebar.selectbox("Choose a page", ["Main", "Affordability Calculator", "General Query on HDB", "About Us", "Methodology"])

if option == "Affordability Calculator":
    affordability_calculator()
elif option == "General Query on HDB":
    general_query()
elif option == "About Us":
    about_us()
elif option == "Methodology":
    methodology()
else:
    # Main Page Content
    with st.expander("IMPORTANT NOTICE: This web application is a prototype developed for educational purposes only. The information provided here is NOT intended for real-world usage and should not be relied upon for making any decisions, especially those related to financial, legal, or healthcare matters."):
        st.write("Furthermore, please be aware that the LLM may generate inaccurate or incorrect information. You assume full responsibility for how you use any generated output. Always consult with qualified professionals for accurate and personalized advice.")
