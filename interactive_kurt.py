import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import brain

# --- 1. INITIALIZE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "lead_data" not in st.session_state:
    st.session_state.lead_data = {"Name": "", "Company": "", "Phone": "", "Email": "", "Product": ""}
if "step" not in st.session_state:
    st.session_state.step = "name"

# --- 2. GOOGLE SHEETS FUNCTION ---
def update_google_sheets(data):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        # Ensure creds.json is exactly as downloaded from Google
        creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open("Ruby Leads 2026").sheet1
        row = [
            data.get("Name", ""), data.get("Company", ""), 
            data.get("Phone", ""), data.get("Email", ""),
            data.get("Product", ""), "", "", "", 
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ]
        sheet.append_row(row)
    except Exception as e:
        st.error(f"Sheet Sync Error: {e}") # This will show the error in the app for debugging

# --- 3. LAYOUT (Restored to Gold Standard) ---
st.set_page_config(layout="wide")

# This creates the top-left image placement
col1, col2 = st.columns([1, 2])

with col1:
    st.image("ruby_image.jpg") # Use your actual image filename here
    st.title("RUBY – Associated Industries 2027")

with col2:
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_input := st.chat_input("Type here..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Lead Generation Flow
        if st.session_state.step == "name":
            st.session_state.lead_data["Name"] = user_input
            st.session_state.step = "company"
            response = f"Nice to meet you {user_input}! Which company are you with?"
        
        elif st.session_state.step == "company":
            st.session_state.lead_data["Company"] = user_input
            st.session_state.step = "phone"
            response = "Got it. What is your telephone number?"
            
        elif st.session_state.step == "phone":
            st.session_state.lead_data["Phone"] = user_input
            st.session_state.step = "email"
            response = "And your company email address?"
            
        elif st.session_state.step == "email":
            st.session_state.lead_data["Email"] = user_input
            st.session_state.step = "chat"
            response = "Perfect! How can I help you today?"
            update_google_sheets(st.session_state.lead_data)
            
        else:
            # Replaced 'get_answer' with a generic call—check your brain.py function name!
            try:
                response = brain.get_answer(user_input, st.session_state.messages)
            except AttributeError:
                response = "I'm having trouble connecting to my brain. Please check the function name in brain.py."
            
            if any(word in user_input.lower() for word in ["quote", "calendar", "all"]):
                st.session_state.lead_data["Product"] = user_input
                update_google_sheets(st.session_state.lead_data)

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
