import streamlit as st
import requests
import base64
from datetime import datetime
from gtts import gTTS
import os
import time
from brain import CompanyBrain

# --- 1. UI SETUP: THE FLOATING OVERLAY ---
st.set_page_config(page_title="RUBY - Associated Industries", layout="centered")

st.markdown("""
    <style>
    /* 1. Make the background of the main app transparent at the top */
    .stApp {
        background-color: white;
    }
    
    /* 2. Hide all default Streamlit headers and extra space */
    header { visibility: hidden; }
    [data-testid="stHeader"] { display: none; }
    [data-testid="stAppViewBlockContainer"] {
        padding-top: 0px !important;
    }

    /* 3. THE FLOATING FRONT LAYER: This sits ON TOP of the chat */
    .video-floating-front {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 240px; 
        /* This ensures it is in front of the chat bubbles */
        z-index: 1000000; 
        background-color: white;
        display: flex;
        flex-direction: column;
        align-items: center;
        border-bottom: 2px solid #f0f2f6;
        padding-top: 10px;
    }

    /* 4. THE CHAT LAYER: Give it enough room so it doesn't start behind the video */
    .main .block-container {
        padding-top: 260px !important; 
    }

    /* Mobile adjustments for the front layer */
    @media (max-width: 600px) {
        .video-floating-front { height: 180px; }
        .main .block-container { padding-top: 200px !important; }
        .stVideo { max-height: 120px; }
        .ruby-title { font-size: 1rem !important; }
    }

    .stVideo { border-radius: 15px; box-shadow: 0px 4px 15px rgba(0,0,0,0.1); }
    .ruby-title { font-weight: bold; font-size: 1.3rem; color: #1f1f1f; margin-bottom: 5px; }
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
    webhook_url = "https://script.google.com/macros/s/AKfycbyItMfaLdTh1AomZBj6ZfLK-fDHOZC4o7jm7CFhJibg3AMxB61uXtOxVr7axV2Qn-CmPA/exec"
    try:
        data["Timestamp"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        requests.post(webhook_url, json=data)
    except Exception as e:
        pass

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

# --- 4. THE VISUAL INTERFACE (Front Overlay) ---
video_placeholder = st.empty()

def update_avatar(video_filename):
    with video_placeholder.container():
        # Using the new high-priority CSS class
        st.markdown('<div class="video-floating-front">', unsafe_allow_html=True)
        st.markdown('<div class="ruby-title">RUBY - Associated Industries 2027</div>', unsafe_allow_html=True)
        try:
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

    update_avatar("kurt_talking.mp4")

    if st.session_state.step == "name":
        st.session_state.lead_data["Name"] = user_input
        st.session_state.step = "company"
        response = f"Hello {user_input}! Which company are you with?"
    elif st.session_state.step == "company":
        st.session_state.lead_data["Company"] = user_input
        st.session_state.step = "chat"
        save_to_sheets(st.session_state.lead_data)
        response = "Great! How can I help you with our 2027 range today?"
    else:
        response = brain.get_answer(user_input, st.session_state.messages)

    with st.chat_message("assistant"):
        st.write(response)
        speak(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    time.sleep(2) 
    update_avatar("kurt_idle.mp4")
