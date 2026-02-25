import streamlit as st
import requests
import base64
from datetime import datetime
from gtts import gTTS
import os
import time
from brain import CompanyBrain

# --- 1. UI SETUP: INTEGRATED HEADER LOCK ---
st.set_page_config(page_title="RUBY - Associated Industries", layout="wide")

st.markdown("""
<style>
header {visibility: hidden;}
[data-testid="stHeader"] {display: none;}
footer {visibility: hidden;}

/* THE INTEGRATED LOCK: Putting title and video in one fixed box */
.ruby-header {
    position: fixed;
    top: 0; left: 0; width: 100%; height: 280px; /* Increased height for both */
    backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px);
    background: rgba(255,255,255,0.85);
    z-index: 9999;
    display: flex; flex-direction: column; align-items: center; justify-content: flex-start;
    border-bottom: 1px solid rgba(0,0,0,0.06);
    padding-top: 15px;
}

.ruby-title { 
    font-size: 1.3rem; 
    font-weight: 600; 
    margin-bottom: 10px; 
    color: #333;
}

/* Push chat content below the new integrated height */
.main .block-container {
    padding-top: 300px !important;
    padding-bottom: 110px !important;
}

/* Mobile Adjustments */
@media (max-width: 768px) {
    .ruby-header { height: 220px; }
    .main .block-container { padding-top: 240px !important; }
    .ruby-title { font-size: 1rem; }
}
</style>
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

# --- 4. RENDER INTEGRATED HEADER ---
# We use st.empty() to act as a window into our fixed CSS div
header_window = st.empty()

with header_window.container():
    # Opening the fixed CSS wrapper
    st.markdown('<div class="ruby-header">', unsafe_allow_html=True)
    st.markdown('<div class="ruby-title">RUBY – Associated Industries 2027</div>', unsafe_allow_html=True)
    
    # Rendering video directly inside the fixed area
    # Note: Streamlit wraps st.video in its own div, but CSS will keep it pinned
    cols = st.columns([1, 1.5, 1]) # Narrower video container
    with cols[1]:
        st.video(st.session_state.avatar, autoplay=True, loop=True, muted=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- 5. CHAT LOGIC ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if user_input := st.chat_input("Talk to RUBY..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Switch to talking avatar
    st.session_state.avatar = "kurt_talking.mp4"
    
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
        save_to_sheets(st.session_state.lead_data)
        response = "Perfect! I've logged those details. How can I help you today?"
    else:
        response = brain.get_answer(user_input, st.session_state.messages)

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# Audio and Idle Reset
if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant" and st.session_state.avatar == "kurt_talking.mp4":
    speak(st.session_state.messages[-1]["content"])
    time.sleep(1.5)
    st.session_state.avatar = "kurt_idle.mp4"
    st.rerun()
