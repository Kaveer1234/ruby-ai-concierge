import streamlit as st
from brain import CompanyBrain
from gtts import gTTS
import os
import time
import json

# -------------------------------
# Load Google Sheets creds from Streamlit secrets
# -------------------------------
creds_dict = st.secrets["gcp_service_account"]

# -------------------------------
# Initialize CompanyBrain with personality library
# -------------------------------
brain = CompanyBrain(
    library_path="library.txt",
    creds_dict=creds_dict,
    sheet_name="Leads"
)

# -------------------------------
# Session state to track conversation
# -------------------------------
if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "lead_data" not in st.session_state:
    st.session_state.lead_data = {}
if "quote_data" not in st.session_state:
    st.session_state.quote_data = {}

# -------------------------------
# Helper functions
# -------------------------------
def speak(text):
    """Convert text to speech and play inline"""
    tts = gTTS(text=text, lang="en")
    filename = "temp.mp3"
    tts.save(filename)
    st.audio(filename, format="audio/mp3")
    os.remove(filename)

def add_message(role, message):
    """Add a message to conversation"""
    st.session_state.conversation.append({"role": role, "message": message})

# -------------------------------
# Lead capture form
# -------------------------------
def lead_capture():
    st.subheader("Hi! Let's get started 😊")
    
    if "name" not in st.session_state.lead_data:
        name = st.text_input("What's your name?", key="name_input")
        if name:
            st.session_state.lead_data["name"] = name
            add_message("customer", name)
    
    elif "company" not in st.session_state.lead_data:
        company = st.text_input(f"Great {st.session_state.lead_data['name']}! Your company?", key="company_input")
        if company:
            st.session_state.lead_data["company"] = company
            add_message("customer", company)
    
    elif "phone" not in st.session_state.lead_data:
        phone = st.text_input("Your phone number?", key="phone_input")
        if phone:
            st.session_state.lead_data["phone"] = phone
            add_message("customer", phone)
    
    elif "email" not in st.session_state.lead_data:
        email = st.text_input("And your email?", key="email_input")
        if email:
            st.session_state.lead_data["email"] = email
            add_message("customer", email)
            # Update Google Sheet immediately
            brain.update_leads_sheet(st.session_state.lead_data)
            add_message("ruby", f"Thanks {st.session_state.lead_data['name']}! I’ve saved your details. 😊")

# -------------------------------
# Quote capture form
# -------------------------------
def quote_capture():
    st.subheader("Let's get your quote 📄")
    q = st.session_state.quote_data
    
    if "type" not in q:
        qtype = st.text_input("Type of calendar?", key="q_type")
        if qtype:
            q["type"] = qtype
    
    elif "quantity" not in q:
        qty = st.number_input("Quantity?", min_value=1, key="q_qty")
        if qty:
            q["quantity"] = qty
    
    elif "colors" not in q:
        colors = st.text_input("Colors for overprint?", key="q_colors")
        if colors:
            q["colors"] = colors
    
    elif "budget" not in q:
        budget = st.text_input("If possible, budget?", key="q_budget")
        if budget:
            q["budget"] = budget
            # All quote info filled → update sheet
            combined_data = {**st.session_state.lead_data, **q}
            brain.update_leads_sheet(combined_data)
            add_message("ruby", "Perfect! I’ve saved your quote details. You’ll hear from us soon! 🌟")
            st.success("Quote submitted successfully!")

# -------------------------------
# Conversation UI
# -------------------------------
st.title("Ruby AI Concierge 💖")

# Display conversation
for chat in st.session_state.conversation:
    if chat["role"] == "ruby":
        st.markdown(f"**Ruby:** {chat['message']}")
    else:
        st.markdown(f"**You:** {chat['message']}")

# Start the flow
if not st.session_state.lead_data.get("email"):
    lead_capture()
else:
    quote_capture()

# -------------------------------
# Personality reply
# -------------------------------
# Example: Ruby can give bubbly responses from library
if st.button("Say something bubbly 💬"):
    response = brain.get_bubbly_response()
    add_message("ruby", response)
    speak(response)
