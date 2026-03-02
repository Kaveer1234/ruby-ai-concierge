import streamlit as st
import base64
from datetime import datetime
from gtts import gTTS
import os
import time
from brain import CompanyBrain
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- 1. INITIALIZE ALL BINS (Must be at the top) ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "step" not in st.session_state:
    st.session_state.step = "name"

if "lead_data" not in st.session_state:
    # Bins matching your Google Sheet: Ruby Leads 2026
    st.session_state.lead_data = {
        "Name": "", "Company": "", "Phone": "", "Email": "",
        "Product": "", "Quantity": "", "Colours": "", "Budget": ""
    }

# --- 2. GOOGLE SHEETS FUNCTION ---
def update_google_sheets(data, lead_type="Initial"):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open("Ruby Leads 2026").sheet1 #
        
        row = [
            data.get("Name", ""), data.get("Company", ""), 
            data.get("Phone", ""), data.get("Email", ""),
            data.get("Product", ""), data.get("Quantity", ""), 
            data.get("Colours", ""), data.get("Budget", ""),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ]
        sheet.append_row(row)
    except Exception as e:
        st.error(f"Sync Error: {e}")

# ... (Keep get_video_base64, Preload, and CSS logic here) ...

# --- 3. CHAT DISPLAY ---
# Display history from the 'messages' bin
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# --- 4. INTERACTION LOOP ---
if user_input := st.chat_input("Talk to RUBY..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.avatar = "talking"
    
    # Lead Collection Logic
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
        # 🚀 MILESTONE 1: Send contact lead immediately
        update_google_sheets(st.session_state.lead_data, "Contact Captured")
    else:
        # Standard Knowledge Base Interaction
        ctx = f"User is {st.session_state.lead_data['Name']} from {st.session_state.lead_data['Company']}. "
        response = brain.get_answer(ctx + user_input, st.session_state.messages)

        # 🚀 MILESTONE 2: Capture Quote details if user picks a product
        if any(kw in response.lower() for kw in ["elephant", "jumbo", "quote", "n18"]):
            st.session_state.lead_data["Product"] = user_input
            update_google_sheets(st.session_state.lead_data, "Quote Detail")

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
