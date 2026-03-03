import streamlit as st
from groq import Groq
import os
import re

class CompanyBrain:
    def __init__(self, library_path=None):
        # 1. THE ULTIMATE KEY FETCH
        raw_key = st.secrets.get("GROQ_API_KEY")
        
        # Clean the key of any quotes or spaces Gavin might have in Secrets
        self.api_key = str(raw_key).strip().strip('"').strip("'") if raw_key else None
        
        # DEBUG: This helps us see in the 'Manage App' logs if the key is formatted right
        if self.api_key and not self.api_key.startswith("gsk_"):
            print("WARNING: Your GROQ_API_KEY does not start with 'gsk_'. It might be copied incorrectly.")

        self.client = Groq(api_key=self.api_key) if self.api_key else None
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
        if "User is " in user_query:
            try:
                user_name = user_query.split("User is ")[1].split(" from")[0]
            except:
                user_name = "there"

        # --- THE RUBY SOUL ---
        system_prompt = f"""
        ROLE: You are RUBY, the bubbly, high-energy Digital Concierge for Associated Industries! 
        VIBE: Warm, professional, and very excited. You are a helpful AI assistant.
        
        KNOWLEDGE: 
        {self.knowledge_base}
        
        RULES:
        1. Greet {user_name} with massive excitement! 
        2. Use the KNOWLEDGE. Mention Jumbo Posters (900x580mm) or Prestige Multisheets.
        3. NO MARKDOWN. Keep it under 50 words!
        """
        
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history[-5:]:
            messages.append(msg)
        messages.append({"role": "user", "content": user_query})
            
        try:
            if not self.client: 
                return "Gavin, I still can't find my API Key in the dashboard!"
                
            completion = self.client.chat.completions.create(
                model=self.model, messages=messages, temperature=0.8, max_tokens=300
            )
            return completion.choices[0].message.content
        except Exception as e:
            # If it's still a 401, this will tell us exactly what Groq thinks is wrong
            return f"Oh {user_name}, I'm so excited about our 2027 range, but my brain is a bit foggy! Error: {str(e)}"
