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

# Force a unique key for the video to trigger a browser refresh [cite: 2026-02-11]
video_key = f"vid_{st.session_state.avatar}_{len(st.session_state.get('messages', []))}"
current_video_hex = get_video_base64(st.session_state.avatar)

st.markdown(f"""
<style>
header {{visibility: hidden;}}
[data-testid="stHeader"] {{display: none;}}
footer {{visibility: hidden;}}

/* FIXED HEADER: Locked at top */
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

/* THE CHAT ZONE: Scrollable middle ground [cite: 2026-02-11] */
.main .block-container {{
    padding-top: 400px !important; 
    padding-bottom: 120px !important;
}}

video {{
    border-radius: 15px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}}
</style>

<div class="ruby-header">
    <div style="font-family:sans-serif; font-weight:700; margin-bottom:10px;">RUBY – Associated Industries 2027</div>
    <video width="480" autoplay loop muted playsinline key="{video_key}">
        <source src="data:video/mp4;base64,{current_video_hex}" type="video/mp4">
    </video>
</div>
""", unsafe_allow_html=True)

# --- 2. LEAD CAPTURE & AUDIO ---
def save_to_sheets(data):
    # Google App Script Webhook [cite: 2026-02-12]
    webhook_url = "https://script.google.com/macros/s/AKfycbyItMfaLdTh1AomZBj6ZfLK-fDHOZC4o7jm7CFhJibg3AMxB61uXtOxVr7axV2Qn-CmPA/exec"
    try:
        data["Timestamp"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        # Use a timeout to prevent the app from hanging if the sheet is slow [cite: 2026-02-12]
        requests.post(webhook_url, json=data, timeout=5)
    except Exception as e:
        print(f"Sheet Error: {e}")

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
    st.session_state.avatar = "kurt_talking.mp4"
    
    # Sequential Lead Capture [cite: 2026-02-12]
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
        save_to_sheets(st.session_state.lead_data) # Finalize Lead [cite: 2026-02-12]
        response = "Perfect! I've logged those details. How can I help you today?"
    else:
        # Pass lead data as context so RUBY doesn't "forget" who she is talking to [cite: 2026-02-11]
        context = f"User: {st.session_state.lead_data['Name']} from {st.session_state.lead_data['Company']}. "
        response = brain.get_answer(context + user_input, st.session_state.messages)

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# Audio and Reset
if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant" and st.session_state.avatar == "kurt_talking.mp4":
    speak(st.session_state.messages[-1]["content"])
    time.sleep(1.5) # Allow speech to start
    st.session_state.avatar = "kurt_idle.mp4"
    st.rerun()
