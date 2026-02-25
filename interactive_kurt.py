import streamlit as st
import requests
import base64
from datetime import datetime
from gtts import gTTS
import os
import time
from brain import CompanyBrain

# --- 1. UI SETUP: SETTING J (STABLE) ---
st.set_page_config(page_title="RUBY - Associated Industries", layout="wide")

def get_video_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except: return ""

if "avatar" not in st.session_state:
    st.session_state.avatar = "kurt_idle.mp4"

# Generate a unique key based on the current time to force-refresh the video element
video_id = f"ruby_vid_{int(time.time())}" 
current_video_hex = get_video_base64(st.session_state.avatar)

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
    <video width="480" autoplay loop muted playsinline key="{video_id}">
        <source src="data:video/mp4;base64,{current_video_hex}" type="video/mp4">
    </video>
</div>
""", unsafe_allow_html=True)

# --- 2. LEAD CAPTURE & AUDIO ---
def speak(text):
    tts = gTTS(text=text, lang='en', tld='co.za')
    tts.save("response.mp3")
    with open("response.mp3", "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
        # Adding an ID to the audio to ensure it triggers too
        st.markdown(f'<audio src="data:audio/mp3;base64,{b64}" autoplay="true" id="ruby_audio"></audio>', unsafe_allow_html=True)
    os.remove("response.mp3")

# --- 3. INITIALIZATION ---
if "step" not in st.session_state:
    st.session_state.step = "name"
    st.session_state.lead_data = {"Name": "", "Company": "", "Phone": "", "Email": ""}
    st.session_state.messages = []

brain = CompanyBrain()

# --- 4. CHAT DISPLAY ---
st.markdown('<div class="chat-scroll-zone">', unsafe_allow_html=True)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
st.markdown('</div>', unsafe_allow_html=True)

# --- 5. THE INTERACTION LOOP ---
if user_input := st.chat_input("Talk to RUBY..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # 1. SET TO TALKING IMMEDIATELY
    st.session_state.avatar = "kurt_talking.mp4"
    
    # Process Logic [cite: 2026-02-12]
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
        # (Webhook call would go here)
        response = "Perfect! I've logged those details. How can I help you today?"
    else:
        context = f"User: {st.session_state.lead_data['Name']} from {st.session_state.lead_data['Company']}. "
        response = brain.get_answer(context + user_input, st.session_state.messages)

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# --- 6. AUDIO TRIGGER & RESET ---
# This part handles the "Talking -> Idle" transition
if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant" and st.session_state.avatar == "kurt_talking.mp4":
    # Start the voice
    speak(st.session_state.messages[-1]["content"])
    
    # Pause for a brief moment so the talking video is seen [cite: 2026-02-11]
    # Adjust this time based on average message length if needed
    time.sleep(2.0) 
    
    # Reset to Idle and rerun to update the video element
    st.session_state.avatar = "kurt_idle.mp4"
    st.rerun()
