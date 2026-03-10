import streamlit as st
import requests
import base64
from datetime import datetime
from gtts import gTTS
import os
import time
from brain import CompanyBrain

# --- 1. SETUP & CONFIG ---
os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
st.set_page_config(page_title="RUBY - Associated Industries", layout="wide")

@st.cache_data
def get_video_base64(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        return ""
    except:
        return ""

# --- 2. INITIALIZE SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi there! I'm RUBY from Associated Industries. It's lovely to meet you. May I ask your name?"}]

if "step" not in st.session_state:
    st.session_state.step = "name"
    st.session_state.avatar = "idle"  # Current state: idle, thinking, or talking
    st.session_state.lead_data = {
        "Name":"", "Company":"", "Phone":"", "Email":"",
        "Quote Product":"", "Quote Quantity":"", "Quote Colours":"", "Quote Budget":""
    }

# Pre-load all videos into memory once for instant swapping
if "video_idle" not in st.session_state:
    st.session_state.video_idle = get_video_base64("kurt_idle.mp4")
    st.session_state.video_talking = get_video_base64("kurt_talking.mp4")
    st.session_state.video_thinking = get_video_base64("kurt_thinking.mp4")

# --- 3. UI LAYOUT & FIXED HEADER ---
# Pick the right video hex based on the current state
if st.session_state.avatar == "talking":
    current_video_hex = st.session_state.video_talking
elif st.session_state.avatar == "thinking":
    current_video_hex = st.session_state.video_thinking
else:
    current_video_hex = st.session_state.video_idle

st.markdown(f"""
<style>
header, [data-testid="stHeader"], footer {{display:none}}
.main .block-container {{padding:0; max-width:100%}}
.ruby-fixed-header {{
    position:fixed; top:0; left:0; width:100%; height:400px;
    background:white; z-index:9999; display:flex; 
    flex-direction:column; align-items:center; border-bottom:3px solid #f0f2f6; padding-top:10px;
}}
.chat-scroll-zone {{
    margin-top:408px; height:calc(100vh - 520px); overflow-y:auto;
    padding:0 15% 100px 15%; display:flex; flex-direction:column;
}}
div[data-testid="stChatInput"] {{ position:fixed; bottom:20px; z-index:10000; }}
video {{ border-radius:12px; box-shadow:0 4px 20px rgba(0,0,0,0.15); }}
</style>

<div class="ruby-fixed-header">
    <div style="font-weight:700;font-size:1.1rem;margin-bottom:10px;">RUBY – Associated Industries 2027</div>
    <video width="480" autoplay loop muted playsinline key="{st.session_state.avatar}">
        <source src="data:video/mp4;base64,{current_video_hex}" type="video/mp4">
    </video>
</div>
""", unsafe_allow_html=True)

# --- 4. FUNCTIONS ---
def save_to_sheets(data):
    webhook_url = "https://script.google.com/macros/s/AKfycbyItMfaLdTh1AomZBj6ZfLK-fDHOZC4o7jm7CFhJibg3AMxB61uXtOxVr7axV2Qn-CmPA/exec"
    try:
        data["Timestamp"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        requests.post(webhook_url, json=data, timeout=5)
    except: pass

def speak(text):
    try:
        tts = gTTS(text=text, lang="en", tld="co.za")
        tts.save("voice.mp3")
        with open("voice.mp3","rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        st.markdown(f'<audio src="data:audio/mp3;base64,{b64}" autoplay></audio>', unsafe_allow_html=True)
        os.remove("voice.mp3")
    except: pass

brain = CompanyBrain()

# --- 5. CHAT DISPLAY ---
st.markdown('<div class="chat-scroll-zone">', unsafe_allow_html=True)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
st.markdown('</div>', unsafe_allow_html=True)

# --- 6. INTERACTION LOGIC ---
if user := st.chat_input("Talk to RUBY..."):
    st.session_state.messages.append({"role":"user","content":user})
    
    # Switch to thinking video while the computer works
    st.session_state.avatar = "thinking"
    st.rerun()

# This part runs only after the user has typed something and the app reruns
if st.session_state.messages[-1]["role"] == "user":
    user_text = st.session_state.messages[-1]["content"]
    step = st.session_state.step
    response = ""

    # Lead capture & Quote flow logic
    if step == "name":
        clean_name = user_text.lower().replace("hi","").replace("hello","").replace("my name is","").replace("i am","").replace("i'm","").strip().title()
        st.session_state.lead_data["Name"] = clean_name
        st.session_state.step = "company"
        response = f"Nice to meet you {clean_name}! Which company are you with?"
    elif step == "company":
        st.session_state.lead_data["Company"] = user_text
        st.session_state.step = "phone"
        response = "Got it. What is your telephone number?"
    elif step == "phone":
        st.session_state.lead_data["Phone"] = user_text
        st.session_state.step = "email"
        response = "And your company email address?"
    elif step == "email":
        st.session_state.lead_data["Email"] = user_text
        st.session_state.step = "chat"
        save_to_sheets(st.session_state.lead_data)
        response = "Perfect! I've logged those details. How can I help you today?"
    elif "quote" in user_text.lower() or "price" in user_text.lower():
        st.session_state.step = "quote_product"
        response = "Sure thing. What product would you like quoted?"
    elif step == "quote_product":
        st.session_state.lead_data["Quote Product"] = user_text
        st.session_state.step = "quote_quantity"
        response = "Great. Roughly how many units are you looking for?"
    elif step == "quote_quantity":
        st.session_state.lead_data["Quote Quantity"] = user_text
        st.session_state.step = "quote_colours"
        response = "Do you know how many overprint colours you'd like?"
    elif step == "quote_colours":
        st.session_state.lead_data["Quote Colours"] = user_text
        st.session_state.step = "quote_budget"
        response = "If you have a rough budget in mind you're welcome to share it."
    elif step == "quote_budget":
        st.session_state.lead_data["Quote Budget"] = user_text
        st.session_state.step = "chat"
        save_to_sheets(st.session_state.lead_data)
        response = f"Perfect {st.session_state.lead_data['Name']}. I've captured the enquiry for your {st.session_state.lead_data['Quote Product']}. Sales will send a quote to {st.session_state.lead_data['Email']} shortly."
    else:
        context = f"Customer: {st.session_state.lead_data['Name']} from {st.session_state.lead_data['Company']}."
        response = brain.get_answer(context + user_text, st.session_state.messages)

    # Now Ruby is ready to "Talk"
    st.session_state.messages.append({"role":"assistant","content":response})
    st.session_state.avatar = "talking"
    st.rerun()

# --- 7. VOICE & RESET ---
if st.session_state.messages[-1]["role"] == "assistant" and st.session_state.avatar == "talking":
    speak(st.session_state.messages[-1]["content"])
    time.sleep(1.0)
    st.session_state.avatar = "idle"
    st.rerun()

