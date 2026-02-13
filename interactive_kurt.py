import streamlit as st
import time
import requests
import re
from gtts import gTTS

# --- INITIALIZATION ---
if "brain" not in st.session_state:
    try:
        from brain import CompanyBrain
        st.session_state.brain = CompanyBrain()
    except Exception as e:
        st.error(f"Ruby's brain is offline. Error: {e}")
        st.session_state.brain = None

    st.session_state.chat_history = [{"role": "assistant", "content": "Good day! I am RUBY. To assist me in giving you a good service, I would require a few details about you. May I start with your name?"}]
    st.session_state.lead_data = {"Name": "", "Company": "", "Phone": "", "Email": ""}
    st.session_state.quote_data = {"Product": "", "Quantity": "", "Colours": "", "Budget": ""}
    st.session_state.quote_step = 0
    st.session_state.is_talking = False
    st.session_state.last_text = ""
    st.session_state.mail_sent = False

st.set_page_config(page_title="Associated Industries", layout="wide")

def send_to_office(data, subject):
    url = "https://formspree.io/f/xlgwgpla"
    data["_subject"] = subject
    try: requests.post(url, data=data, timeout=8)
    except: pass

# --- UI & LOGIC ---
with st.sidebar:
    st.markdown("### Ruby: Digital Concierge")
    video = "kurt_talking.mp4" if st.session_state.is_talking else "kurt_idle.mp4"
    st.video(video, autoplay=True, loop=True, muted=True)
    st.write(f"**Lead:** {st.session_state.lead_data['Name']}")

st.title("Associated Industries (PTY) Ltd")
chat_box = st.container(height=400)
for msg in st.session_state.chat_history:
    chat_box.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Reply to Ruby..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    last_ruby = st.session_state.chat_history[-2]["content"].lower()
    clean = prompt.lower().replace("my name is", "").replace("i am", "").strip().title()
    
    # Listeners
    if re.search(r'\d{9,}', prompt): st.session_state.lead_data["Phone"] = prompt
    if "@" in prompt: st.session_state.lead_data["Email"] = prompt

    answer = ""

    # 1. Capture Flow
    if "your name" in last_ruby and not st.session_state.lead_data["Name"]:
        st.session_state.lead_data["Name"] = clean
        answer = f"Awesome, thanks {st.session_state.lead_data['Name']}! And which company are you with?"
    elif "which company" in last_ruby and not st.session_state.lead_data["Company"]:
        st.session_state.lead_data["Company"] = clean
        answer = "Got it. What’s the best number to reach you on?"
    elif "reach you on" in last_ruby and not st.session_state.lead_data["Email"]:
        answer = "Perfect. And lastly, what is your work email address?"
    elif "@" in prompt and not st.session_state.mail_sent:
        answer = f"Thanks {st.session_state.lead_data['Name']}, I've got everything! How can I help you with our 2026 range or branch details today?"
        send_to_office(st.session_state.lead_data, "NEW LEAD")
        st.session_state.mail_sent = True

    # 2. Quote Logic
    elif any(x in prompt.lower() for x in ["quote", "price"]) and st.session_state.quote_step == 0:
        st.session_state.quote_step = 1
        answer = "I can help with that. Which product code (e.g., M82)?"
    elif st.session_state.quote_step > 0:
        # (Standard quote steps 1-4 here...)
        st.session_state.quote_step = 0 # Placeholder for brevity
        answer = "I've noted those quote details!"

    # 3. Brain
    if not answer:
        if st.session_state.brain:
            answer = st.session_state.brain.get_answer(prompt, st.session_state.chat_history)
        else:
            answer = "I'm here! What can I tell you about our calendars?"

    st.session_state.last_text = answer
    st.session_state.chat_history.append({"role": "assistant", "content": answer})
    voice_text = re.sub(r'[\*\#\_]', '', answer)
    gTTS(text=voice_text, lang='en', tld='co.uk').save("response.mp3")
    st.session_state.is_talking = True
    st.rerun()

if st.session_state.is_talking:
    st.audio("response.mp3", autoplay=True)
    time.sleep((len(st.session_state.last_text) / 9) + 4)
    st.session_state.is_talking = False
    st.rerun()
