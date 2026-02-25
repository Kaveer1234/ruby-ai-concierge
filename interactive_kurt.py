import streamlit as st
import requests
import base64
from datetime import datetime
from gtts import gTTS
import os
import time
from brain import CompanyBrain

st.set_page_config(page_title="RUBY - Associated Industries", layout="wide")

def get_video_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except: return ""

# --- 1. PRELOAD VIDEOS (ONCE) ---
if "idle_hex" not in st.session_state:
    st.session_state.idle_hex = get_video_base64("kurt_idle.mp4")
    st.session_state.talk_hex = get_video_base64("kurt_talking.mp4")

if "avatar" not in st.session_state:
    st.session_state.avatar = "idle"

# Toggle visibility via CSS [cite: 2026-02-11]
idle_css = "display: block;" if st.session_state.avatar == "idle" else "display: none;"
talk_css = "display: block;" if st.session_state.avatar == "talking" else "display: none;"

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

.vid-stack {{
    width: 480px; height: 270px;
    position: relative;
    border-radius: 12px; overflow: hidden;
    background: black;
}}

#vid-idle {{ {idle_css} }}
#vid-talking {{ {talk_css} }}

video {{ width: 100%; height: 100%; object-fit: cover; }}
</style>

<div class="ruby-fixed-header">
    <div style="font-weight:700; margin-bottom:10px;">RUBY – Associated Industries 2027</div>
    <div class="vid-stack">
        <video id="vid-idle" autoplay loop muted playsinline>
            <source src="data:video/mp4;base64,{st.session_state.idle_hex}" type="video/mp4">
        </video>
        <video id="vid-talking" autoplay loop muted playsinline>
            <source src="data:video/mp4;base64,{st.session_state.talk_hex}" type="video/mp4">
        </video>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 2. THE BRAIN & DATA ---
def speak(text):
    tts = gTTS(text=text, lang='en', tld='co.za')
    tts.save("response.mp3")
    with open("response.mp3", "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
        st.markdown(f'<audio src="data:audio/mp3;base64,{b64}" autoplay="true"></audio>', unsafe_allow_html=True)
    os.remove("response.mp3")

if "step" not in st.session_state:
    st.session_state.step = "name"
    st.session_state.lead_data = {"Name": "", "Company": "", "Phone": "", "Email": ""}
    st.session_state.messages = []

brain = CompanyBrain()

# --- 3. CHAT DISPLAY ---
st.markdown('<div class="chat-scroll-zone">', unsafe_allow_html=True)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
st.markdown('</div>', unsafe_allow_html=True)

# --- 4. INTERACTION ---
if user_input := st.chat_input("Talk to RUBY..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.avatar = "talking" # Switch BEFORE processing [cite: 2026-02-11]
    
    # Lead Gen Flow
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
        response = "Perfect! How can I help you today?"
    else:
        ctx = f"User is {st.session_state.lead_data['Name']} from {st.session_state.lead_data['Company']}. "
        response = brain.get_answer(ctx + user_input, st.session_state.messages)

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# --- 5. AUDIO & RESET ---
if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant" and st.session_state.avatar == "talking":
    speak(st.session_state.messages[-1]["content"])
    time.sleep(4.0) # Length of talking animation
    st.session_state.avatar = "idle"
    st.rerun()
