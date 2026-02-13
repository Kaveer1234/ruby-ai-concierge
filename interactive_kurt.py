import streamlit as st
import time
import requests
import re
from gtts import gTTS

# --- ROBUST INITIALIZATION ---
if "brain" not in st.session_state:
    try:
        from brain import CompanyBrain
        st.session_state.brain = CompanyBrain()
    except Exception as e:
        st.error(f"Ruby's brain is offline. Check brain.py. Error: {e}")
        st.session_state.brain = None

    st.session_state.chat_history = [{"role": "assistant",
                                      "content": "Good day! I am RUBY. To assist me in giving you a good service, I would require a few details about you. May I start with your name?"}]
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
    data["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        requests.post(url, data=data, timeout=8)
        return True
    except:
        return False

# --- SIDEBAR UI ---
with st.sidebar:
    st.markdown("### Ruby: Digital Concierge")
    video = "kurt_talking.mp4" if st.session_state.is_talking else "kurt_idle.mp4"
    st.video(video, autoplay=True, loop=True, muted=True)
    st.divider()
    st.markdown("### 📝 Captured Lead")
    st.write(f"**Name:** {st.session_state.lead_data['Name']}")
    st.write(f"**Company:** {st.session_state.lead_data['Company']}")
    st.write(f"**Phone:** {st.session_state.lead_data['Phone']}")
    st.write(f"**Email:** {st.session_state.lead_data['Email']}")

# --- MAIN CHAT AREA ---
st.title("Associated Industries (PTY) Ltd")
chat_box = st.container(height=400)

for msg in st.session_state.chat_history:
    chat_box.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Reply to Ruby..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    # Garbage Filter
    last_ruby = st.session_state.chat_history[-2]["content"].lower()
    garbage_list = ["my name is", "i am", "the company is", "we are", "ruby", "hi", "hello"]
    clean = prompt.lower()
    for word in garbage_list:
        clean = clean.replace(word, "")
    clean = clean.strip().title()

    # Regex Listeners
    phone_match = re.search(r'(\d{3}\s?\d{3}\s?\d{4}|\d{9,})', prompt)
    if phone_match: st.session_state.lead_data["Phone"] = phone_match.group(0)
    
    email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', prompt)
    if email_match: st.session_state.lead_data["Email"] = email_match.group(0)

    answer = ""

    # --- LEAD FLOW LOGIC ---
    if "your name" in last_ruby and not st.session_state.lead_data["Name"]:
        st.session_state.lead_data["Name"] = clean
        answer = f"Awesome, thanks {st.session_state.lead_data['Name']}! And which company are you with?"

    elif "which company" in last_ruby and not st.session_state.lead_data["Company"]:
        st.session_state.lead_data["Company"] = clean
        answer = "Got it. Just in case we get disconnected, what’s the best number to reach you on?"

    elif "reach you on" in last_ruby and not st.session_state.lead_data["Email"]:
        # Bridge to the Catalog
        answer = f"Perfect. And lastly, what is your work email address? I'll use this to send you our 2026 catalog and any quotes we discuss."

    # --- QUOTE TRIGGER ---
    elif any(x in prompt.lower() for x in ["quote", "price", "how much"]) and st.session_state.quote_step == 0:
        st.session_state.quote_step = 1
        answer = f"Certainly {st.session_state.lead_data['Name']}, I can help with a quote. Which product code are you interested in?"

    # --- BRAIN FALLBACK ---
    if not answer:
        if st.session_state.brain:
            answer = st.session_state.brain.get_answer(prompt, st.session_state.chat_history)
        else:
            answer = "I'm here to help! What can I tell you about our wildlife or corporate calendars?"

    st.session_state.last_text = answer
    st.session_state.chat_history.append({"role": "assistant", "content": answer})

    # Auto-Email Lead Capture
    if st.session_state.lead_data["Email"] and not st.session_state.mail_sent:
        send_to_office(st.session_state.lead_data, "NEW LEAD: " + st.session_state.lead_data["Name"])
        st.session_state.mail_sent = True

    # Voice Processing (Stripping Markdown)
    voice_text = re.sub(r'[\*\#\_]', '', answer)
    tts = gTTS(text=voice_text, lang='en', tld='co.uk')
    tts.save("response.mp3")
    st.session_state.is_talking = True
    st.rerun()

# --- VOICE & VIDEO SYNC ---
if st.session_state.is_talking:
    st.audio("response.mp3", autoplay=True)
    wait_time = (len(st.session_state.last_text) / 9) + 3.5
    time.sleep(min(wait_time, 20))
    st.session_state.is_talking = False
    st.rerun()
