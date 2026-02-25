import streamlit as st
import requests
import base64
from datetime import datetime
from gtts import gTTS
import os
import time
from brain import CompanyBrain

# --- 1. UI SETUP: THE SANDWICH LOCK ---
st.set_page_config(page_title="RUBY - Associated Industries", layout="wide")

def get_video_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except: return ""

if "avatar" not in st.session_state:
    st.session_state.avatar = "kurt_idle.mp4"

current_video_hex = get_video_base64(st.session_state.avatar)

# This CSS creates a fixed header and a scrollable chat area in the middle [cite: 2026-02-11]
st.markdown(f"""
<style>
header {{visibility: hidden;}}
[data-testid="stHeader"] {{display: none;}}
footer {{visibility: hidden;}}

/* FIXED HEADER */
.ruby-header {{
    position: fixed;
    top: 0; left: 0; width: 100%;
    height: 380px;
    background: white;
    z-index: 1000;
    display: flex; flex-direction: column; align-items: center;
    border-bottom: 2px solid #f0f2f6;
    padding-top: 10px;
}}

.ruby-title {{
    font-size: 1.2rem; font-weight: 700; color: #1E1E1E;
    margin-bottom: 5px; font-family: sans-serif;
}}

/* THE SCROLLABLE CHAT CHANNEL [cite: 2026-02-11] */
/* We target the main container and force it to stay between header and footer */
.main .block-container {{
    max-height: calc(100vh - 100px); 
    overflow-y: auto !important;
    padding-top: 400px !important; /* Starts below header */
    padding-bottom: 150px !important; /* Ends above chat input */
}}

/* Ensure the chat input stays pinned at the very bottom */
[data-testid="stChatInput"] {{
    position: fixed;
    bottom: 20px;
    z-index: 1001;
}}

video {{
    border-radius: 15px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}}
</style>

<div class="ruby-header">
    <div class="ruby-title">RUBY – Associated Industries 2027</div>
    <video width="480" autoplay loop muted playsinline key="{st.session_state.avatar}">
        <source src="data:video/mp4;base64,{current_video_hex}" type="video/mp4">
    </video>
</div>
""", unsafe_allow_html=True)

# --- 2. HELPER FUNCTIONS ---
def save_to_sheets(data):
    # Updated Webhook logic for reliability [cite: 2026-02-12]
    webhook_url = "https://script.google.com/macros/s/AKfycbyItMfaLdTh1AomZBj6ZfLK-fDHOZC4o7jm7CFhJibg3AMxB61uXtOxVr7axV2Qn-CmPA/exec"
    try:
        data["Timestamp"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        r = requests.post(webhook_url, json=data, timeout=10)
        return r.status_code == 200
    except: return False

def speak(text):
    tts = gTTS(text=text, lang='en', tld='co.za')
    tts.save("response.mp3")
    with open("response.mp3", "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
        st.markdown(f'<audio src="data:audio/mp3;base64,{b64}" autoplay="true"></audio>', unsafe_allow_html=True)
    os.remove("response.mp3")

# --- 3. INITIALIZATION ---
if "step" not in st.session_state:
    st.session_state.step = "name"
    st.session_state.lead_data = {"Name": "", "Company": "", "Phone": "", "Email": ""}
    st.session_state.messages = []

brain = CompanyBrain()

# --- 4. CHAT HISTORY ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# --- 5. CHAT LOGIC ---
if user_input := st.chat_input("Talk to RUBY..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.avatar = "kurt_talking.mp4" # Toggle video key [cite: 2026-02-11]
    
    # Lead Gen logic [cite: 2026-02-12]
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
        save_to_sheets(st.session_state.lead_data) # Send to Sheets [cite: 2026-02-12]
        response = "Perfect! I've logged those details. How can I help you today?"
    else:
        # Pass full history to brain to improve quote memory [cite: 2026-02-11]
        response = brain.get_answer(user_input, st.session_state.messages)

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# Audio and Reset
if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant" and st.session_state.avatar == "kurt_talking.mp4":
    speak(st.session_state.messages[-1]["content"])
    time.sleep(1.5)
    st.session_state.avatar = "kurt_idle.mp4"
    st.rerun()
