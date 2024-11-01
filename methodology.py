import streamlit as st

def methodology():
    st.title("Methodology")
    st.write("""
    ## Data Flows
    1. **General Query on HDB**: The user's query is passed to the LLM, which processes it and generates a response based on the model’s knowledge base.
    2  **Housing Affordability Calculator**: User inputs household income, savings, other financial details, as well as his desired housing type / town. The inputs are passed to the LLM with advice on whether it is affordable.

    ## Flowcharts
    Below are the flowcharts that describe the detailed process flow of each use case.
    """)

    st.image("flowcharts/use_case_1_flowchart.png", caption="Use Case 1: General Query on HDB")
    st.image("flowcharts/use_case_2_flowchart.png", caption="Use Case 2 Housing Affordability Calculator:")


    ## Objectives
    - To allow users to ask general questions about HDB resale prices (based on resale flat prices) and received LLM powered responses.
    - To provide users with an easy way to calculate their housing affordability, based on their current income/savings and desired house. The LLM would also provide personalized advice based on the input.
