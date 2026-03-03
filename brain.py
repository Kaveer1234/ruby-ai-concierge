import streamlit as st
from groq import Groq
import os
import re

class CompanyBrain:
    def __init__(self, library_path=None):
        # 1. AUTHENTICATION: Uses the key from your Streamlit Secrets
        self.api_key = st.secrets.get("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.model = "llama-3.3-70b-versatile"
        
        # 2. LIBRARY SETUP: Points to your products.txt
        self.library_file = library_path if library_path else "library/products.txt"
        self.knowledge_base = self._load_library()

    def _load_library(self):
        if os.path.exists(self.library_file):
            try:
                with open(self.library_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    # CLEANER: Strips technical tags so Ruby speaks naturally
                    clean_text = re.sub(r'\[(?:source|cite): [\d, ]+\]', '', content)
                    return clean_text
            except Exception as e:
                print(f"Library Load Error: {e}")
                return "Our 2027 collection is breathtaking!"
        return "Associated Industries 2027 range."

    def get_answer(self, user_query, history):
        # Extract user name for personalized greeting
        user_name = "there"
        if "User is " in user_query:
            try:
                user_name = user_query.split("User is ")[1].split(" from")[0]
            except:
                user_name = "there"

        # 3. THE GOLD STANDARD SYSTEM PROMPT
        system_prompt = f"""
        ROLE: You are RUBY, the bubbly and high-energy Digital Concierge for Associated Industries! 
        Your soul is: Warm, helpful, and professional.
        
        KNOWLEDGE BASE: 
        {self.knowledge_base}
        
        VIBE RULES:
        1. Greet {user_name} with major excitement! 
        2. Use the KNOWLEDGE BASE to answer. Mention specific 2027 gems like our Jumbo Posters (900x580mm) or the 'Majestically Wild' wildlife theme.
        3. NO MARKDOWN (no stars, no bold). Keep it under 50 words. Be snappy and fun!
        """
        
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history[-5:]: 
            messages.append(msg)
        messages.append({"role": "user", "content": user_query})
            
        try:
            if not self.client: raise Exception("API Key Missing")
            
            completion = self.client.chat.completions.create(
                model=self.model, messages=messages, temperature=0.8, max_tokens=300
            )
            return completion.choices[0].message.content
        except Exception as e:
            # Fallback message if the API is busy
            return f"Oh {user_name}, I'm just so excited to show you our 2027 range! What specific products can I help you find today?"
