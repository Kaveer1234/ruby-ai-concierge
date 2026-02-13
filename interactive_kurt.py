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
    st.divider()
    st.write(f"**Chatting with:** {st.session_state.lead_data['Name'] or 'Guest'}")

st.title("Associated Industries (PTY) Ltd")
chat_box = st.container(height=400)
for msg in st.session_state.chat_history:
    chat_box.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Message Ruby..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    last_ruby = st.session_state.chat_history[-2]["content"].lower()
    clean = prompt.lower().replace("my name is", "").replace("i am", "").strip().title()
    
    # Listeners for Data
    if re.search(r'\d{9,}', prompt): st.session_state.lead_data["Phone"] = prompt
    if "@" in prompt: st.session_state.lead_data["Email"] = prompt

    answer = ""

    # 1. HUMAN LEAD FLOW
    if "your name" in last_ruby and not st.session_state.lead_data["Name"]:
        st.session_state.lead_data["Name"] = clean
        answer = f"It's a pleasure to meet you, {st.session_state.lead_data['Name']}! Which company are you representing today?"

    elif "which company" in last_ruby and not st.session_state.lead_data["Company"]:
        st.session_state.lead_data["Company"] = clean
        answer = f"Ah, {clean}! A fantastic organization. Just in case our connection drops, what's the best number to reach you on?"

    elif "reach you on" in last_ruby and not st.session_state.lead_data["Email"]:
        answer = "I've got that. And finally, your work email address? I'll use it to send you our 2026 collection."

    elif "@" in prompt and not st.session_state.mail_sent:
        answer = f"Perfect, {st.session_state.lead_data['Name']}. I've got your details safely stored! How can I help you today? I can provide a quote or tell you about our 2026 range."
        send_to_office(st.session_state.lead_data, "NEW LEAD")
        st.session_state.mail_sent = True

    # 2. SOULFUL QUOTE WORKFLOW
    elif any(x in prompt.lower() for x in ["quote", "price"]) and st.session_state.quote_step == 0:
        st.session_state.quote_step = 1
        answer = "I'd be absolutely delighted to help with a quote! Which specific product or diary code are you interested in?"

    elif st.session_state.quote_step == 1:
        st.session_state.quote_data["Product"] = prompt
        st.session_state.quote_step = 2
        answer = f"The {prompt}? Excellent choice. How many units were you looking to order for your team?"

    elif st.session_state.quote_step == 2:
        st.session_state.quote_data["Quantity"] = prompt
        st.session_state.quote_step = 3
        answer = f"Got it, {prompt} units. And for the branding, are we looking at a single-color logo or something more vibrant?"

    elif st.session_state.quote_step == 3:
        st.session_state.quote_data["Colours"] = prompt
        st.session_state.quote_step = 4
        answer = "Almost there! Do you have a rough budget in mind? It helps me ensure we give you the best possible value."

    elif st.session_state.quote_step == 4:
        st.session_state.quote_data["Budget"] = prompt
        st.session_state.quote_step = 0 # Reset for the Brain to take over
        send_to_office({**st.session_state.lead_data, **st.session_state.quote_data}, "FULL QUOTE")
        answer = "Wonderful! I've sent that request over to our specialists. They'll be in touch very soon. Is there anything else you'd like to know, perhaps about our Durban branch?"

    # 3. BRAIN FALLBACK
    if not answer:
        if st.session_state.brain:
            answer = st.session_state.brain.get_answer(prompt, st.session_state.chat_history)
        else:
            answer = "I'm right here! Would you like to hear about our 2026 calendars or our branch locations?"

    st.session_state.last_text = answer
    st.session_state.chat_history.append({"role": "assistant", "content": answer})
    
    # Voice Generation (UK English for a more sophisticated concierge feel)
    voice_text = re.sub(r'[\*\#\_]', '', answer)
    gTTS(text=voice_text, lang='en', tld='co.uk').save("response.mp3")
    st.session_state.is_talking = True
    st.rerun()

if st.session_state.is_talking:
    st.audio("response.mp3", autoplay=True)
    wait_time = (len(st.session_state.last_text) / 9) + 4.5
    time.sleep(min(wait_time, 25))
    st.session_state.is_talking = False
    st.rerun()
