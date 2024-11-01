import streamlit as st
import bcrypt

# Precomputed hashed password stored in secrets

# Fetch the hashed password from Streamlit secrets and encode it to bytes
hashed_password = st.secrets["STREAMLIT_PASSWORD"].encode('utf-8')  # Ensure it is in bytes

def authenticate(password):
    # Check if the provided password matches the hashed password
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

def password_protect():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        # Create a unique key for the login form
        form_key = f"login_form_{st.session_state.get('form_id', 0)}"
        
        # Create a form for login
        with st.form(key=form_key):
            password = st.text_input("Enter password", type="password")
            login_button = st.form_submit_button("Login")  # This button will submit the form

            # Attempt login when the button is clicked or when Enter is pressed
            if login_button:
                if authenticate(password):
                    st.session_state.authenticated = True
                    st.success("Login successful")
                else:
                    st.error("Incorrect password")

        # Increment form_id to ensure uniqueness for the next form
        if 'form_id' not in st.session_state:
            st.session_state['form_id'] = 0
        st.session_state['form_id'] += 1

        return False
    return True