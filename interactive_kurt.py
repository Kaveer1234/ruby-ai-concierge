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
        st.error(f"Ruby's brain is offline.")
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
    url = "https://formspree.io/f/xlgwgpla" # Your lead capture [cite: 2026-02-12]
    data["_subject"] = subject
    try: requests.post(url, data=data, timeout=8)
    except: pass

# --- UI ---
with st.sidebar:
    st.markdown("### Ruby: Digital Concierge")
    video = "kurt_talking.mp4" if st.session_state.is_talking else "kurt_idle.mp4"
    st.video(video, autoplay=True, loop=True, muted=True)
    st.divider()
    # Dynamic display of whoever is talking
    current_name = st.session_state.lead_data['Name'] or 'Guest'
    st.write(f"**Chatting with:** {current_name}") [cite: 2026-02-06, 2026-02-11]

st.title("Associated Industries (PTY) Ltd")
chat_box = st.container(height=400)
for msg in st.session_state.chat_history:
    chat_box.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Message Ruby..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    last_ruby = st.session_state.chat_history[-2]["content"].lower()
    
    # 1. DYNAMIC NAME CAPTURE
    if "your name" in last_ruby and not st.session_state.lead_data["Name"]:
        clean_name = prompt.lower()
        for word in ["hi", "hello", "my name is", "i am"]:
            clean_name = clean_name.replace(word, "")
        st.session_state.lead_data["Name"] = clean_name.strip().title()
        answer = f"It's a pleasure to meet you, {st.session_state.lead_data['Name']}! Which company are you representing today?" [cite: 2026-02-06, 2026-02-11]
    
    # ... (Rest of the Lead & Quote logic stays the same) ...
    # Ensure all Lead logic uses {st.session_state.lead_data['Name']} instead of 'Kaveer'
    
    elif "@" in prompt and not st.session_state.mail_sent:
        st.session_state.lead_data["Email"] = prompt
        answer = f"Perfect, {st.session_state.lead_data['Name']}. I've got your details! How can I help you today?" [cite: 2026-02-06, 2026-02-12]
        send_to_office(st.session_state.lead_data, "NEW LEAD: " + st.session_state.lead_data["Name"])
        st.session_state.mail_sent = True

    # 3. Brain Fallback
    if not answer:
        if st.session_state.brain:
            answer = st.session_state.brain.get_answer(prompt, st.session_state.chat_history)
        else:
            answer = "I'm right here! What can I tell you about our 2026 range?" [cite: 2026-02-09]

    st.session_state.last_text = answer
    st.session_state.chat_history.append({"role": "assistant", "content": answer})
    
    # Voice Gen with Dynamic Wait [cite: 2026-02-11]
    voice_text = re.sub(r'[\*\#\_]', '', answer)
    gTTS(text=voice_text, lang='en', tld='co.uk').save("response.mp3")
    st.session_state.is_talking = True
    st.rerun()

if st.session_state.is_talking:
    st.audio("response.mp3", autoplay=True)
    # GOLD STANDARD WAIT [cite: 2026-02-11]
    wait_time = (len(st.session_state.last_text) / 9) + 4.5
    time.sleep(min(wait_time, 25))
    st.session_state.is_talking = False
    st.rerun()
