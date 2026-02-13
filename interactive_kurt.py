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
    st.markdown("### 📝 Captured Details")
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

    # Garbage Filter logic for names/companies
    last_ruby = st.session_state.chat_history[-2]["content"].lower()
    garbage_list = ["my name is", "i am", "the company is", "we are", "ruby", "hi", "hello"]
    clean = prompt.lower()
    for word in garbage_list:
        clean = clean.replace(word, "")
    clean = clean.strip().title()

    # Regex Listeners for Phone/Email
    phone_match = re.search(r'(\d{3}\s?\d{3}\s?\d{4}|\d{9,})', prompt)
    if phone_match: st.session_state.lead_data["Phone"] = phone_match.group(0)
    
    email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', prompt)
    if email_match: st.session_state.lead_data["Email"] = email_match.group(0)

    answer = ""

    # --- 1. LEAD FLOW ---
    if "your name" in last_ruby and not st.session_state.lead_data["Name"]:
        st.session_state.lead_data["Name"] = clean
        answer = f"Awesome, thanks {st.session_state.lead_data['Name']}! And which company are you with?"

    elif "which company" in last_ruby and not st.session_state.lead_data["Company"]:
        st.session_state.lead_data["Company"] = clean
        answer = "Got it. Just in case we get disconnected, what’s the best number to reach you on?"

    elif "reach you on" in last_ruby and not st.session_state.lead_data["Email"]:
        answer = "Perfect. And lastly, what is your work email address? I'll use this to send you our 2026 catalog and any quotes we discuss."

    # --- 2. QUOTE WORKFLOW ---
    elif any(x in prompt.lower() for x in ["quote", "price", "how much"]) and st.session_state.quote_step == 0:
        st.session_state.quote_step = 1
        answer = f"Certainly {st.session_state.lead_data['Name']}, I can help with a quote. Which product code or item are you interested in (e.g., M82, Diaries)?"

    elif st.session_state.quote_step == 1:
        st.session_state.quote_data["Product"] = prompt
        st.session_state.quote_step = 2
        answer = f"Got it, {prompt}. How many units are you looking to order?"

    elif st.session_state.quote_step == 2:
        st.session_state.quote_data["Quantity"] = prompt
        st.session_state.quote_step = 3
        answer = "And how many Overprint Colours are required for your logo branding?"

    elif st.session_state.quote_step == 3:
        st.session_state.quote_data["Colours"] = prompt
        st.session_state.quote_step = 4
        answer = "Lastly, do you have a total budget in mind? You can say 'No' if you're not sure."

    elif st.session_state.quote_step == 4:
        st.session_state.quote_data["Budget"] = prompt
        # Send full quote data
        final_data = {**st.session_state.lead_data, **st.session_state.quote_data}
        send_to_office(final_data, "FULL QUOTE: " + st.session_state.lead_data["Name"])
        # RESET logic so she can answer address questions next
        st.session_state.quote_step = 0 
        answer = "Perfect! I have sent all those details to our sales team at sales@brabys.co.za. They will be in touch shortly. Is there anything else I can help with today?"

    # --- 3. BRAIN FALLBACK ---
    if not answer:
        if st.session_state.brain:
            # If we just captured the email, the very next response should be from the brain
            answer = st.session_state.brain.get_answer(prompt, st.session_state.chat_history)
        else:
            answer = "I'm here to help! What can I tell you about our 2026 range or our branch locations?"

    st.session_state.last_text = answer
    st.session_state.chat_history.append({"role": "assistant", "content": answer})

    # Auto-Email Trigger for Lead Capture (triggered once Email is present)
    if st.session_state.lead_data["Email"] and not st.session_state.mail_sent:
        send_to_office(st.session_state.lead_data, "NEW LEAD: " + st.session_state.lead_data["Name"])
        st.session_state.mail_sent = True

    # Voice Cleanup & Playback
    voice_text = re.sub(r'[\*\#\_]', '', answer)
    tts = gTTS(text=voice_text, lang='en', tld='co.uk')
    tts.save("response.mp3")
    st.session_state.is_talking = True
    st.rerun()

# --- VOICE & VIDEO SYNC ---
if st.session_state.is_talking:
    st.audio("response.mp3", autoplay=True)
    # Calibrated wait time for natural speech finish
    wait_time = (len(st.session_state.last_text) / 9) + 4
    time.sleep(min(wait_time, 22))
    st.session_state.is_talking = False
    st.rerun()
