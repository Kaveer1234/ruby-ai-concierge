import streamlit as st
from groq import Groq
import os
import re

class CompanyBrain:
    def __init__(self):
        # 1. CHECK SECRETS: Ensure your key is named GROQ_API_KEY in Streamlit
        self.api_key = st.secrets.get("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.model = "llama-3.3-70b-versatile"
        self.library_file = "library/products.txt"
        self.knowledge_base = self._load_library()

    def _load_library(self):
        if os.path.exists(self.library_file):
            try:
                with open(self.library_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Removes both and tags
                    clean_text = re.sub(r'\[(?:source|cite): [\d, ]+\]', '', content)
                    return clean_text
            except Exception as e:
                print(f"DEBUG: Library Load Error: {e}")
                return "Error loading products."
        return "Associated Industries 2027 range."

    def get_answer(self, user_query, history):
        user_name = "there"
        if "User is " in user_query:
            try:
                user_name = user_query.split("User is ")[1].split(" from")[0]
            except:
                user_name = "there"

        system_prompt = f"""
        ROLE: You are RUBY, the bubbly and high-energy Digital Concierge for Associated Industries! 
        Your soul is: Warm, friendly, and professional. 
        
        KNOWLEDGE BASE: 
        {self.knowledge_base}
        
        VIBE RULES:
        1. Always address the user as {user_name} with excitement! 
        2. Use the KNOWLEDGE BASE to answer. Mention our Jumbo Posters (900x580mm) or Prestige Multisheets.
        3. NO MARKDOWN. Keep it under 50 words. Be snappy and fun!
        """
        
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history[-5:]: 
            messages.append(msg)
        messages.append({"role": "user", "content": user_query})
            
        try:
            if not self.client:
                raise Exception("Groq API Client is missing. Check Streamlit Secrets.")
                
            completion = self.client.chat.completions.create(
                model=self.model, messages=messages, temperature=0.6, max_tokens=300
            )
            return completion.choices[0].message.content
        except Exception as e:
            # THIS PRINTS TO YOUR 'MANAGE APP' LOGS
            print(f"!!! RUBY ENGINE ERROR: {e}")
            return f"Oh {user_name}, I'm just so excited to show you our 2027 range! What specific products can I help you find today?"

