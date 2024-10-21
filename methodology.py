import streamlit as st

def methodology():
    st.title("Methodology")
    st.write("""
    ## Data Flows
    1. **Housing Affordability Calculator**: User inputs household income, savings, and other financial details. The calculator computes the estimated price of HDB flats they can afford.
    2. **General Query on HDB**: The user's query is passed to the LLM, which processes it and generates a response based on the model’s knowledge base.

    ## Flowcharts
    Below are the flowcharts that describe the detailed process flow of each use case.
    """)

    st.image("flowcharts/use_case_1_flowchart.png", caption="Use Case 1: Housing Affordability Calculator")
    st.image("flowcharts/use_case_2_flowchart.png", caption="Use Case 2: General Query on HDB")
