import streamlit as st
import time
import requests
import re
from gtts import gTTS
from brain import CompanyBrain

# --- INITIALIZATION ---
if "brain" not in st.session_state:
    st.session_state.brain = CompanyBrain()
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
    u_name = st.text_input("Name", value=st.session_state.lead_data["Name"])
    u_comp = st.text_input("Company", value=st.session_state.lead_data["Company"])
    u_phon = st.text_input("Phone", value=st.session_state.lead_data["Phone"])
    u_mail = st.text_input("Email", value=st.session_state.lead_data["Email"])

    if st.session_state.quote_step > 0:
        st.divider()
        st.markdown("### 📊 Quote Requirements")
        st.info(f"Product: {st.session_state.quote_data['Product']}\n\nQty: {st.session_state.quote_data['Quantity']}\n\nColours: {st.session_state.quote_data['Colours']}\n\nBudget: {st.session_state.quote_data['Budget']}")

# --- MAIN CHAT AREA ---
st.title("Associated Industries (PTY) Ltd")
chat_box = st.container(height=400)

for msg in st.session_state.chat_history:
    chat_box.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Reply to Ruby..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    # --- GLOBAL PATTERN RECOGNITION ---
    last_ruby = st.session_state.chat_history[-2]["content"].lower()
    garbage = r'(my name is|i am|the company is|we are|is email|is my email|ruby|hi|hello|is my phone|is my name|is name)'
    clean = re.sub(garbage, '', prompt, flags=re.I).strip()
    refusal = any(word in clean.lower() for word in ["don't", "dont", "not", "refuse", "skip", "no", "rather not"])

    # 1. Global Phone & Email Check
    phone_match = re.search(r'(\d{3}\s?\d{3}\s?\d{4}|\d{9,})', prompt)
    if phone_match:
        st.session_state.lead_data["Phone"] = phone_match.group(0)

    email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', prompt)
    if email_match:
        st.session_state.lead_data["Email"] = email_match.group(0)

    # 2. Contextual Lead Capture (With Safety Filter)
    if "your name" in last_ruby and not st.session_state.lead_data["Name"]:
        st.session_state.lead_data["Name"] = clean.title()
    elif "company" in last_ruby and not st.session_state.lead_data["Company"]:
        # Don't save "quote" as a company name
        if not any(x in prompt.lower() for x in ["quote", "price", "how much"]):
            st.session_state.lead_data["Company"] = "N/A (Refused)" if refusal else clean.title()
    elif "phone number" in last_ruby and refusal and not st.session_state.lead_data["Phone"]:
        st.session_state.lead_data["Phone"] = "Refused"

    # 3. Quote Workflow
    if any(x in prompt.lower() for x in ["quote", "price", "how much"]) and st.session_state.quote_step == 0:
        st.session_state.quote_step = 1
        answer = f"Certainly {st.session_state.lead_data['Name']}, I can assist with that. Which product are you interested in (M82, Diaries, Gifts, etc.)?"
    elif st.session_state.quote_step == 1:
        st.session_state.quote_data["Product"] = clean
        st.session_state.quote_step = 2
        answer = "Great. How many units are you looking to order?"
    elif st.session_state.quote_step == 2:
        st.session_state.quote_data["Quantity"] = clean
        st.session_state.quote_step = 3
        answer = "For branding purposes, how many Overprint Colours are required for your logo?"
    elif st.session_state.quote_step == 3:
        st.session_state.quote_data["Colours"] = clean
        st.session_state.quote_step = 4
        answer = "Lastly, do you have a total budget in mind? (You can say 'No' if not available)."
    elif st.session_state.quote_step == 4:
        st.session_state.quote_data["Budget"] = "N/A" if refusal else clean
        st.session_state.quote_step = 5
        final_data = {**st.session_state.lead_data, **st.session_state.quote_data}
        send_to_office(final_data, "FULL QUOTE REQUEST: " + st.session_state.lead_data["Name"])
        answer = "Perfect! I have sent those details to our sales team. They will be in touch shortly. Is there anything else I can help with?"
    else:
        answer = st.session_state.brain.get_answer(prompt, st.session_state.chat_history)

    st.session_state.last_text = answer
    st.session_state.chat_history.append({"role": "assistant", "content": answer})

    # Lead Auto-Discovery (Sends basic info if they don't finish a quote)
    if st.session_state.lead_data["Email"] and not st.session_state.mail_sent and st.session_state.quote_step < 5:
        send_to_office(st.session_state.lead_data, "General Lead Captured: " + st.session_state.lead_data["Name"])
        st.session_state.mail_sent = True

    tts = gTTS(text=answer, lang='en', tld='co.uk')
    tts.save("response.mp3")
    st.session_state.is_talking = True
    st.rerun()

# --- VOICE PLAYBACK & DYNAMIC WAIT ---
if st.session_state.is_talking:
    st.audio("response.mp3", autoplay=True)
    wait = min(len(st.session_state.last_text) / 15, 6)
    time.sleep(wait)
    st.session_state.is_talking = False
    st.rerun()
