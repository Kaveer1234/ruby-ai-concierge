import streamlit as st
import requests
import base64
from datetime import datetime
from gtts import gTTS
import os
import time
from brain import CompanyBrain

# Load Groq API key from Streamlit secrets
os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]

# --- 1. UI SETUP: THE PHYSICAL BARRIER ---
st.set_page_config(page_title="RUBY - Associated Industries", layout="wide")


def get_video_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""


if "avatar" not in st.session_state:
    st.session_state.avatar = "kurt_idle.mp4"

current_video_hex = get_video_base64(st.session_state.avatar)

st.markdown(f"""
<style>
/* 1. Reset everything to zero [cite: 2026-02-11] */
header, [data-testid="stHeader"], footer {{display: none !important;}}
.main .block-container {{padding: 0 !important; max-width: 100% !important;}}

/* 2. THE HEADER: Physically occupies the top 400px [cite: 2026-02-11] */
.ruby-fixed-header {{
    position: fixed;
    top: 0; left: 0; width: 100%;
    height: 400px;
    background: white;
    z-index: 9999; /* Highest priority */
    display: flex; flex-direction: column; align-items: center;
    border-bottom: 3px solid #f0f2f6;
    padding-top: 10px;
}}

/* 3. THE SCROLL ZONE: Starts 2mm (8px) below the header [cite: 2026-02-11] */
.chat-scroll-zone {{
    margin-top: 408px; /* Header height + 8px gap */
    height: calc(100vh - 520px); /* Strictly limited height */
    overflow-y: auto;
    padding: 0 15% 100px 15%; /* Side padding for centered look */
    display: flex;
    flex-direction: column;
}}

/* 4. CHAT INPUT: Pinned to the very bottom [cite: 2026-02-11] */
div[data-testid="stChatInput"] {{
    position: fixed;
    bottom: 20px !important;
    z-index: 10000;
}}

video {{ border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.15); }}
</style>

<div class="ruby-fixed-header">
    <div style="font-weight:700; font-size:1.1rem; margin-bottom:10px;">RUBY – Associated Industries 2027</div>
    <video width="480" autoplay loop muted playsinline key="{st.session_state.avatar}">
        <source src="data:video/mp4;base64,{current_video_hex}" type="video/mp4">
    </video>
</div>
""", unsafe_allow_html=True)


# --- 2. LOGIC & LEAD GEN ---
def save_to_sheets(data):
    # Ensure leads are captured for everyone who talks [cite: 2026-02-12]
    webhook_url = "https://script.google.com/macros/s/AKfycbyItMfaLdTh1AomZBj6ZfLK-fDHOZC4o7jm7CFhJibg3AMxB61uXtOxVr7axV2Qn-CmPA/exec"
    try:
        data["Timestamp"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        requests.post(webhook_url, json=data, timeout=5)
    except:
        pass


def speak(text):
    tts = gTTS(text=text, lang='en', tld='co.za')
    tts.save("response.mp3")
    with open("response.mp3", "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
        st.markdown(f'<audio src="data:audio/mp3;base64,{b64}" autoplay="true"></audio>', unsafe_allow_html=True)
    os.remove("response.mp3")


# --- 3. STATE & BRAIN ---
if "step" not in st.session_state:
    st.session_state.step = "name"
    st.session_state.lead = {
        "Name":"",
        "Company":"",
        "Phone":"",
        "Email":"",
        "Quote Product":"",
        "Quote Quantity":"",
        "Quote Colours":"",
        "Quote Budget":""
    }

    greeting = "Hi there! I'm RUBY from Associated Industries. It's lovely to meet you. May I ask your name?"

    st.session_state.messages.append({"role":"assistant","content":greeting})

    st.session_state.messages = []

brain = CompanyBrain()

# --- 4. THE VAULTED CHAT DISPLAY [cite: 2026-02-11] ---
# Wrapping the messages in a manual div to force the vertical boundary
st.markdown('<div class="chat-scroll-zone">', unsafe_allow_html=True)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
st.markdown('</div>', unsafe_allow_html=True)

# --- 5. INTERACTION ---
if user_input := st.chat_input("Talk to RUBY..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.avatar = "kurt_talking.mp4"

    # Lead Gen Flow [cite: 2026-02-12]
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
        save_to_sheets(st.session_state.lead_data)
        response = "Perfect! I've saved your details. How can I help you today?"
    else:
        # Pass lead data as context so she knows who she is talking to [cite: 2026-02-11]
        context = f"User: {st.session_state.lead_data['Name']} from {st.session_state.lead_data['Company']}. "
        response = brain.get_answer(context + user_input, st.session_state.messages)

    elif step == "quote_product":

        st.session_state.lead["Quote Product"] = user
        st.session_state.step = "quote_quantity"
        response = "Great choice. Roughly how many units are you looking for?"


    elif step == "quote_quantity":

        st.session_state.lead["Quote Quantity"] = user
        st.session_state.step = "quote_colours"
        response = "Nice. Do you know how many overprint colours you'd like?"


    elif step == "quote_colours":

        st.session_state.lead["Quote Colours"] = user
        st.session_state.step = "quote_budget"
        response = "Got it. If you have a rough budget in mind you're welcome to share it — it helps us recommend the best option."


    elif step == "quote_budget":

        st.session_state.lead["Quote Budget"] = user

        save_to_sheets(st.session_state.lead)

        st.session_state.step = "chat"

        response = "Fantastic. I'll pass that to our sales team and they'll prepare a quote for you shortly."


    else:

        quote_words = ["quote","price","cost","quotation"]

        if any(w in user.lower() for w in quote_words):

            st.session_state.step = "quote_product"

            response = "Sure! I'd be happy to help with a quote. What product are you interested in?"

        else:

            context = f"User {st.session_state.lead['Name']} from {st.session_state.lead['Company']} asks: "

            response = brain.get_answer(context + user, st.session_state.messages)


    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# Audio and Reset Logic
if st.session_state.messages and st.session_state.messages[-1][
    "role"] == "assistant" and st.session_state.avatar == "kurt_talking.mp4":
    speak(st.session_state.messages[-1]["content"])
    time.sleep(1.5)
    st.session_state.avatar = "kurt_idle.mp4"
    st.rerun()

