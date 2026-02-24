import streamlit as st
import requests
import base64
from datetime import datetime
from gtts import gTTS
import os
from brain import CompanyBrain

# --- 1. UI SETUP (Simplified & Stable) ---
st.set_page_config(page_title="RUBY - Associated Industries", layout="centered")

st.markdown("""
    <style>
    /* Clean up the top space without breaking the layout */
    .block-container { padding-top: 2rem !important; }
    
    /* Ensure the video looks good on all screens */
    .stVideo { width: 100%; border-radius: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
    
    /* Make the Title stand out */
    .ruby-header { 
        text-align: center; 
        color: #31333F; 
        font-family: sans-serif; 
        font-weight: bold; 
        font-size: 24px; 
        margin-bottom: 20px; 
    }
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
    # Your confirmed Version 2 URL
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

brain = CompanyBrain()

# --- 4. THE VISUAL INTERFACE (Safe Method) ---
# We use a standard container here to avoid the "White Box" overlap
header_container = st.container()
with header_container:
    st.markdown('<div class="ruby-header">RUBY - Associated Industries 2027</div>', unsafe_allow_html=True)
    try:
        # Re-linking your GitHub file
        video_file = open('kurt_idle.mp4', 'rb') 
        video_bytes = video_file.read()
        st.video(video_bytes)
    except FileNotFoundError:
        st.warning("Video file 'kurt_idle.mp4' not found.")
    st.divider()

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
