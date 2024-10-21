import openai
import streamlit as st

# You can replace this with the actual API key after signing up
openai.api_key = 'your-openai-api-key'

def general_query():
    st.title("General Query on HDB Resale Market")
    
    user_query = st.text_input("Enter your query about the HDB resale process:")
    
    if st.button("Submit"):
        if user_query:
            response = openai.Completion.create(
                engine="text-davinci-003",  # You can use GPT-3.5 or GPT-4 depending on your preference
                prompt=user_query,
                max_tokens=150
            )
            st.write(response.choices[0].text)
        else:
            st.write("Please enter a query.")
