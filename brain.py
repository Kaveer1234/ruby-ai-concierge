import streamlit as st
from groq import Groq
import os
import fitz  # PyMuPDF for reading PDFs

class CompanyBrain:
    def __init__(self):
        self.api_key = st.secrets.get("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.model = "llama-3.3-70b-versatile"
        self.library_files = [
            "library/products.txt", 
            "library/Part1_compressed.pdf", 
            "library/Part2_compressed.pdf"
        ]
        self.knowledge_base = self._load_library()

    # --- THE MISSING FUNCTION ---
    def _load_library(self):
        text = ""
        for file_path in self.library_files:
            if not os.path.exists(file_path):
                continue
            if file_path.endswith(".pdf"):
                try:
                    doc = fitz.open(file_path)
                    for page in doc:
                        text += page.get_text()
                except Exception as e:
                    print(f"Error loading PDF {file_path}: {e}")
            else:
                with open(file_path, "r", encoding="utf-8") as f:
                    text += f.read()
        return text

    def get_answer(self, user_query, history):
        user_name = "there"
        if "User is " in user_query:
            try:
                user_name = user_query.split("User is ")[1].split(" from")[0]
            except:
                user_name = "there"

        # Use the first 12000 characters of your library
        context = self.knowledge_base[:12000] if self.knowledge_base else "Associated Industries 2027 range."
        
        system_prompt = f"""
        ROLE: You are RUBY, a sophisticated Digital Concierge for Associated Industries.
        KNOWLEDGE BASE: {context}
        
        DYNAMIC RULES:
        1. Address the user by their name: {user_name}.
        2. Use the KNOWLEDGE BASE to answer product questions.
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
            return f"I've noted that, {user_name}! I'm looking into that for you. What else can I help with?"
