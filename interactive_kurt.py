import streamlit as st
import requests
import base64
from datetime import datetime
from gtts import gTTS
import os
import time
from brain import CompanyBrain

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="RUBY - Associated Industries",
    layout="wide"
)

# --------------------------------------------------
# PREMIUM UI CSS
# --------------------------------------------------
st.markdown("""
<style>

/* Hide Streamlit default UI */
header {visibility: hidden;}
[data-testid="stHeader"] {display: none;}
footer {visibility: hidden;}

[data-testid="stAppViewContainer"] {
    padding-top: 0rem !important;
}

[data-testid="stAppViewBlockContainer"] {
    padding-top: 0rem !important;
    max-width: 100% !important;
}

/* ---------------- HEADER ---------------- */
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

/* Title */
.ruby-title {
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 12px;
}

/* Video */
.stVideo video {
    border-radius: 16px;
    max-height: 150px;
    animation: fadeIn 0.4s ease-in-out;
}

@keyframes fadeIn {
    from {opacity: 0;}
    to {opacity: 1;}
}

/* Push chat below header */
.main .block-container {
    padding-top: 250px !important;
    padding-bottom: 110px !important;
}

/* Pin chat input */
[data-testid="stChatInput"] {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    background: white;
    padding: 12px 20px 20px 20px;
    border-top: 1px solid #eee;
    z-index: 9999;
}

/* Typing indicator */
.typing span {
    height: 8px;
    width: 8px;
    margin: 0 2px;
    background-color: #999;
    border-radius: 50%;
    display: inline-block;
    animation: bounce 1.4s infinite ease-in-out both;
}

.typing span:nth-child(1) { animation-delay: -0.32s; }
.typing span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
    0%, 80%, 100% { transform: scale(0); }
    40% { transform: scale(1); }
}

/* Floating mic */
.mic-btn {
    position: fixed;
    bottom: 90px;
    right: 25px;
    background: black;
    color: white;
    width: 55px;
    height: 55px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    cursor: pointer;
    box-shadow: 0px 6px 18px rgba(0,0,0,0.2);
    z-index: 9999;
}

/* Mobile */
@media (max-width: 768px) {
    .ruby-header { height: 170px; }
    .main .block-container { padding-top: 190px !important; }
    .ruby-title { font-size: 1.1rem; }
    .stVideo video { max-height: 110px; }
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------
def save_to_sheets(data):
    webhook_url = "YOUR_GOOGLE_SCRIPT_WEBHOOK_URL"
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

# --------------------------------------------------
# INITIAL SESSION STATE
# --------------------------------------------------
if "step" not in st.session_state:
    st.session_state.step = "name"
    st.session_state.lead_data = {"Name": "", "Company": ""}
    st.session_state.messages = []
    st.session_state.avatar = "kurt_idle.mp4"

brain = CompanyBrain()

# --------------------------------------------------
# HEADER RENDER FUNCTION
# --------------------------------------------------
header_placeholder = st.empty()

def update_avatar(video_file):
    header_placeholder.empty()
    with header_placeholder.container():
        st.markdown('<div class="ruby-header">', unsafe_allow_html=True)
        st.markdown('<div class="ruby-title">RUBY – Associated Industries 2027</div>', unsafe_allow_html=True)
        st.video(video_file, autoplay=True, loop=True, muted=True)
        st.markdown('</div>', unsafe_allow_html=True)

update_avatar(st.session_state.avatar)

# --------------------------------------------------
# DISPLAY CHAT HISTORY
# --------------------------------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# --------------------------------------------------
# CHAT INPUT LOGIC
# --------------------------------------------------
if user_input := st.chat_input("Talk to RUBY..."):

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    update_avatar("kurt_talking.mp4")

    with st.chat_message("assistant"):
        typing_placeholder = st.empty()
        typing_placeholder.markdown("""
            <div class="typing">
                <span></span><span></span><span></span>
            </div>
        """, unsafe_allow_html=True)

    time.sleep(1.2)

    if st.session_state.step == "name":
        st.session_state.lead_data["Name"] = user_input
        st.session_state.step = "company"
        response = f"Nice to meet you {user_input}! Which company are you with?"
    elif st.session_state.step == "company":
        st.session_state.lead_data["Company"] = user_input
        st.session_state.step = "chat"
        save_to_sheets(st.session_state.lead_data)
        response = "Great! How can I help you with our 2027 range today?"
    else:
        response = brain.get_answer(user_input, st.session_state.messages)

    typing_placeholder.empty()

    with st.chat_message("assistant"):
        st.write(response)
        speak(response)

    st.session_state.messages.append({"role": "assistant", "content": response})

    time.sleep(1.5)
    update_avatar("kurt_idle.mp4")

# --------------------------------------------------
# FLOATING MIC BUTTON
# --------------------------------------------------
st.markdown('<div class="mic-btn">🎤</div>', unsafe_allow_html=True)

# --------------------------------------------------
# AUTO SCROLL
# --------------------------------------------------
st.markdown("""
<script>
window.scrollTo(0, document.body.scrollHeight);
</script>
""", unsafe_allow_html=True)
