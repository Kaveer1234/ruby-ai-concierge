import os
import streamlit as st
from company_brain import CompanyBrain  # ensure company_brain.py is in same folder

# -------------------------------
# Paths & Sheet
# -------------------------------
LIBRARY_PATH = "library/products.txt"
CREDS_PATH = "secrets/creds.json"
SHEET_NAME = "Leads"

# -------------------------------
# Startup checks
# -------------------------------
missing_files = []
if not os.path.exists(LIBRARY_PATH):
    missing_files.append(f"Library file missing: {LIBRARY_PATH}")
if not os.path.exists(CREDS_PATH):
    missing_files.append(f"Credentials file missing: {CREDS_PATH}")

if missing_files:
    st.error("⚠️ Startup Error:\n" + "\n".join(missing_files))
    st.stop()

# -------------------------------
# Initialize Brain
# -------------------------------
brain = CompanyBrain(
    library_path=LIBRARY_PATH,
    creds_path=CREDS_PATH,
    sheet_name=SHEET_NAME
)

# -------------------------------
# Streamlit Layout
# -------------------------------
st.set_page_config(page_title="Ruby AI Concierge", layout="wide")
st.title("💬 Ruby AI Concierge")

# Video section (layout unchanged)
st.video("video/ruby_intro.mp4")

# -------------------------------
# Chat Section
# -------------------------------
st.subheader("💡 Chat with Ruby")
user_input = st.text_input("You:", key="chat_input")
if st.button("Send", key="send_btn") and user_input:
    response = brain.respond(user_input)
    st.text_area("Ruby:", value=response, height=100)

# -------------------------------
# Lead capture form
# -------------------------------
with st.form("lead_form", clear_on_submit=True):
    st.subheader("👋 Let's get started!")
    name = st.text_input("Your Name", key="lead_name")
    company = st.text_input("Company", key="lead_company")
    phone = st.text_input("Phone", key="lead_phone")
    email = st.text_input("Email", key="lead_email")
    submit_lead = st.form_submit_button("Submit Lead")
    if submit_lead:
        brain.add_lead(name, company, phone, email)
        st.success("✅ Lead submitted!")

# -------------------------------
# Quote request form
# -------------------------------
with st.form("quote_form", clear_on_submit=True):
    st.subheader("📅 Request a Quote")
    q_name = st.text_input("Name", key="quote_name")
    q_company = st.text_input("Company", key="quote_company")
    q_phone = st.text_input("Phone", key="quote_phone")
    q_email = st.text_input("Email", key="quote_email")
    calendar_type = st.text_input("Type of Calendar", key="quote_calendar")
    quantity = st.text_input("Quantity", key="quote_quantity")
    colours = st.text_input("Colours for overprint", key="quote_colours")
    budget = st.text_input("Budget (optional)", key="quote_budget")
    submit_quote = st.form_submit_button("Submit Quote")
    if submit_quote:
        lead_data = {
            "name": q_name,
            "company": q_company,
            "phone": q_phone,
            "email": q_email,
            "calendar_type": calendar_type,
            "quantity": quantity,
            "colours": colours,
            "budget": budget
        }
        brain.add_quote(lead_data)
        st.success("✅ Quote request submitted!")
