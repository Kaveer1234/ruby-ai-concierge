import streamlit as st
import requests
import base64
from datetime import datetime
from gtts import gTTS
import os
import time
from brain import CompanyBrain

# --- 1. UI SETUP: THE STICKER LOCK ---
st.set_page_config(page_title="RUBY - Associated Industries", layout="wide")

# We convert the video to a data URI so it can be played inside a raw HTML div
def get_video_base64(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

video_base64 = get_video_base64(st.session_state.get("avatar", "kurt_idle.mp4"))

st.markdown(f"""
<style>
/* Hide standard UI */
header {{visibility: hidden;}}
[data-testid="stHeader"] {{display: none;}}
footer {{visibility: hidden;}}

/* THE STICKER: This is pinned to the browser window, NOT the page [cite: 2026-02-11] */
.fixed-header {{
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 380px;
    background-color: white;
    z-index: 999999; /* Higher than anything else */
    display: flex;
    flex-direction: column;
    align-items: center;
    border-bottom: 2px solid #f0f2f6;
    padding-top: 10px;
}}

.ruby-title {{
    font-size: 1.2rem;
    font-weight: 700;
    color: #1E1E1E;
    margin-bottom: 10px;
    font-family: sans-serif;
}}

/* Push chat content down so it doesn't hide behind the sticker [cite: 2026-02-11] */
.main .block-container {{
    padding-top: 400px !important;
}}

video {{
    border-radius: 10px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}}
</style>

<div class="fixed-header">
    <div class="ruby-title">RUBY – Associated Industries 2027</div>
    <video width="450" autoplay loop muted playsinline>
        <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
    </video>
</div>
""", unsafe_allow_html=True)

# --- 2. HELPER FUNCTIONS ---
def save_to_sheets(data):
    webhook_url = "https://script.google.com/macros/s/AKfycbyItMfaLdTh1AomZBj6ZfLK-fDHOZC4o7jm7CFhJibg3AMxB61uXtOxVr7axV2Qn-CmPA/exec"
    try:
        data["Timestamp"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        requests.post(webhook_url, json=data)
    except: pass

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
    st.session_state.avatar = "kurt_idle.mp4"

brain = CompanyBrain()

# --- 4. CHAT HISTORY ---
# The chat bubbles will now scroll and disappear UNDER the fixed header
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# --- 5. CHAT LOGIC ---
if user_input := st.chat_input("Talk to RUBY..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.avatar = "kurt_talking.mp4"
    
    # Lead Gen Flow [cite: 2026-02-12]
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
        save_to_sheets(st.session_state.lead_data)
        response = "Perfect! How can I help you today?"
    else:
        response = brain.get_answer(user_input, st.session_state.messages)

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# Audio and Reset
if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant" and st.session_state.avatar == "kurt_talking.mp4":
    speak(st.session_state.messages[-1]["content"])
    time.sleep(1.5)
    st.session_state.avatar = "kurt_idle.mp4"
    st.rerun()
