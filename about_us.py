import streamlit as st

def about_us():
    st.title("About Us")
    st.write("""
    ## Project Scope
    This web application serves as an educational tool to help users navigate the HDB resale market, offering two main features: a housing affordability calculator and general information about HDB. 
    
    ## Objectives
    - To provide citizens with an easy way to calculate their housing affordability.
    - To allow users to ask general questions about HDB and receive AI-powered responses.
    
    ## Data Sources
    - [HDB Official Website](https://www.hdb.gov.sg/)
    - [Singapore Government APIs](https://www.developer.gov.sg/)
    
    ## Features
    - LLM-powered general query assistant
    - Housing affordability calculator based on income and savings
    """)
