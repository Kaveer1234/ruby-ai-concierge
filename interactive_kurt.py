import streamlit as st
from brain import CompanyBrain

# -------------------------------
# Paths & Sheet
# -------------------------------
LIBRARY_PATH = "library/products.txt"
CREDS_PATH = "secrets/creds.json"
SHEET_NAME = "Leads"

# -------------------------------
# Initialize CompanyBrain
# -------------------------------
brain = CompanyBrain(library_path=LIBRARY_PATH),

# -------------------------------
# Streamlit App Layout
# -------------------------------

st.set_page_config(page_title="Ruby AI Concierge", layout="wide")

st.title("💬 Ruby AI Concierge")

# Embed video avatar (idle/talking/thinking)
video_file = "kurt_idle.mp4"
st.video(video_file)

# -------------------------------
# Lead Capture Form
# -------------------------------
st.subheader("New Customer Inquiry")
with st.form("lead_form"):
    name = st.text_input("Name")
    company = st.text_input("Company")
    tel = st.text_input("Telephone")
    email = st.text_input("Email")
    submit_lead = st.form_submit_button("Submit Inquiry")

    if submit_lead and name and company and tel and email:
        brain.add_lead(name, company, tel, email)
        st.success(f"Thanks {name}! Your info has been captured.")

# -------------------------------
# Quote Request Form
# -------------------------------
st.subheader("Request a Quote")
with st.form("quote_form"):
    q_name = st.text_input("Customer Name")
    q_company = st.text_input("Company Name")
    q_tel = st.text_input("Telephone")
    q_email = st.text_input("Email")
    calendar_type = st.text_input("Type of Calendar")
    quantity = st.number_input("Quantity", min_value=1)
    colours = st.text_input("Colours for Overprint")
    budget = st.text_input("Budget (if known)")
    submit_quote = st.form_submit_button("Submit Quote")

    if submit_quote and q_name and q_company and q_tel and q_email:
        lead_info = {
            "name": q_name,
            "company": q_company,
            "tel": q_tel,
            "email": q_email
        }
        brain.add_quote(lead_info, calendar_type, quantity, colours, budget)
        st.success(f"Quote request submitted for {q_name}!")

# -------------------------------
# Chat Section
# -------------------------------
st.subheader("Chat with Ruby")
user_message = st.text_input("Say something to Ruby:")

if user_message:
    response = brain.respond(user_message)
    st.write(f"Ruby: {response}")


