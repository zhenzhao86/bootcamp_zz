import bcrypt
import streamlit as st

# Precomputed hash of the password (hashed once and then stored here)
STREAMLIT_PASSWORD = st.secrets["STREAMLIT_PASSWORD"]
PRECOMPUTED_HASH = bcrypt.hashpw(STREAMLIT_PASSWORD, bcrypt.gensalt())  # Hash this password once and save the result

def authenticate(password):
    return bcrypt.checkpw(password.encode(), PRECOMPUTED_HASH)

def password_protect():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        with st.form("login_form"):
            password = st.text_input("Enter password", type="password")
            login_button = st.form_submit_button("Login")
        
            if login_button:
                if authenticate(password):
                    st.session_state.authenticated = True
                    st.success("Login successful. Please click button again to login.") 
                else:
                    st.error("Incorrect password")
        
        return False
    return True
