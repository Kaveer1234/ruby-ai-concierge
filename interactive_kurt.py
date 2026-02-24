import streamlit as st
import requests
import base64
from datetime import datetime
from gtts import gTTS
import os
import time
from brain import CompanyBrain

# --- 1. UI SETUP: PINNED HEADER ---
st.set_page_config(page_title="RUBY - Associated Industries", layout="centered")

st.markdown("""
    <style>
    /* Hide default Streamlit headers */
    header { visibility: hidden; }
    [data-testid="stHeader"] { display: none; }
    
    /* THE LOCK: Absolute pinning of the video box */
    .video-lock-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 380px; 
        z-index: 9999;
        background-color: white;
        display: flex;
        flex-direction: column;
        align-items: center;
        border-bottom: 2px solid #e6e6e6;
        padding-top: 10px;
    }

    /* THE CHAT: Push down so messages don't start behind the video */
    .main .block-container {
        padding-top: 400px !important;
    }

    /* Mobile scaling */
    @media (max-width: 600px) {
        .video-lock-container { height: 260px; }
        .main .block-container { padding-top: 280px !important; }
        .stVideo { max-height: 160px; }
        .ruby-title { font-size: 1.2rem !important; }
    }

    .stVideo { width: 100%; max-width: 450px; border-radius: 12px; }
    .ruby-title { font-weight: bold; font-size: 1.8rem; color: #31333F; margin-bottom: 5px; }
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
    st.session_state.lead_data = {"Name": "", "Company": "", "Phone": "", "Email": "", "Product": "", "Quantity": "", "Colours": "", "Budget": ""}
    st.session_state.messages = []
    st.session_state.avatar = "kurt_idle.mp4"

brain = CompanyBrain()

# --- 4. THE VISUAL INTERFACE (ONE SINGLE DEFINITION) ---
video_placeholder = st.empty()

def update_avatar(video_filename):
    """Updates the pinned video container with the specified file."""
    with video_placeholder.container():
        st.markdown('<div class="video-lock-container">', unsafe_allow_html=True)
        st.markdown('<div class="ruby-title">RUBY - Associated Industries 2027</div>', unsafe_allow_html=True)
        try:
            # We use the file path directly for st.video to avoid data conversion overhead
            st.video(video_filename, autoplay=True, loop=True, muted=True)
        except Exception:
            st.warning(f"Could not load {video_filename}")
        st.markdown('</div>', unsafe_allow_html=True)

# Start with idle
update_avatar(st.session_state.avatar)

# Display Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# --- 5. LOGIC FLOW ---
if user_input := st.chat_input("Talk to RUBY..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Switch to talking video immediately
    update_avatar("kurt_talking.mp4")

    response = ""
    # Lead logic... (Name, Company, Phone, Email)
    if st.session_state.step == "name":
        if len(user_input.strip()) < 3 or user_input.lower() in ["hi", "hello", "hey"]:
            response = "Hello! I'm RUBY, your Digital Concierge. May I ask your name?"
        else:
            st.session_state.lead_data["Name"] = clean_input(user_input, ["my name is ", "i am "])
            st.session_state.step = "company"
            response = f"It's a pleasure, {st.session_state.lead_data['Name']}! Which company are you with?"
    
    # ... Rest of your lead logic ...
    elif st.session_state.step == "company":
        st.session_state.lead_data["Company"] = user_input.strip()
        st.session_state.step = "phone"
        response = f"{st.session_state.lead_data['Company']}! What is your contact number?"
    
    elif st.session_state.step == "phone":
        st.session_state.lead_data["Phone"] = user_input.strip()
        st.session_state.step = "email"
        response = "And your work email?"
        
    elif st.session_state.step == "email":
        st.session_state.lead_data["Email"] = user_input.strip()
        st.session_state.step = "chat"
        save_to_sheets(st.session_state.lead_data)
        response = "Thank you! How can I help you today?"
    else:
        response = brain.get_answer(user_input, st.session_state.messages)

    with st.chat_message("assistant"):
        st.write(response)
        speak(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Return to idle after a short delay for the voice to play
    time.sleep(2) 
    update_avatar("kurt_idle.mp4")
