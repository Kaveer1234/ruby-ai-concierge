import streamlit as st
import requests
from datetime import datetime
from brain import CompanyBrain

# --- HELPER FUNCTIONS ---
def clean_input(text, prefix_list):
    """Strips conversational phrases to keep data clean for the sheet [cite: 2026-02-11]."""
    clean_text = text.strip()
    for prefix in prefix_list:
        if clean_text.lower().startswith(prefix):
            clean_text = clean_text[len(prefix):].strip()
    # Remove trailing punctuation like full stops
    if clean_text.endswith("."):
        clean_text = clean_text[:-1]
    return clean_text

def save_to_sheets(data):
    """Sends lead data to your Google Apps Script URL [cite: 2026-02-12]."""
    # PASTE YOUR WEB APP URL HERE
    webhook_url = "YOUR_GOOGLE_SCRIPT_WEB_APP_URL_HERE"
    try:
        data["Timestamp"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        requests.post(webhook_url, json=data)
    except Exception as e:
        print(f"Error saving to sheets: {e}")

# --- INITIALIZATION ---
if "step" not in st.session_state:
    st.session_state.step = "name"
    st.session_state.lead_data = {"Name": "", "Company": "", "Phone": "", "Email": "", "Product": "", "Quantity": "", "Colours": "", "Budget": ""}
    st.session_state.messages = []

brain = CompanyBrain()

st.title("RUBY - Associated Industries 2027")

# --- CHAT INTERFACE ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if user_input := st.chat_input("Type your message here..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    response = ""

    # --- STEP 1: NAME CAPTURE (With 'Hi' Filter) ---
    if st.session_state.step == "name":
        # Check if they just said hello [cite: 2026-02-11]
        if len(user_input.strip()) < 3 or user_input.lower() in ["hi", "hello", "hey", "good morning"]:
            response = "Hello! I'm RUBY, your Digital Concierge. Before we dive into our 2027 range, may I ask what your name is?"
        else:
            prefixes = ["hi my name is ", "my name is ", "i am ", "this is ", "name is "]
            st.session_state.lead_data["Name"] = clean_input(user_input, prefixes)
            st.session_state.step = "company"
            response = f"It's a pleasure to meet you, {st.session_state.lead_data['Name']}! Which company are you representing today?"

    # --- STEP 2: COMPANY CAPTURE ---
    elif st.session_state.step == "company":
        prefixes = ["my company is ", "company is ", "i am from ", "representing ", "my company name is "]
        st.session_state.lead_data["Company"] = clean_input(user_input, prefixes)
        st.session_state.step = "phone"
        response = f"Ah, {st.session_state.lead_data['Company']}! A fantastic organization. Just in case our connection drops, what's the best number to reach you on?"

    # --- STEP 3: PHONE CAPTURE ---
    elif st.session_state.step == "phone":
        st.session_state.lead_data["Phone"] = user_input.strip()
        st.session_state.step = "email"
        response = "I've got that. And finally, your work email address? I'll use it to send your 2027 catalog and quotes."

    # --- STEP 4: EMAIL CAPTURE & FIRST SAVE ---
    elif st.session_state.step == "email":
        st.session_state.lead_data["Email"] = user_input.lower().strip()
        st.session_state.step = "chat"
        save_to_sheets(st.session_state.lead_data) # Initial lead save to sheet [cite: 2026-02-12]
        response = f"Perfect, {st.session_state.lead_data['Name']}. I've got your details! How can I help you find the perfect 2027 calendars today?"

    # --- STEP 5: GENERAL CHAT & KNOWLEDGE BASE ---
    else:
        response = brain.get_answer(user_input, st.session_state.messages)

    # Display RUBY's response
    with st.chat_message("assistant"):
        st.write(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
