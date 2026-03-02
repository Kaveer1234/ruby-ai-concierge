import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import brain  # Assuming your brain.py is in the same folder

# --- 1. INITIALIZE BINS (Stops the crash in image_349145.png) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "lead_data" not in st.session_state:
    st.session_state.lead_data = {
        "Name": "", "Company": "", "Phone": "", "Email": "",
        "Product": "", "Quantity": "", "Colours": "", "Budget": ""
    }

if "step" not in st.session_state:
    st.session_state.step = "name"

# --- 2. GOOGLE SHEETS FUNCTION ---
def update_google_sheets(data, lead_type="Initial"):
    try:
        # Uses the creds.json you uploaded to GitHub
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
        client = gspread.authorize(creds)
        
        # Opens your sheet: Ruby Leads 2026
        sheet = client.open("Ruby Leads 2026").sheet1 
        
        row = [
            data.get("Name", ""), data.get("Company", ""), 
            data.get("Phone", ""), data.get("Email", ""),
            data.get("Product", ""), data.get("Quantity", ""), 
            data.get("Colours", ""), data.get("Budget", ""),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ]
        sheet.append_row(row)
        print("Successfully updated sheet!")
    except Exception as e:
        print(f"Sheet Error: {e}")

# --- 3. CHAT LOGIC & TRIGGERS ---
st.title("RUBY – Associated Industries 2027")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_input := st.chat_input("Type here..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

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
        
        # 🚀 TRIGGER: SEND INITIAL CONTACT TO SHEET
        update_google_sheets(st.session_state.lead_data, "Initial Lead")

    else:
        # Standard chat for quotes/questions
        response = brain.get_answer(user_input, st.session_state.messages)
        
        # 🚀 TRIGGER: IF QUOTE REQUESTED, UPDATE PRODUCT INFO
        if any(word in user_input.lower() for word in ["quote", "calendar", "all"]):
            st.session_state.lead_data["Product"] = user_input
            update_google_sheets(st.session_state.lead_data, "Detailed Quote")

    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
