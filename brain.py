import streamlit as st
from groq import Groq
import os
import re

class CompanyBrain:
    def __init__(self, library_path=None):

        # Load API key directly from Streamlit secrets
        self.api_key = st.secrets["GROQ_API_KEY"]

        # Initialize Groq client
        self.client = Groq(api_key=self.api_key)

        self.model = "llama-3.3-70b-versatile"
        self.library_file = library_path if library_path else "library/products.txt"
        self.knowledge_base = self._load_library()

    def _load_library(self):
        if os.path.exists(self.library_file):
            try:
                with open(self.library_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    return re.sub(r'\[(?:source|cite): [\d, ]+\]', '', content)
            except Exception:
                return "Our 2027 collection is breathtaking!"
        return "Associated Industries 2027 range."

    def get_answer(self, user_query, history):

        user_name = "there"
        if "User:" in user_query:
            try:
                user_name = user_query.split("User: ")[1].split(" from")[0]
            except:
                pass

        system_prompt = f"""
ROLE: You are RUBY, the bubbly Digital Representitive for Associated Industries.

KNOWLEDGE:
{self.knowledge_base}

Personality:
Warm, upbeat, conversational, professional.
Speak like a helpful sales assistant, not a robot.

RULES:
1. Only greet the user once at the beginning of the conversation.
2. Mention Jumbo Posters (900x580mm) or Prestige Multisheets.
3. No markdown.
4. Keep replies under 50 words.
5. Do NOT greet every message.
6. Use a natural tone.
"""

        messages = [{"role": "system", "content": system_prompt}]

        for msg in history[-5:]:
            messages.append(msg)

        messages.append({"role": "user", "content": user_query})

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=200
            )

            return completion.choices[0].message.content

        except Exception as e:
            return f"Ruby is having a small technical hiccup: {str(e)}"


