import streamlit as st
import requests
import base64
from datetime import datetime
from gtts import gTTS
import os
from brain import CompanyBrain

# --- 1. MOBILE & DESKTOP UI SETUP ---
st.set_page_config(page_title="RUBY - Associated Industries", layout="centered")

# Custom CSS for responsiveness [cite: 2026-02-11]
st.markdown("""
    <style>
    .main { max-width: 800px; margin: 0 auto; }
    .stVideo { width: 100% !important; border-radius: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
    /* Mobile adjustments */
    @media (max-width: 600px) {
        .stChatMessage { font-size: 14px !important; }
        .stTitle { font-size: 22px !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HELPER FUNCTIONS ---
def clean_input(text, prefix_list):
    """Strips conversational phrases [cite: 2026-02-11]."""
    clean_text = text.strip()
    for prefix in prefix_list:
        if clean_text.lower().startswith(prefix):
            clean_text = clean_text[len(prefix):].strip()
    return clean_text.rstrip(".")

def save_to_sheets(data):
    """Sends clean data to Google [cite: 2026-02-12]."""
    webhook_url = "YOUR_GOOGLE_SCRIPT_WEB_APP_URL_HERE"
    try:
        data["Timestamp"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        requests.post(webhook_url, json=data)
    except Exception as e:
        st.error(f"Sync Error: {e}")

def speak(text):
    """Voice engine [cite: 2026-02-09, 2026-02-11]."""
    tts = gTTS(text=text, lang='en', tld='co.za')
    tts.save("response.mp3")
    with open("response.mp3", "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f'<audio src="data:audio/mp3;base64,{b64}" autoplay="true"></audio>'
        st.markdown(md, unsafe_allow_html=True)
    os.remove("response.mp3")

# --- 3. INITIALIZATION ---
if "step" not in st.session_state:
    st.session_state.step = "name"
    st.session_state.lead_data = {"Name": "", "Company": "", "Phone": "", "Email": "", "Product": "", "Quantity": "", "Colours": "", "Budget": ""}
    st.session_state.messages = []

brain = CompanyBrain()

# --- 4. THE VISUAL INTERFACE (Corrected Filenames) ---
st.title("RUBY - Associated Industries 2027")

# We will use kurt_idle.mp4 as the primary avatar
try:
    video_file = open('kurt_idle.mp4', 'rb') 
    video_bytes = video_file.read()
    st.video(video_bytes)
except FileNotFoundError:
    st.warning("Video file 'kurt_idle.mp4' not found in your GitHub folder.")

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# --- 5. LOGIC FLOW ---
if user_input := st.chat_input("Talk to RUBY..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    response = ""

    if st.session_state.step == "name":
        if len(user_input.strip()) < 3 or user_input.lower() in ["hi", "hello", "hey"]:
            response = "Hello! I'm RUBY, your Digital Concierge. Before we look at our 2027 range, may I ask your name?"
        else:
            st.session_state.lead_data["Name"] = clean_input(user_input, ["my name is ", "hi my name is ", "i am "])
            st.session_state.step = "company"
            response = f"It's a pleasure, {st.session_state.lead_data['Name']}! Which company are you with?"

    elif st.session_state.step == "company":
        st.session_state.lead_data["Company"] = clean_input(user_input, ["my company is ", "representing ", "from "])
        st.session_state.step = "phone"
        response = f"{st.session_state.lead_data['Company']}! Excellent. What's your contact number for the quote?"

    elif st.session_state.step == "phone":
        st.session_state.lead_data["Phone"] = user_input.strip()
        st.session_state.step = "email"
        response = "Thank you. And your work email address to send the 2027 catalog?"

    elif st.session_state.step == "email":
        st.session_state.lead_data["Email"] = user_input.lower().strip()
        st.session_state.step = "chat"
        save_to_sheets(st.session_state.lead_data) 
        response = f"Got it! I've sent your details to the team. How can I help you with our 2027 range today?"

    else:
        response = brain.get_answer(user_input, st.session_state.messages)

    # Output with Voice and Text
    with st.chat_message("assistant"):
        st.write(response)
        speak(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
