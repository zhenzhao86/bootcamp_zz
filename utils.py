import streamlit as st
import bcrypt

# Hardcoded password (for example purposes, you may implement more secure ways)
def authenticate(password):
    # Hashing the password once here is not ideal. Ideally, use a stored hashed password.
    hashed_password = st.secrets["STREAMLIT_PASSWORD"]
    return bcrypt.checkpw(password.encode(), hashed_password)

def password_protect():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        # Create a form for login
        with st.form("login_form"):
            password = st.text_input("Enter password", type="password")
            login_button = st.form_submit_button("Login")  # This button will submit the form

            # Attempt login when the button is clicked or when Enter is pressed
            if login_button:
                if authenticate(password):
                    st.session_state.authenticated = True
                    st.success("Login successful")
                else:
                    st.error("Incorrect password")

        return False
    return True

# Call the password protection function at the beginning of your main app code
if password_protect():
    st.write("Your secure content goes here")