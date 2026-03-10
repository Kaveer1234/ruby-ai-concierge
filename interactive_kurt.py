import streamlit as st
from brain import CompanyBrain
from datetime import datetime
import pyttsx3
import os

st.set_page_config(page_title="RUBY - Associated Industries", layout="wide")

# -----------------------------
# Offline TTS engine
# -----------------------------
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()  # blocks until finished

# -----------------------------
# Google Sheets webhook
# -----------------------------
import requests

def save_to_sheets(data):
    webhook_url = "https://script.google.com/macros/s/YOUR_WEBHOOK_ID/exec"
    try:
        data["Timestamp"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        requests.post(webhook_url, json=data, timeout=5)
    except:
        pass

# -----------------------------
# Session State
# -----------------------------
if "messages" not in st.session_state:
    greeting = "Hi there! I'm RUBY from Associated Industries. It's lovely to meet you. May I ask your name?"
    st.session_state.messages = [{"role":"assistant","content":greeting}]
    st.session_state.avatar = "kurt_idle.mp4"

if "step" not in st.session_state:
    st.session_state.step = "name"
    st.session_state.lead_data = {
        "Name":"","Company":"","Phone":"","Email":"",
        "Quote Product":"","Quote Quantity":"","Quote Colours":"","Quote Budget":""
    }

brain = CompanyBrain()

# -----------------------------
# Fixed header with avatar
# -----------------------------
def get_video_base64(file_path):
    try:
        with open(file_path,"rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return ""

avatar_hex = get_video_base64(st.session_state.avatar)

st.markdown(f"""
<style>
header, [data-testid="stHeader"], footer {{display:none}}
.main .block-container {{padding:0; max-width:100%}}
.ruby-fixed-header {{
position:fixed; top:0; left:0; width:100%; height:400px;
background:white; z-index:9999; display:flex; flex-direction:column;
align-items:center; border-bottom:3px solid #f0f2f6; padding-top:10px;
}}
.chat-scroll-zone {{
margin-top:408px; height:calc(100vh - 520px);
overflow-y:auto; padding:0 15% 100px 15%; display:flex; flex-direction:column;
}}
div[data-testid="stChatInput"] {{position:fixed; bottom:20px; z-index:10000;}}
video {{border-radius:12px; box-shadow:0 4px 20px rgba(0,0,0,0.15);}}
</style>

<div class="ruby-fixed-header">
<div style="font-weight:700;font-size:1.1rem;margin-bottom:10px;">
RUBY – Associated Industries 2027
</div>

<video width="480" autoplay loop muted playsinline>
<source src="data:video/mp4;base64,{avatar_hex}" type="video/mp4">
</video>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Chat display
# -----------------------------
st.markdown('<div class="chat-scroll-zone">', unsafe_allow_html=True)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Chat input
# -----------------------------
if user := st.chat_input("Talk to RUBY..."):
    st.session_state.messages.append({"role":"user","content":user})
    step = st.session_state.step

    # -----------------------------
    # Lead capture
    # -----------------------------
    if step == "name":
        name = user.lower().replace("my name is","").replace("i am","").replace("i'm","").strip().title()
        st.session_state.lead_data["Name"] = name
        st.session_state.step = "company"
        response = f"Nice to meet you {name}! Which company are you with?"

    elif step == "company":
        st.session_state.lead_data["Company"] = user
        st.session_state.step = "phone"
        response = "Got it. What is your telephone number?"

    elif step == "phone":
        st.session_state.lead_data["Phone"] = user
        st.session_state.step = "email"
        response = "And your company email address?"

    elif step == "email":
        st.session_state.lead_data["Email"] = user
        st.session_state.step = "chat"
        save_to_sheets(st.session_state.lead_data)
        response = "Perfect! I've logged those details. How can I help you today?"

    # -----------------------------
    # Quote flow
    # -----------------------------
    elif "quote" in user.lower() or "price" in user.lower():
        st.session_state.step = "quote_product"
        response = "Sure thing. What product would you like quoted?"

    elif step == "quote_product":
        st.session_state.lead_data["Quote Product"] = user
        st.session_state.step = "quote_quantity"
        response = "Great. Roughly how many units are you looking for?"

    elif step == "quote_quantity":
        st.session_state.lead_data["Quote Quantity"] = user
        st.session_state.step = "quote_colours"
        response = "Do you know how many overprint colours you'd like?"

    elif step == "quote_colours":
        st.session_state.lead_data["Quote Colours"] = user
        st.session_state.step = "quote_budget"
        response = "If you have a rough budget in mind you're welcome to share it."

    elif step == "quote_budget":
        st.session_state.lead_data["Quote Budget"] = user
        st.session_state.step = "chat"
        save_to_sheets(st.session_state.lead_data)
        response = f"""
Perfect {st.session_state.lead_data['Name']}.

I've captured the details for your {st.session_state.lead_data['Quote Product']} enquiry.

Our sales team will prepare a formal quotation and send it to {st.session_state.lead_data['Email']} shortly.
"""

    # -----------------------------
    # Normal AI chat
    # -----------------------------
    else:
        context = f"Customer name: {st.session_state.lead_data['Name']}\nCompany: {st.session_state.lead_data['Company']}\n"
        response = brain.get_answer(context + user, st.session_state.messages)

    st.session_state.messages.append({"role":"assistant","content":response})

    # -----------------------------
    # Play talking video + TTS
    # -----------------------------
    st.session_state.avatar = "kurt_talking.mp4"
    st.video(st.session_state.avatar, start_time=0)
    speak(response)
    st.session_state.avatar = "kurt_idle.mp4"
    st.video(st.session_state.avatar, start_time=0)

    st.rerun()
