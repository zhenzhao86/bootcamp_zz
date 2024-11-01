import streamlit as st
import bcrypt

# Password
def authenticate(password):
    hashed_password = bcrypt.hashpw(b"aibootcampzz", bcrypt.gensalt())  # Replace with a hashed password
    return bcrypt.checkpw(password.encode(), hashed_password)

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
                    st.success("Login successful")
                    st.experimental_rerun()  
                else:
                    st.error("Incorrect password")
        
        return False
    return True
