import bcrypt
import streamlit as st

# Retrieve the precomputed hash of the password from Streamlit secrets
hashed_password = st.secrets["STREAMLIT_PASSWORD"]

# Convert the stored hashed password to bytes (if necessary)
PRECOMPUTED_HASH = hashed_password.encode('utf-8')

def authenticate(password):
    # Ensure the input password is encoded to bytes before checking
    return bcrypt.checkpw(password.encode('utf-8'), PRECOMPUTED_HASH)

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
                    st.success("Login successful. Please click the button again to login.") 
                else:
                    st.error("Incorrect password")
        
        return False
    return True

# Call the password protection function at the beginning of your main app code
if password_protect():
    st.write("Your secure content goes here")
