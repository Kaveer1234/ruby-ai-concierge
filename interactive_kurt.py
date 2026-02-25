import streamlit as st
import requests
import base64
from datetime import datetime
from gtts import gTTS
import os
import time
from brain import CompanyBrain

# --- 1. UI SETUP: REMOVING THE WHITE BLOCK ---
st.set_page_config(page_title="RUBY - Associated Industries", layout="centered")

st.markdown("""
    <style>
    /* 1. Eliminate the default Streamlit padding at the very top */
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
    }
    header { visibility: hidden; }
    [data-testid="stHeader"] { display: none; }
    
    /* 2. THE LOCK: Positioned at the TRUE top (top: 0) */
    .video-lock-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 250px; /* Slimmer height to save space */
        z-index: 9999;
        background-color: white;
        display: flex;
        flex-direction: column;
        align-items: center;
        border-bottom: 1px solid #eee;
        margin: 0;
        padding: 0;
    }

    /* 3. THE CHAT: Adjusting exactly where the chat starts */
    .main .block-container {
        padding-top: 260px !important; 
    }

    /* Mobile scaling: Keeping it tight */
    @media (max-width: 600px) {
        .video-lock-container { height: 180px; }
        .main .block-container { padding-top: 190px !important; }
        .stVideo { max-height: 120px; width: auto; }
        .ruby-title { font-size: 0.9rem !important; margin-top: 2px; }
    }

    .stVideo { border-radius: 10px; margin-top: 2px; }
    .ruby-title { font-weight: bold; font-size: 1.2rem; color: #31333F; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HELPER FUNCTIONS ---
def clean_input(text, prefix_list):
    clean_text = text.strip()
    for prefix in prefix_list:
        if clean_text.lower().startswith(prefix):
            clean_text = clean_text[len(prefix):].strip()
    return clean_text.rstrip(".")

def save_to_sheets(data):
    webhook_url = "https://script.google.com/macros/s/AKfycbyItMfaLdTh1AomZBj6ZfLK-fDHOZC4o7jm7CFhJibg3AMxB61uXtOxVr7axV2 (etc)"
    try:
        data["Timestamp"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        requests.post(webhook_url, json=data)
    except Exception as e:
        st.error(f"Sync Error: {e}")

def speak(text):
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
    st.session_state.lead_data = {"Name": "", "Company": "", "Phone": "", "Email": ""}
    st.session_state.messages = []
    st.session_state.avatar = "kurt_idle.mp4"

brain = CompanyBrain()

# --- 4. THE VISUAL INTERFACE ---
video_placeholder = st.empty()

def update_avatar(video_filename):
    with video_placeholder.container():
        st.markdown('<div class="video-lock-container">', unsafe_allow_html=True)
        st.markdown('<div class="ruby-title">RUBY - Associated Industries 2027</div>', unsafe_allow_html=True)
        try:
            # We use the filename directly to keep it light [cite: 2026-02-11]
            st.video(video_filename, autoplay=True, loop=True, muted=True)
        except:
            st.warning("Avatar Loading...")
        st.markdown('</div>', unsafe_allow_html=True)

# Initial draw
update_avatar(st.session_state.avatar)

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# --- 5. LOGIC FLOW ---
if user_input := st.chat_input("Talk to RUBY..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # SWAP TO TALKING [cite: 2026-02-11]
    update_avatar("kurt_talking.mp4")

    # (Lead Logic simplified for brevity)
    if st.session_state.step == "name":
        st.session_state.lead_data["Name"] = user_input
        st.session_state.step = "company"
        response = f"Hi {user_input}! Which company are you with?"
    elif st.session_state.step == "company":
        st.session_state.lead_data["Company"] = user_input
        st.session_state.step = "chat"
        save_to_sheets(st.session_state.lead_data)
        response = "Got it! How can I help you today?"
    else:
        response = brain.get_answer(user_input, st.session_state.messages)

    with st.chat_message("assistant"):
        st.write(response)
        speak(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # REVERT TO IDLE [cite: 2026-02-11]
    time.sleep(2) 
    update_avatar("kurt_idle.mp4")
