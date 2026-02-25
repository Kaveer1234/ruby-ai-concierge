import streamlit as st
import requests
import base64
from datetime import datetime
from gtts import gTTS
import os
import time
from brain import CompanyBrain

# --- 1. UI SETUP: THE IRON VAULT ---
st.set_page_config(page_title="RUBY - Associated Industries", layout="wide")

# Function to get video data [cite: 2026-02-11]
def get_video_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except: return ""

# --- 2. INITIALIZATION ---
if "step" not in st.session_state:
    st.session_state.step = "name"
    st.session_state.lead_data = {"Name": "", "Company": "", "Phone": "", "Email": ""}
    st.session_state.messages = []
    st.session_state.avatar = "kurt_idle.mp4" # Default state

brain = CompanyBrain()

# Encode the current avatar right now
current_video_hex = get_video_base64(st.session_state.avatar)
# Unique key for the HTML element [cite: 2026-02-11]
video_key = f"vid_{st.session_state.avatar}_{len(st.session_state.messages)}"

st.markdown(f"""
<style>
header, [data-testid="stHeader"], footer {{display: none !important;}}
.main .block-container {{padding: 0 !important; max-width: 100% !important;}}

.ruby-fixed-header {{
    position: fixed;
    top: 0; left: 0; width: 100%;
    height: 400px;
    background: white;
    z-index: 9999;
    display: flex; flex-direction: column; align-items: center;
    border-bottom: 3px solid #f0f2f6;
    padding-top: 10px;
}}

.chat-scroll-zone {{
    margin-top: 408px;
    height: calc(100vh - 520px);
    overflow-y: auto;
    padding: 0 15% 100px 15%;
    display: flex;
    flex-direction: column;
}}

div[data-testid="stChatInput"] {{
    position: fixed;
    bottom: 20px !important;
    z-index: 10000;
}}

video {{ border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.15); }}
</style>

<div class="ruby-fixed-header">
    <div style="font-weight:700; font-size:1.1rem; margin-bottom:10px;">RUBY – Associated Industries 2027</div>
    <video width="480" autoplay loop muted playsinline key="{video_key}">
        <source src="data:video/mp4;base64,{current_video_hex}" type="video/mp4">
    </video>
</div>
""", unsafe_allow_html=True)

# --- 3. CORE FUNCTIONS ---
def speak(text):
    tts = gTTS(text=text, lang='en', tld='co.za')
    tts.save("response.mp3")
    with open("response.mp3", "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
        st.markdown(f'<audio src="data:audio/mp3;base64,{b64}" autoplay="true"></audio>', unsafe_allow_html=True)
    os.remove("response.mp3")

# --- 4. CHAT DISPLAY ---
st.markdown('<div class="chat-scroll-zone">', unsafe_allow_html=True)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
st.markdown('</div>', unsafe_allow_html=True)

# --- 5. THE INTERACTION LOOP ---
if user_input := st.chat_input("Talk to RUBY..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # 1. IMMEDIATE SWAP TO TALKING [cite: 2026-02-11]
    st.session_state.avatar = "kurt_talking.mp4"
    
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
        response = "Perfect! I've logged those details. How can I help you today?"
    else:
        context = f"User: {st.session_state.lead_data['Name']} from {st.session_state.lead_data['Company']}. "
        response = brain.get_answer(context + user_input, st.session_state.messages)

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# --- 6. AUDIO & RESET ---
if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant" and st.session_state.avatar == "kurt_talking.mp4":
    speak(st.session_state.messages[-1]["content"])
    
    # Keep talking for a moment while the audio plays
    time.sleep(3.0) 
    
    # RESET TO IDLE [cite: 2026-02-11]
    st.session_state.avatar = "kurt_idle.mp4"
    st.rerun()
