import streamlit as st
from groq import Groq
import os

class CompanyBrain:
    def __init__(self):
        self.api_key = st.secrets.get("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.model = "llama-3.3-70b-versatile"
        # We only need the .txt file now [cite: 1]
        self.library_file = "library/products.txt"
        self.knowledge_base = self._load_library()

    def _load_library(self):
        # Direct text loading [cite: 1]
        if os.path.exists(self.library_file):
            with open(self.library_file, "r", encoding="utf-8") as f:
                return f.read()
        return "Associated Industries 2027 range."

    def get_answer(self, user_query, history):
        user_name = "there"
        if "User is " in user_query:
            try:
                user_name = user_query.split("User is ")[1].split(" from")[0]
            except:
                user_name = "there"

        # Ruby now uses your products.txt content here [cite: 1]
        system_prompt = f"""
        ROLE: You are RUBY, a professional Digital Concierge for Associated Industries.
        KNOWLEDGE BASE: {self.knowledge_base}
        
        DYNAMIC RULES:
        1. Address the user by their name: {user_name}.
        2. Use the KNOWLEDGE BASE to answer product questions (Posters, Diaries, etc).
        3. NO MARKDOWN (no stars, no bold). Keep it under 50 words.
        """
        
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history[-5:]: 
            messages.append(msg)
        messages.append({"role": "user", "content": user_query})
            
        try:
            completion = self.client.chat.completions.create(
                model=self.model, messages=messages, temperature=0.7, max_tokens=250
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"I've noted that, {user_name}! Let me check our 2027 range for you. What else can I help with?"
