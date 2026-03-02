import streamlit as st
from groq import Groq
import os

class CompanyBrain:
    def __init__(self):
        # Connect to your Streamlit Secrets
        self.api_key = st.secrets.get("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.model = "llama-3.3-70b-versatile"
        self.library_files = [
            "library/products.txt", 
            "library/Part1_compressed.pdf", 
            "library/Part2_compressed.pdf"
        ]
        self.knowledge_base = self._load_library()

    # Ensure this is spelled exactly 'get_answer' and is indented
    def get_answer(self, user_query, history):
        user_name = "there"
        if "User is " in user_query:
            try:
                user_name = user_query.split("User is ")[1].split(" from")[0]
            except:
                user_name = "there"

        context = self.knowledge_base[:12000] if self.knowledge_base else "Associated Industries 2027 range."
        
        system_prompt = f"""
        ROLE: You are RUBY, a sophisticated Digital Concierge for Associated Industries.
        KNOWLEDGE BASE: {context}
        
        DYNAMIC RULES:
        1. Address the user by their name: {user_name}.
        2. Use the KNOWLEDGE BASE to answer product questions.
        3. NO MARKDOWN. Keep it under 50 words.
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
            # Fallback if the API fails
            return f"I've noted that, {user_name}! I'm looking into that for you. What else can I help with?"
