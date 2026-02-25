import streamlit as st
import requests
import base64
from datetime import datetime
from gtts import gTTS
import os
import time
from brain import CompanyBrain

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="RUBY - Associated Industries",
    layout="wide"
)

# -------------------------------------------------
# GLASS SAAS UI CSS
# -------------------------------------------------
st.markdown("""
<style>

/* -------- REMOVE STREAMLIT DEFAULT -------- */
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

/* -------- FLOATING GLASS HEADER -------- */
.ruby-header {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 230px;
    backdrop-filter: blur(18px);
    -webkit-backdrop-filter: blur(18px);
    background: rgba(255,255,255,0.65);
    z-index: 9999;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border-bottom: 1px solid rgba(0,0,0,0.06);
}

.ruby-title {
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 12px;
}

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
    padding-bottom: 100px !important;
}

/* -------- PIN CHAT INPUT -------- */
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

/* -------- TYPING DOTS -------- */
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

/* -------- FLOATING MIC BUTTON -------- */
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

/* -------- MOBILE -------- */
@media (max-width: 768px) {

    .ruby-header {
        height: 170px;
    }

    .main .block-container {
        padding-top: 190px !important;
    }

    .ruby-title {
        font-size: 1.1rem;
    }

    .stVideo video {
        max-height: 110px;
    }
}

</style>
""", unsafe_allow_html=True)

# Floating mic button (UI only for now)
st.markdown('<div class="mic-btn">🎤</div>', unsafe_allow_html=True)

# -------------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------------

def save_to_sheets(data):
    webhook_url = "YOUR_GOOGLE_SCRIPT_WEBHOOK"
    try:
        data["Timestamp"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        requests.post(webhook_url, json=data)
    except:
        pass


def speak(text):
    tts = gTTS(text=text, lang='en', tld='co.za')
    tts.save("response.mp3")
    with open("response.mp3", "rb") as f:
        audio_bytes = f.read()
        b64 = base64.b64encode(audio_bytes).decode()
        audio_html = f'<audio src="data:audio/mp3;base64,{b64}" autoplay></audio>'
        st.markdown(audio_html, unsafe_allow_html=True)
    os.remove("response.mp3")


def typing_animation():
    st.markdown("""
        <div class="typing">
            <span></span><span></span><span></span>
        </div>
    """, unsafe_allow_html=True)


# -------------------------------------------------
# SESSION STATE INIT
# -------------------------------------------------

if "step" not in st.session_state:
    st.session_state.step = "name"
    st.session_state.lead_data = {
        "Name": "",
        "Company": "",
        "Phone": "",
        "Email": ""
    }
    st.session_state.messages = []
    st.session_state.avatar = "kurt_idle.mp4"

brain = CompanyBrain()

# -------------------------------------------------
# FLOATING HEADER
# -------------------------------------------------

header_placeholder = st.empty()

def update_avatar(video_file):
    header_placeholder.empty()
    with header_placeholder.container():
        st.markdown('<div class="ruby-header">', unsafe_allow_html=True)
        st.markdown('<div class="ruby-title">RUBY – Associated Industries 2027</div>', unsafe_allow_html=True)
        st.video(video_file, autoplay=True, loop=True, muted=True)
        st.markdown('</div>', unsafe_allow_html=True)

update_avatar(st.session_state.avatar)

# -------------------------------------------------
# DISPLAY CHAT HISTORY
# -------------------------------------------------

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# -------------------------------------------------
# CHAT INPUT LOGIC
# -------------------------------------------------

if user_input := st.chat_input("Talk to RUBY..."):

    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.write(user_input)

    update_avatar("kurt_talking.mp4")

    with st.chat_message("assistant"):
        typing_animation()

    time.sleep(1)

    # Lead capture flow
    if st.session_state.step == "name":
        st.session_state.lead_data["Name"] = user_input
        st.session_state.step = "company"
        response = f"Hello {user_input}! Which company are you with?"

    elif st.session_state.step == "company":
        st.session_state.lead_data["Company"] = user_input
        st.session_state.step = "chat"
        save_to_sheets(st.session_state.lead_data)
        response = "Great! How can I help you with our 2027 range today?"

    else:
        response = brain.get_answer(user_input, st.session_state.messages)

    # Remove typing animation by rerendering message
    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )

    with st.chat_message("assistant"):
        st.write(response)
        speak(response)

    time.sleep(1.5)
    update_avatar("kurt_idle.mp4")

# -------------------------------------------------
# AUTO SCROLL
# -------------------------------------------------
st.markdown("""
<script>
window.scrollTo(0, document.body.scrollHeight);
</script>
""", unsafe_allow_html=True)
