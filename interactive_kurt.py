import streamlit as st
import requests
import base64
from datetime import datetime
from gtts import gTTS
import os
import time
from brain import CompanyBrain

# --- 1. MOBILE & DESKTOP UI SETUP (The Final Fix) ---
st.set_page_config(page_title="RUBY - Associated Industries", layout="centered")

st.markdown("""
    <style>
    /* 1. Force the Header to stay at the absolute top */
    .stApp {
        margin-top: 0px;
    }
    header { visibility: hidden; }
    
    /* 2. Create the Locked Video Box */
    .video-lock-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 380px; /* Space for Title + Video */
        background-color: white;
        z-index: 9999;
        display: flex;
        flex-direction: column;
        align-items: center;
        border-bottom: 2px solid #e6e6e6;
        padding-top: 10px;
    }

    /* 3. Push the Chat content down so it doesn't hide behind the video */
    .main .block-container {
        padding-top: 400px !important;
    }

    /* 4. Mobile Overrides to keep it compact */
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

# --- 4. THE VISUAL INTERFACE (Dynamic Placeholder with Fixed Lock) ---
# This placeholder stays pinned to the top of the browser window
video_placeholder = st.empty()

def update_avatar(video_filename):
    # This 'with' block ensures the content goes INTO the empty placeholder [cite: 2026-02-11]
    with video_placeholder.container():
        # This div uses the 'video-lock-container' CSS from Section 1 [cite: 2026-02-11]
        st.markdown('<div class="video-lock-container">', unsafe_allow_html=True)
        st.markdown('<div class="ruby-title">RUBY - Associated Industries 2027</div>', unsafe_allow_html=True)
        try:
            video_file = open(video_filename, 'rb')
            video_bytes = video_file.read()
            # We add a key so Streamlit tracks this specific video instance [cite: 2026-02-11]
            st.video(video_bytes)
        except FileNotFoundError:
            st.warning(f"File {video_filename} not found.")
        st.markdown('</div>', unsafe_allow_html=True)

# Show initial idle video ONLY ONCE here
if "avatar" not in st.session_state:
    st.session_state.avatar = "kurt_idle.mp4"

update_avatar(st.session_state.avatar)

def update_avatar(video_filename):
    with video_placeholder.container():
        st.markdown('<div class="video-lock">', unsafe_allow_html=True)
        st.title("RUBY - Associated Industries 2027")
        try:
            video_file = open(video_filename, 'rb')
            video_bytes = video_file.read()
            st.video(video_bytes)
        except FileNotFoundError:
            st.warning(f"File {video_filename} not found.")
        st.markdown('</div>', unsafe_allow_html=True)

# Show initial idle video
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

    response = ""

    # Set to talking video [cite: 2026-02-11]
    update_avatar("kurt_talking.mp4")

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
        response = brain.get_answer(user_input, st.session_state.messages)

    # Output with Voice and Text
    with st.chat_message("assistant"):
        st.write(response)
        speak(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Return to idle after speaking [cite: 2026-02-11]
    time.sleep(1) # Small delay for the audio to finish
    update_avatar("kurt_idle.mp4")


