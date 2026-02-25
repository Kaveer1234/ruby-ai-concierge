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
    /* 1. Hide the default Streamlit header bar completely */
    header { visibility: hidden; }
    [data-testid="stHeader"] { display: none; }
    
    /* 2. Remove all top padding from the main app container */
    [data-testid="stAppViewBlockContainer"] {
        padding-top: 0px !important;
        margin-top: 0px !important;
    }

    /* 3. THE FLOATING WINDOW: Pin it to the absolute top of the screen */
    .floating-header {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 260px; 
        background-color: white;
        /* Massive z-index to stay on top of all chat elements */
        z-index: 999999; 
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        border-bottom: 2px solid #f0f2f6;
        box-shadow: 0px 2px 10px rgba(0,0,0,0.05);
    }

    /* 4. THE CHAT SPACE: Create a permanent gap so chat starts below the floating window */
    .main .block-container {
        padding-top: 280px !important; 
    }

    /* Mobile adjustments: Smaller floating window for phones */
    @media (max-width: 600px) {
        .floating-header { height: 190px; }
        .main .block-container { padding-top: 210px !important; }
        .stVideo { max-height: 120px; width: auto; }
        .ruby-title { font-size: 1.1rem !important; }
    }

    .stVideo { border-radius: 12px; }
    .ruby-title { font-weight: bold; font-size: 1.5rem; color: #1f1f1f; margin-bottom: 8px; }
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
    except:
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

# --- 4. THE VISUAL INTERFACE (Floating Front Window) ---
# We put this placeholder inside a div with the 'floating-header' class
header_placeholder = st.empty()

def update_avatar(video_filename):
    with header_placeholder.container():
        st.markdown('<div class="floating-header">', unsafe_allow_html=True)
        st.markdown('<div class="ruby-title">RUBY - Associated Industries 2027</div>', unsafe_allow_html=True)
        try:
            # Removed dynamic keys to prevent TypeError glitch [cite: 2026-02-11]
            st.video(video_filename, autoplay=True, loop=True, muted=True)
        except:
            st.warning("Avatar loading...")
        st.markdown('</div>', unsafe_allow_html=True)

# Initial draw
update_avatar(st.session_state.avatar)

# Display Chat History (This now starts BELOW the floating window)
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
