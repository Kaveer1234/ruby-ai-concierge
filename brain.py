import streamlit as st
from groq import Groq
import os
import re

class CompanyBrain:
    def __init__(self, library_path=None):
        # This double-check ensures we find the key no matter how Streamlit stores it
        if "GROQ_API_KEY" in st.secrets:
            self.api_key = st.secrets["GROQ_API_KEY"]
        else:
            self.api_key = st.secrets.get("GROQ_API_KEY")

        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.model = "llama-3.3-70b-versatile"
        self.library_file = library_path if library_path else "library/products.txt"
        self.knowledge_base = self._load_library()

    def _load_library(self):
        if os.path.exists(self.library_file):
            try:
                with open(self.library_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Clean the source tags so Ruby sounds natural
                    return re.sub(r'\[(?:source|cite): [\d, ]+\]', '', content)
            except Exception:
                return "Our 2027 range is ready for you!"
        return "Associated Industries 2027 collection."

    def get_answer(self, user_query, history):
        user_name = "there"
        if "User is " in user_query:
            try:
                user_name = user_query.split("User is ")[1].split(" from")[0]
            except:
                user_name = "there"

        # --- THE RUBY SOUL ---
        system_prompt = f"""
        ROLE: You are RUBY, the bubbly, high-energy Digital Concierge for Associated Industries! 
        VIBE: Professional but very excited and friendly.
        
        KNOWLEDGE: 
        {self.knowledge_base}
        
        RULES:
        1. Greet {user_name} with major energy! 
        2. Talk about our 2027 products like the Jumbo Posters (900x580mm) or Prestige Multisheets.
        3. Mention branding options like foiling or screen printing if they ask for a quote.
        4. NO MARKDOWN. Under 50 words.
        """
        
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history[-5:]:
            messages.append(msg)
        messages.append({"role": "user", "content": user_query})
            
        try:
            if not self.client:
                return "I'm still missing my API Key in the Streamlit Secrets! Please double-check the dashboard."
                
            completion = self.client.chat.completions.create(
                model=self.model, messages=messages, temperature=0.8, max_tokens=300
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Oh {user_name}, I'm so excited about our 2027 range, but my brain is a bit foggy! Error: {str(e)}"
