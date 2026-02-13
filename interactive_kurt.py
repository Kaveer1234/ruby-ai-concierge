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
        st.error(f"Ruby's brain is offline. Check brain.py or reboot. Error: {e}")
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
    # Using session state values directly to keep fields updated
    st.text(f"Name: {st.session_state.lead_data['Name']}")
    st.text(f"Company: {st.session_state.lead_data['Company']}")
    st.text(f"Phone: {st.session_state.lead_data['Phone']}")
    st.text(f"Email: {st.session_state.lead_data['Email']}")

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

    # --- RIGID GARBAGE FILTER ---
    last_ruby = st.session_state.chat_history[-2]["content"].lower()
    garbage_list = [
        "my name is", "i am", "the company is", "we are", "is email", 
        "is my email", "ruby", "hi", "hello", "is my phone", "is my name", 
        "is name", "my company name is", "my number is", "use this email",
        "i work for", "i work at", "company is called"
    ]
    clean = prompt.lower()
    for word in garbage_list:
        clean = clean.replace(word, "")
    clean = clean.strip().title()

    # Global Listener
    phone_match = re.search(r'(\d{3}\s?\d{3}\s?\d{4}|\d{9,})', prompt)
    if phone_match:
        st.session_state.lead_data["Phone"] = phone_match.group(0)

    email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', prompt)
    if email_match:
        st.session_state.lead_data["Email"] = email_match.group(0)

    # --- NATURAL LEAD FLOW ---
    answer = ""
    
    if "your name" in last_ruby and not st.session_state.lead_data["Name"]:
        st.session_state.lead_data["Name"] = clean
        answer = f"Awesome, thanks {st.session_state.lead_data['Name']}! And which company are you with?"

    elif "which company" in last_ruby and not st.session_state.lead_data["Company"]:
        st.session_state.lead_data["Company"] = clean
        answer = "Got it. Just in case we get disconnected, what’s the best number to reach you on?"

    elif "reach you on" in last_ruby and not st.session_state.lead_data["Email"]:
        # Phone captured by Global Listener
        answer = "Perfect. And lastly, what is your work email address? I'll use this to send you any catalogs or quotes we discuss."

    # --- QUOTE WORKFLOW ---
    elif any(x in prompt.lower() for x in ["quote", "price", "how much"]) and st.session_state.quote_step == 0:
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
        st.session_state.quote_data["Budget"] = clean
        st.session_state.quote_step = 5
        
        display_name = st.session_state.lead_data["Name"] if st.session_state.lead_data["Name"] else "A Client"
        final_data = {**st.session_state.lead_data, **st.session_state.quote_data}
        send_to_office(final_data, "FULL QUOTE REQUEST: " + display_name)
        
        answer = f"Perfect! I've made a note of your details for the {st.session_state.quote_data['Product']}. I have sent this request to our sales team at sales@brabys.co.za. Is there anything else I can help with?"

    # --- BRAIN FALLBACK ---
    if not answer:
        if st.session_state.brain:
            try:
                answer = st.session_state.brain.get_answer(prompt, st.session_state.chat_history)
            except:
                answer = "I'm having a slight technical moment. Could you repeat that?"
        else:
            answer = "My brain is just warming up. Please tell me your name again?"

    st.session_state.last_text = answer
    st.session_state.chat_history.append({"role": "assistant", "content": answer})

    # Auto-Email Trigger for Lead Capture
    if st.session_state.lead_data["Email"] and not st.session_state.mail_sent and st.session_state.quote_step < 5:
        send_to_office(st.session_state.lead_data, "New Lead Captured: " + st.session_state.lead_data["Name"])
        st.session_state.mail_sent = True

    # --- CLEAN VOICE OUTPUT ---
    # Remove Markdown so gTTS doesn't say "star star" or "hash hash"
    voice_text = re.sub(r'[\*\#\_]', '', answer)
    tts = gTTS(text=voice_text, lang='en', tld='co.uk')
    tts.save("response.mp3")
    st.session_state.is_talking = True
    st.rerun()

# --- VOICE PLAYBACK & FINAL STABILITY WAIT ---
if st.session_state.is_talking:
    st.audio("response.mp3", autoplay=True)
    wait = (len(st.session_state.last_text) / 9) + 4
    time.sleep(min(wait, 22)) 
    st.session_state.is_talking = False
    st.rerun()
