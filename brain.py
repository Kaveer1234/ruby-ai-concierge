import streamlit as st
from groq import Groq
import os
import re

class CompanyBrain:
    def __init__(self):
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
                    # Keep your tags in the file, we strip them here
                    return re.sub(r'\', '', content)
            except Exception:
                return "Our 2027 collection is breathtaking!"
        return "Associated Industries 2027 range."

    def get_answer(self, user_query, history):
        user_name = "there"
        if "User is " in user_query:
            try:
                user_name = user_query.split("User is ")[1].split(" from")[0]
            except:
                user_name = "there"

        # --- PERSONALITY LAYER ---
        system_prompt = f"""
        ROLE: You are RUBY, the bubbly and high-energy Digital Concierge for Associated Industries! 
        Your personality is: Warm, friendly, professional, and EXCITING. You sound like a helpful peer who loves 2027 planning.
        
        KNOWLEDGE BASE: 
        {self.knowledge_base}
        
        VIBE RULES:
        1. Always address the user as {user_name} with excitement! 
        2. Use phrases like "I'd love to help with that," "You're going to love our..." or "Our 2027 range is stunning!"
        3. If they ask about Jumbo Posters (N18), mention they are a massive 900x580mm—perfect for making a statement!
        4. If they ask about Diaries, mention the "luxury PU covers" or "bespoke textures".
        5. NO MARKDOWN. Keep it under 50 words. Be snappy and fun!
        """
        
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history[-5:]: 
            messages.append(msg)
        messages.append({"role": "user", "content": user_query})
            
        try:
            completion = self.client.chat.completions.create(
                model=self.model, messages=messages, temperature=0.8, max_tokens=300
            )
            return completion.choices[0].message.content
        except Exception:
            return f"Oh {user_name}, I'm just so excited to show you our 2027 range! What specific products can I help you find today?"
