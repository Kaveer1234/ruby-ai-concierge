import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import brain

# --- 1. INITIALIZE (VERSION D STANDARD) ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "lead_data" not in st.session_state:
    st.session_state.lead_data = {"Name": "", "Company": "", "Phone": "", "Email": "", "Product": ""}
if "step" not in st.session_state:
    st.session_state.step = "name"

# --- 2. GOOGLE SHEETS FUNCTION (HIDDEN BACKEND) ---
def update_google_sheets(data):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        # Uses the creds.json you confirmed is on GitHub
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
        print(f"Sheet Error: {e}")

# --- 3. LAYOUT (YOUR EXACT VERSION D) ---
st.set_page_config(layout="wide")
st.title("RUBY – Associated Industries 2027")

col1, col2 = st.columns([1, 1]) # Standard 50/50 split from Version D

with col1:
    # Restored your exact video logic
    if st.session_state.get("is_talking"):
        st.video("kurt_talking.mp4", autoplay=True)
    else:
        st.video("kurt_idle.mp4", autoplay=True, loop=True)

with col2:
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_input := st.chat_input("Type here..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # --- LEAD FLOW LOGIC ---
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
            # 🚀 SYNC INITIAL CONTACT
            update_google_sheets(st.session_state.lead_data)
            
        else:
            # Reverted to your original brain call
            response = brain.get_answer(user_input, st.session_state.messages)
            
            # Update sheet if they ask for a quote
            if any(word in user_input.lower() for word in ["quote", "calendar", "all"]):
                st.session_state.lead_data["Product"] = user_input
                update_google_sheets(st.session_state.lead_data)

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
