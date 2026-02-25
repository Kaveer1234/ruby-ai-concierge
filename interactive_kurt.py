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
    top: 0; left: 0; width: 100%; height: 230px;
    backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px);
    background: rgba(255,255,255,0.7);
    z-index: 9999;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    border-bottom: 1px solid rgba(0,0,0,0.06);
}

.ruby-title { font-size: 1.5rem; font-weight: 600; margin-bottom: 12px; }

/* Push chat below the fixed header */
.main .block-container {
    padding-top: 250px !important;
    padding-bottom: 110px !important;
}

.typing span {
    height: 8px; width: 8px; margin: 0 2px;
    background-color: #999; border-radius: 50%;
    display: inline-block;
    animation: bounce 1.4s infinite ease-in-out both;
}
@keyframes bounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }

@media (max-width: 768px) {
    .ruby-header { height: 170px; }
    .main .block-container { padding-top: 190px !important; }
    .ruby-title { font-size: 1.1rem; }
}
</style>
""", unsafe_allow_html=True)

# --- 2. HELPER FUNCTIONS ---
def save_to_sheets(data):
    webhook_url = "https://script.google.com/macros/s/AKfycbyItMfaLdTh1AomZBj6ZfLK-fDHOZC4o7jm7CFhJibg3AMxB61uXtOxVr7axV2Qn-CmPA/exec"
    try:
        data["Timestamp"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        requests.post(webhook_url, json=data)
    except: pass

def speak(text):
    tts = gTTS(text=text, lang='en', tld='co.za')
    tts.save("response.mp3")
    with open("response.mp3", "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
        st.markdown(f'<audio src="data:audio/mp3;base64,{b64}" autoplay="true"></audio>', unsafe_allow_html=True)
    os.remove("response.mp3")

# --- 3. INITIALIZATION (Includes v_key fix) ---
if "step" not in st.session_state:
    st.session_state.step = "name"
    st.session_state.lead_data = {"Name": "", "Company": "", "Phone": "", "Email": ""}
    st.session_state.messages = []
    st.session_state.avatar = "kurt_idle.mp4"
    st.session_state.v_key = 0 # This ensures session state exists [cite: 2026-02-11]

brain = CompanyBrain()

# --- 4. THE HEADER RENDER (Rendered exactly once per run) ---
st.markdown(f"""
    <div class="ruby-header">
        <div class="ruby-title">RUBY – Associated Industries 2027</div>
    </div>
""", unsafe_allow_html=True)

# We place the video inside the header area using a clean container
with st.container():
    # Adding a small spacer to center inside the fixed div
    st.markdown('<div style="height:40px;"></div>', unsafe_allow_html=True)
    cols = st.columns([1, 2, 1])
    with cols[1]:
        st.video(st.session_state.avatar, autoplay=True, loop=True, muted=True)

# --- 5. CHAT HISTORY ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# --- 6. CHAT LOGIC ---
if user_input := st.chat_input("Talk to RUBY..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # 1. Update state to Talking
    st.session_state.avatar = "kurt_talking.mp4"
    
    # 2. Logic for lead capture
    response = ""
    if st.session_state.step == "name":
        st.session_state.lead_data["Name"] = user_input
        st.session_state.step = "company"
        response = f"Nice to meet you {user_input}! Which company are you with?"
    elif st.session_state.step == "company":
        st.session_state.lead_data["Company"] = user_input
        st.session_state.step = "phone"
        response = "Got it. What is your telephone number?"
    elif st.session_state.step == "phone":
        st.session_state.lead_data["Phone"] = user_input
        st.session_state.step = "email"
        response = "And your company email address?"
    elif st.session_state.step == "email":
        st.session_state.lead_data["Email"] = user_input
        st.session_state.step = "chat"
        save_to_sheets(st.session_state.lead_data)
        response = "Perfect! How can I help you today?"
    else:
        response = brain.get_answer(user_input, st.session_state.messages)

    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Rerun once to show the user message and start Ruby talking
    st.rerun()

# This handles the voice and the "return to idle" logic after a rerun
if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant" and st.session_state.avatar == "kurt_talking.mp4":
    last_response = st.session_state.messages[-1]["content"]
    speak(last_response)
    time.sleep(2.0)
    st.session_state.avatar = "kurt_idle.mp4"
    st.rerun()
