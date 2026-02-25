import streamlit as st
import requests
import base64
from datetime import datetime
from gtts import gTTS
import os
import time
from brain import CompanyBrain

# --- 1. UI SETUP: PREMIUM VIEWPORT LOCK ---
st.set_page_config(page_title="RUBY - Associated Industries", layout="wide")

st.markdown("""
<style>
header {visibility: hidden;}
[data-testid="stHeader"] {display: none;}
footer {visibility: hidden;}

/* THE LOCK: Absolute pinning of the blurred header */
.ruby-header {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 230px;
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    background: rgba(255,255,255,0.7);
    z-index: 9999;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border-bottom: 1px solid rgba(0,0,0,0.06);
}

.ruby-title { font-size: 1.5rem; font-weight: 600; margin-bottom: 12px; }

/* Push chat below the fixed header */
.main .block-container {
    padding-top: 250px !important;
    padding-bottom: 110px !important;
}

/* Typing indicator animation */
.typing span {
    height: 8px; width: 8px; margin: 0 2px;
    background-color: #999; border-radius: 50%;
    display: inline-block;
    animation: bounce 1.4s infinite ease-in-out both;
}
.typing span:nth-child(1) { animation-delay: -0.32s; }
.typing span:nth-child(2) { animation-delay: -0.16s; }
@keyframes bounce {
    0%, 80%, 100% { transform: scale(0); }
    40% { transform: scale(1); }
}

@media (max-width: 768px) {
    .ruby-header { height: 170px; }
    .main .block-container { padding-top: 190px !important; }
    .ruby-title { font-size: 1.1rem; }
}
</style>
""", unsafe_allow_html=True)

# --- 2. HELPER FUNCTIONS ---
def save_to_sheets(data):
    # Your verified Lead Webhook URL [cite: 2026-02-12]
    webhook_url = "https://script.google.com/macros/s/AKfycbyItMfaLdTh1AomZBj6ZfLK-fDHOZC4o7jm7CFhJibg3AMxB61uXtOxVr7axV2Qn-CmPA/exec"
    try:
        data["Timestamp"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        requests.post(webhook_url, json=data)
    except:
        pass

def speak(text):
    tts = gTTS(text=text, lang='en', tld='co.za')
    tts.save("response.mp3")
    with open("response.mp3", "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f'<audio src="data:audio/mp3;base64,{b64}" autoplay="true"></audio>'
        st.markdown(md, unsafe_allow_html=True)
    os.remove("response.mp3")

# --- 3. INITIALIZATION ---
if "step" not in st.session_state:
    st.session_state.step = "name"
    # Full lead fields as requested [cite: 2026-02-12]
    st.session_state.lead_data = {"Name": "", "Company": "", "Phone": "", "Email": ""}
    st.session_state.messages = []
    st.session_state.avatar = "kurt_idle.mp4"

brain = CompanyBrain()

# --- 4. HEADER RENDER ---
header_placeholder = st.empty()

def update_avatar(video_file):
    # Dynamic key prevents the DuplicateElementId crash
    v_key = f"video_{int(time.time())}"
    header_placeholder.empty()
    with header_placeholder.container():
        st.markdown('<div class="ruby-header">', unsafe_allow_html=True)
        st.markdown('<div class="ruby-title">RUBY – Associated Industries 2027</div>', unsafe_allow_html=True)
        st.video(video_file, autoplay=True, loop=True, muted=True, key=v_key)
        st.markdown('</div>', unsafe_allow_html=True)

update_avatar(st.session_state.avatar)

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# --- 5. CHAT LOGIC (Full Lead Flow) ---
if user_input := st.chat_input("Talk to RUBY..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    update_avatar("kurt_talking.mp4")

    with st.chat_message("assistant"):
        typing_placeholder = st.empty()
        typing_placeholder.markdown('<div class="typing"><span></span><span></span><span></span></div>', unsafe_allow_html=True)

    time.sleep(1.2)
    response = ""

    # Sequence for capturing contact information [cite: 2026-02-12]
    if st.session_state.step == "name":
        st.session_state.lead_data["Name"] = user_input
        st.session_state.step = "company"
        response = f"Nice to meet you {user_input}! Which company are you with?"
        
    elif st.session_state.step == "company":
        st.session_state.lead_data["Company"] = user_input
        st.session_state.step = "phone"
        response = f"Got it. What is the best telephone number to reach you at {user_input}?"
        
    elif st.session_state.step == "phone":
        st.session_state.lead_data["Phone"] = user_input
        st.session_state.step = "email"
        response = "Thank you. And finally, what is your company email address?"
        
    elif st.session_state.step == "email":
        st.session_state.lead_data["Email"] = user_input
        st.session_state.step = "chat"
        # Send complete lead data to Google Sheets [cite: 2026-02-12]
        save_to_sheets(st.session_state.lead_data)
        response = "Perfect! I've logged your details. How can I help you with our 2027 range today?"
        
    else:
        response = brain.get_answer(user_input, st.session_state.messages)

    typing_placeholder.empty()

    with st.chat_message("assistant"):
        st.write(response)
        speak(response)

    st.session_state.messages.append({"role": "assistant", "content": response})

    # Return to idle after speech finishes [cite: 2026-02-11]
    time.sleep(2.0)
    update_avatar("kurt_idle.mp4")
