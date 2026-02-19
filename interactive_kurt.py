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
        st.error("Ruby's brain is offline.")
        st.session_state.brain = None

    st.session_state.chat_history = [{"role": "assistant", "content": "Good day! I am RUBY. To assist me in giving you a good service, I would require a few details about you. May I start with your name?"}]
    st.session_state.lead_data = {"Name": "", "Company": "", "Phone": "", "Email": ""}
    st.session_state.quote_data = {"Product": "", "Quantity": "", "Colours": "", "Budget": ""}
    st.session_state.quote_step = 0
    st.session_state.is_talking = False
    st.session_state.last_text = ""
    st.session_state.mail_sent = False

st.set_page_config(page_title="Associated Industries", layout="wide")

# --- UPDATED GOOGLE SHEETS FUNCTION ---
def send_to_office(data, subject):
    # Your Unique Google Web App URL [cite: 2026-02-09]
    url = "https://script.google.com/macros/s/AKfycbyPQB6SIQS836QcdVXwGbWkNtKkkbX2V-eHYteW4ghbVgYbkC-bJ7XZUNmtKnD_qihTIg/exec"
    try: 
        # Sending as params ensures the 'doPost(e)' script catches every field [cite: 2026-02-12]
        requests.post(url, params=data, timeout=10)
    except: 
        pass

# --- UI ---
with st.sidebar:
    st.markdown("### Ruby: Digital Concierge")
    video = "kurt_talking.mp4" if st.session_state.is_talking else "kurt_idle.mp4"
    st.video(video, autoplay=True, loop=True, muted=True)
    st.divider()
    current_name = st.session_state.lead_data['Name'] or 'Guest'
    st.write(f"**Chatting with:** {current_name}")

st.title("Associated Industries (PTY) Ltd")
chat_box = st.container(height=400)
for msg in st.session_state.chat_history:
    chat_box.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Message Ruby..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    last_ruby = st.session_state.chat_history[-2]["content"].lower()
    
    answer = ""
    
    # --- INTELLIGENT CLEANING ---
    clean = prompt.lower()
    
    if "your name" in last_ruby:
        for word in ["hi", "hello", "my name is", "i am", "is my name", "call me", "name is"]:
            clean = clean.replace(word, "")
    
    if "which company" in last_ruby:
        for word in ["my company is", "the company is", "representing", "we are", "is the company", "from", "company name is", "company is"]:
            clean = clean.replace(word, "")
    
    if "reach you on" in last_ruby:
        for word in ["my number is", "the number is", "reach me at", "phone number is", "cell number is"]:
            clean = clean.replace(word, "")
    
    clean = clean.strip().title()

    # Listeners
    if re.search(r'\d{9,}', prompt): 
        phone_digits = re.sub(r'\D', '', prompt)
        st.session_state.lead_data["Phone"] = phone_digits
    
    if "@" in prompt: st.session_state.lead_data["Email"] = prompt

    # --- CONVERSATIONAL LOGIC ---
    if "your name" in last_ruby and not st.session_state.lead_data["Name"]:
        st.session_state.lead_data["Name"] = clean
        answer = f"It's a pleasure to meet you, {st.session_state.lead_data['Name']}! Which company are you representing today?"

    elif "which company" in last_ruby and not st.session_state.lead_data["Company"]:
        st.session_state.lead_data["Company"] = clean
        answer = f"Ah, {st.session_state.lead_data['Company']}! A fantastic organization. Just in case our connection drops, what's the best number to reach you on?"

    elif "reach you on" in last_ruby and not st.session_state.lead_data["Email"]:
        answer = "I've got that. And finally, your work email address? I'll use it to send your 2027 catalog and quotes."

    elif "@" in prompt and not st.session_state.mail_sent:
        st.session_state.lead_data["Email"] = prompt
        cat_url = "https://www.associatedindustries.co.za/catalog2027.pdf"
        answer = f"Perfect, {st.session_state.lead_data['Name']}. I've got your details! You can view our 2027 range here: {cat_url}. How can I help you today?"
        # Trigger Google Sheet Save [cite: 2026-02-12]
        send_to_office(st.session_state.lead_data, "NEW LEAD")
        st.session_state.mail_sent = True

    # --- QUOTE WORKFLOW ---
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
        answer = f"Got it, {prompt} units. For the branding, are we looking at a single-color logo or something more vibrant like foiling?"

    elif st.session_state.quote_step == 3:
        st.session_state.quote_data["Colours"] = prompt
        st.session_state.quote_step = 4
        answer = "Almost there! Do you have a rough budget in mind? It helps me find the best value for you."

    elif st.session_state.quote_step == 4:
        st.session_state.quote_data["Budget"] = prompt
        st.session_state.quote_step = 0
        # Save Full Quote to Google Sheet [cite: 2026-02-12]
        send_to_office({**st.session_state.lead_data, **st.session_state.quote_data}, "FULL QUOTE")
        answer = "Wonderful! I've sent that request to our specialists. Is there anything else I can assist with, perhaps our branch locations?"

    # --- BRAIN FALLBACK ---
    if not answer:
        if st.session_state.brain:
            answer = st.session_state.brain.get_answer(prompt, st.session_state.chat_history)
        else:
            answer = "I'm right here! What can I tell you about our 2027 range?"

    st.session_state.last_text = answer
    st.session_state.chat_history.append({"role": "assistant", "content": answer})
    
    # Voice Gen
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

