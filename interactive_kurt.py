import os
import streamlit as st
from company_brain import CompanyBrain  # make sure this points to the updated brain file

# -------------------------------
# Paths & Sheet
# -------------------------------
LIBRARY_PATH = "library/products.txt"
CREDS_PATH = "secrets/creds.json"
SHEET_NAME = "Leads"

# -------------------------------
# Check required files
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
# Initialize CompanyBrain
# -------------------------------
brain = CompanyBrain(
    library_path=LIBRARY_PATH,
    creds_path=CREDS_PATH,
    sheet_name=SHEET_NAME
)

# -------------------------------
# Streamlit Layout (unchanged)
# -------------------------------
st.set_page_config(page_title="Ruby AI Concierge", layout="wide")

st.title("💬 Ruby AI Concierge")

# Video or avatar section (keep as-is)
st.video("video/ruby_intro.mp4")  # or whatever your video path is

# -------------------------------
# Lead capture form
# -------------------------------
with st.form("lead_form", clear_on_submit=True):
    st.subheader("👋 Let's get started!")
    name = st.text_input("Your Name")
    company = st.text_input("Company")
    phone = st.text_input("Phone")
    email = st.text_input("Email")
    submit_lead = st.form_submit_button("Submit")

    if submit_lead:
        brain.add_lead(name, company, phone, email)
        st.success("✅ Lead submitted!")

# -------------------------------
# Quote request flow
# -------------------------------
with st.form("quote_form", clear_on_submit=True):
    st.subheader("📅 Request a Quote")
    q_name = st.text_input("Name")
    q_company = st.text_input("Company")
    q_phone = st.text_input("Phone")
    q_email = st.text_input("Email")
    calendar_type = st.text_input("Type of Calendar")
    quantity = st.text_input("Quantity")
    colours = st.text_input("Colours for overprint")
    budget = st.text_input("Budget (optional)")
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
