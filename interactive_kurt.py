import streamlit as st
from gtts import gTTS
import os
import time
import threading
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# -------------------------------
# CompanyBrain class
# -------------------------------
class CompanyBrain:
    def __init__(self, library_path, creds_path, sheet_name="Leads"):
        self.library_path = library_path
        self.sheet_name = sheet_name

        # Load personality library
        with open(library_path, "r", encoding="utf-8") as f:
            self.library = f.read()

        # Initialize Google Sheets client
        scope = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open_by_key(self._get_sheet_id()).worksheet(sheet_name)

    def _get_sheet_id(self):
        # Put your Google Sheet ID here or read from secrets
        return st.secrets["google_sheets"]["sheet_id"]

    def update_lead(self, lead_data):
        """Append a new lead row"""
        values = [
            lead_data.get("name", ""),
            lead_data.get("company", ""),
            lead_data.get("tel", ""),
            lead_data.get("email", ""),
            lead_data.get("calendar_type", ""),
            lead_data.get("quantity", ""),
            lead_data.get("colours", ""),
            lead_data.get("budget", ""),
            time.strftime("%Y-%m-%d %H:%M:%S")
        ]
        self.sheet.append_row(values)

    def generate_response(self, prompt):
        """Very simple personality response from library"""
        # Here, just echo or use simple rules; you can expand
        response = f"💬 {prompt} (as per library personality)"
        return response

# -------------------------------
# Initialize CompanyBrain
# -------------------------------
brain = CompanyBrain(
    library_path="library.txt",
    creds_path="secrets/creds.json",
    sheet_name="Leads"
)

# -------------------------------
# Streamlit Layout
# -------------------------------
st.set_page_config(page_title="Ruby AI Concierge", layout="wide")

st.title("Ruby AI Concierge 🤖💁‍♀️")

# Video display (keep exactly as-is)
st.video("video.mp4")  # Your AI agent video

# Chat container
chat_container = st.container()

# Form for lead capture
with st.form("lead_form", clear_on_submit=True):
    st.subheader("Let's get to know you! ✨")
    name = st.text_input("Your name")
    company = st.text_input("Company")
    tel = st.text_input("Telephone")
    email = st.text_input("Email")
    submit_lead = st.form_submit_button("Start Chatting")

    if submit_lead:
        # Immediately save lead
        lead = {"name": name, "company": company, "tel": tel, "email": email}
        brain.update_lead(lead)
        st.success("Thanks! Lead saved. You can chat now.")

# Chat input
user_input = st.text_input("Ask Ruby anything...")

if user_input:
    response = brain.generate_response(user_input)
    st.markdown(f"**Ruby:** {response}")

    # Optional: generate TTS
    tts = gTTS(response)
    tts.save("response.mp3")
    st.audio("response.mp3", format="audio/mp3")

    # Check for quote request
    if "quote" in user_input.lower():
        with st.form("quote_form", clear_on_submit=True):
            st.subheader("Let's get your quote info 📝")
            calendar_type = st.text_input("Type of Calendar")
            quantity = st.text_input("Quantity")
            colours = st.text_input("Colours for overprint")
            budget = st.text_input("If possible, your budget")
            submit_quote = st.form_submit_button("Submit Quote")

            if submit_quote:
                quote_data = {
                    "name": name,
                    "company": company,
                    "tel": tel,
                    "email": email,
                    "calendar_type": calendar_type,
                    "quantity": quantity,
                    "colours": colours,
                    "budget": budget
                }
                brain.update_lead(quote_data)
                st.success("Quote info saved! We'll get back to you soon.")
