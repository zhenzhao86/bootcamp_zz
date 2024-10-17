import streamlit as st
import pandas as pd
import requests

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
}

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

if __name__ == "__main__":
    main()
