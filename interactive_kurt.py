import streamlit as st
import base64
from datetime import datetime
from gtts import gTTS
import os
import time
from brain import CompanyBrain
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- GOOGLE SHEETS INTEGRATION ---
def update_google_sheets(data, lead_type="Initial"):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
        client = gspread.authorize(creds)
        
        # Opens your specific sheet: Ruby Leads 2026
        sheet = client.open("Ruby Leads 2026").sheet1 
        
        # MAPPING TO YOUR 9 COLUMNS (A-I)
        row = [
            data.get("Name", ""),     # A: Name
            data.get("Company", ""),  # B: Company
            data.get("Phone", ""),    # C: Phone
            data.get("Email", ""),    # D: Email
            data.get("Product", ""),  # E: Product
            data.get("Quantity", ""), # F: Quantity
            data.get("Colours", ""),  # G: Colours
            data.get("Budget", ""),   # H: Budget
            datetime.now().strftime("%Y-%m-%d %H:%M:%S") # I: Timestamp
        ]
        sheet.append_row(row)
        print(f"✅ {lead_type} lead updated.")
    except Exception as e:
        print(f"❌ Sheet Sync Failed: {e}")

# ... (Keep get_video_base64 and Preload logic exactly the same) ...

# --- 4. INTERACTION ---
if user_input := st.chat_input("Talk to RUBY..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.avatar = "talking"
    
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
        
        # 🚀 TRIGGER 1: Send initial contact immediately
        update_google_sheets(st.session_state.lead_data, "Contact Capture")

    else:
        ctx = f"User is {st.session_state.lead_data['Name']} from {st.session_state.lead_data['Company']}. "
        response = brain.get_answer(ctx + user_input, st.session_state.messages)

        # 🚀 TRIGGER 2: If the user picks a product (like Jumbo Poster/Elephant)
        # We look for keywords that indicate the quote details are being decided
        if any(keyword in response.lower() for keyword in ["ref n18", "elephant", "jumbo", "quantity"]):
            # Update local lead_data with any extracted info before sending
            st.session_state.lead_data["Product"] = user_input if "elephant" in user_input.lower() else st.session_state.lead_data.get("Product", "Jumbo Poster Inquiry")
            update_google_sheets(st.session_state.lead_data, "Detailed Quote")

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
