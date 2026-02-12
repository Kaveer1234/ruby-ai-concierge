import streamlit as st
from groq import Groq


class CompanyBrain:
    def __init__(self):
        # SECURE INITIALIZATION:
        # Pulls the key from Streamlit's private vault instead of plain text [cite: 2026-02-12]
        try:
            self.client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        except Exception as e:
            st.error("Missing API Key. Please add GROQ_API_KEY to your Streamlit Secrets.")
            self.client = None

    def get_answer(self, user_input, history):
        if not self.client:
            return "I'm having trouble connecting to my brain right now. Please check my API configuration."

        # Convert history for Groq format [cite: 2026-02-11]
        messages = [{"role": "system",
                     "content": "You are RUBY, a helpful concierge for Associated Industries. Be professional and concise."}]
        for msg in history[-5:]:  # Keep last 5 messages for context
            messages.append({"role": msg["role"], "content": msg["content"]})

        messages.append({"role": "user", "content": user_input})

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.7,
                max_tokens=150
            )
            return response.choices[0].message.content
        except Exception as e:

            return f"I encountered an error: {str(e)}"
