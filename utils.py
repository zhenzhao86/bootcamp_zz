import streamlit as st
import bcrypt

# Hardcoded password (for example purposes, you may implement more secure ways)
def authenticate(password):
    hashed_password = bcrypt.hashpw(b"password123", bcrypt.gensalt())  # Replace with a hashed password
    return bcrypt.checkpw(password.encode(), hashed_password)

def password_protect():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        password = st.text_input("Enter password", type="password")
        if st.button("Login"):
            if authenticate(password):
                st.session_state.authenticated = True
                st.success("Login successful")
            else:
                st.error("Incorrect password")
        return False
    return True
