import streamlit as st
import requests
import base64
from datetime import datetime
from gtts import gTTS
import os
import time
from brain import CompanyBrain

# --- 1. UI SETUP: PINNED COMPACT HEADER ---
st.set_page_config(page_title="RUBY - Associated Industries", layout="centered")

st.markdown("""
    <style>
    /* Hide default Streamlit headers and menu */
    header { visibility: hidden; }
    [data-testid="stHeader"] { display: none; }
    
    /* THE LOCK: Smaller, pinned container at the absolute top */
    .video-lock-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 280px; 
        z-index: 9999;
        background-color: white;
        display: flex;
        flex-direction: column;
        align-items: center;
        border-bottom: 2px solid #e6e6e6;
        padding-top: 5px;
    }

    /* THE CHAT: Push down adjusted for smaller avatar */
    .main .block-container {
        padding-top: 300px !important; 
        max-width: 700px !important;
    }

    /* Mobile scaling: Even more compact for phone view */
    @media (max-width: 600px) {
        .video-lock-container { height: 180px; }
        .main .block-container { padding-top: 200px !important; }
        .stVideo { max-height: 110px; } 
        .ruby-title { font-size: 1rem !important; }
    }

    /* Avatar size control */
    .stVideo { width: 100%; max-width: 300px; border-radius: 10px; }
    .ruby-title { font-weight: bold; font-size: 1.4rem; color: #31333F; margin-bottom: 2px; }
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
    # Sends lead information to Google Sheets via Webhook [cite: 2026-02-12]
    webhook_url = "https://script.google.com/macros/s/AKfycbyItMfaLdTh1AomZBj6ZfLK-fDHOZC4o7jm7CFhJibg3AMxB61uXtOxVr7axV2Qn-CmPA/exec"
    try:
        data["Timestamp"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        requests.post(webhook_url, json=data)
    except Exception as e:
        st.error(f"Sync Error: {e}")

def speak(text):
    # Uses gTTS for voice engine [cite: 2026-02-09]
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
    st.session_state.lead_data = {"Name": "", "Company": "", "Phone": "", "Email": "", "Product": "", "Quantity": "", "Colours": "", "Budget": ""}
    st.session_state.messages = []
    st.session_state.avatar = "kurt_idle.mp4"

brain = CompanyBrain()

# --- 4. THE VISUAL INTERFACE (Single Definition) ---
video_placeholder = st.empty()

def update_avatar(video_filename):
    """Updates the pinned video container without page refresh."""
    with video_placeholder.container():
        st.markdown('<div class="video-lock-container">', unsafe_allow_html=True)
        st.markdown('<div class="ruby-title">RUBY - Associated Industries 2027</div>', unsafe_allow_html=True)
        try:
            # Stable video loading [cite: 2026-02-11]
            st.video(video_filename, autoplay=True, loop=True, muted=True)
        except Exception:
            st.warning("Loading Avatar...")
        st.markdown('</div>', unsafe_allow_html=True)

# Initial draw: Start in idle mode
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

    # SWAP TO TALKING VIDEO IMMEDIATELY [cite: 2026-02-11]
    update_avatar("kurt_talking.mp4")

    response = ""
    
    # Lead Collection Logic [cite: 2026-02-12]
    if st.session_state.step == "name":
        if len(user_input.strip()) < 3 or user_input.lower() in ["hi", "hello", "hey"]:
            response = "Hello! I'm RUBY, your Digital Concierge. Before we look at our 2027 range, may I ask your name?"
        else:
            st.session_state.lead_data["Name"] = clean_input(user_input, ["my name is ", "hi my name is ", "i am "])
            st.session_state.step = "company"
            response = f"It's a pleasure, {st.session_state.lead_data['Name']}! Which company are you with?"

    elif st.session_state.step == "company":
        st.session_state.lead_data["Company"] = clean_input(user_input, ["my company is ", "representing ", "from "])
        st.session_state.step = "phone"
        response = f"{st.session_state.lead_data['Company']}! Excellent. What's your contact number for the quote?"

    elif st.session_state.step == "phone":
        st.session_state.lead_data["Phone"] = user_input.strip()
        st.session_state.step = "email"
        response = "Thank you. And your work email address to send the 2027 catalog?"

    elif st.session_state.step == "email":
        st.session_state.lead_data["Email"] = user_input.lower().strip()
        st.session_state.step = "chat"
        save_to_sheets(st.session_state.lead_data) 
        response = f"Got it! I've sent your details to the team. How can I help you with our 2027 range today?"

    else:
        # Standard AI Brain response
        response = brain.get_answer(user_input, st.session_state.messages)

    # Output with Voice and Text
    with st.chat_message("assistant"):
        st.write(response)
        speak(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # RETURN TO IDLE after speaking [cite: 2026-02-11]
    time.sleep(2) 
    update_avatar("kurt_idle.mp4")
