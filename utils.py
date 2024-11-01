import bcrypt
import streamlit as st

# Precomputed hash of the password (hashed once and then stored here)
PRECOMPUTED_HASH = bcrypt.hashpw(b"aibootcampzz", bcrypt.gensalt())  # Hash this password once and save the result

def authenticate(password):
    return bcrypt.checkpw(password.encode(), PRECOMPUTED_HASH)

def password_protect():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        password = st.text_input("Enter password", type="password")
        if st.button("Login"):
            if authenticate(password):
                st.session_state.authenticated = True
                st.success("Login successful!")
            else:
                st.error("Incorrect password")
        return False
    return True
