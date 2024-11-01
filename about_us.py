import streamlit as st

def about_us():
    st.title("About Us")
    st.write("""
    ## Project Scope
    This is my first Streamlit and LLM project. This web application serves as a tool to help users navigate the HDB resale market, offering two main features: a general query assistant and a housing affordability calculator. 
    
    ## Objectives
    - To allow users to ask general questions about HDB resale prices (based on resale flat prices) and received LLM powered responses.
    - To provide users with an easy way to calculate their housing affordability, based on their current income/savings and desired house. The LLM would also provide personalized advice based on the input.

    ## Data Sources
    The Resale Flat Prices are taken from data gov site : https://data.gov.sg/collections/189/view        
    
    ## Features
    - LLM-powered general query assistant (general query)
    - Housing affordability calculator based on income and savings (affordability calculator)

    ## Pages             
    Affordability Calculator - Input your current finances and desired home, and our LLM will provide personalized advice to afford your dream home.
    General Query on HDB - Ask questions about HDB resale data.
    About Us - About this project.
    Methodology - The logic behind our AI-powered advisors.
    """)

    st.image("image/merlion.jpg", caption="Merlion")
