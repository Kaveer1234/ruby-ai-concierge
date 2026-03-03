import streamlit as st
from gtts import gTTS
import os
import time
from brain import CompanyBrain
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- RECOVERY POINT: VERSION D ---

# 1. BRAIN INITIALIZATION
LIBRARY_PATH = "library/products.txt"
brain = CompanyBrain(library_path=LIBRARY_PATH)

# 2. GOOGLE SHEETS SETUP (LEAD GEN)
def save_lead(name, company, phone, email):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        # Ensure your 'credentials.json' is in your GitHub main folder
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        client = gspread.authorize(creds)
        # Ensure your Sheet name matches exactly
        sheet = client.open("Ruby_Leads").sheet1
        sheet.append_row([name, company, phone, email, time.strftime("%Y-%m-%d %H:%M:%S")])
        return True
    except Exception as e:
        print(f"Lead Save Error: {e}")
        return False

# 3. VOICE ENGINE (DYNAMIC WAIT FIX)
def speak_text(text):
    if text:
        tts = gTTS(text=text, lang='en')
        filename = f"temp_{int(time.time())}.mp3"
        tts.save(filename)
        
        audio_file = open(filename, 'rb')
        audio_bytes = audio_file.read()
        
        st.audio(audio_bytes, format='audio/mp3', autoplay=True)
        
        # Calculation to ensure the full audio finishes
        duration = len(text.split()) * 0.4 + 2 
        time.sleep(duration)
        
        audio_file.close()
        os.remove(filename)

# 4. APP INTERFACE
st.title("RUBY – Associated Industries 2027")

if "step" not in st.session_state:
    st.session_state.step = "name"
    st.session_state.user_data = {}
    st.session_state.history = []

# LEAD CAPTURE FLOW
if st.session_state.step == "name":
    name = st.text_input("Please enter your name:")
    if name:
        st.session_state.user_data["name"] = name
        st.session_state.step = "company"
        st.rerun()

elif st.session_state.step == "company":
    st.write(f"Nice to meet you {st.session_state.user_data['name']}!")
    co = st.text_input(f"Which company are you with?")
    if co:
        st.session_state.user_data["company"] = co
        st.session_state.step = "phone"
        st.rerun()

elif st.session_state.step == "phone":
    phone = st.text_input("What is your telephone number?")
    if phone:
        st.session_state.user_data["phone"] = phone
        st.session_state.step = "email"
        st.rerun()

elif st.session_state.step == "email":
    email = st.text_input("And your company email address?")
    if email:
        st.session_state.user_data["email"] = email
        save_lead(
            st.session_state.user_data["name"],
            st.session_state.user_data["company"],
            st.session_state.user_data["phone"],
            st.session_state.user_data["email"]
        )
        st.session_state.step = "chat"
        st.rerun()

# PRODUCT CHAT (RUBY'S BRAIN)
elif st.session_state.step == "chat":
    user_query = st.chat_input("How can I help you today?")
    if user_query:
        # Pass name to the brain for personalization
        context_query = f"User is {st.session_state.user_data['name']} from {st.session_state.user_data['company']}. {user_query}"
        response = brain.get_answer(context_query, st.session_state.history)
        
        st.session_state.history.append({"role": "user", "content": user_query})
        st.session_state.history.append({"role": "assistant", "content": response})
        
        for msg in st.session_state.history:
            st.chat_message(msg["role"]).write(msg["content"])
        
        speak_text(response)
