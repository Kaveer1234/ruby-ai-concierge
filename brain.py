import os
import PyPDF2
from groq import Groq

class CompanyBrain:
    def __init__(self):
        self.api_key = os.environ.get("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.model = "llama-3.3-70b-versatile"
        self.library_files = [
            "library/Part1_compressed.pdf", "library/Part2_compressed.pdf",
            "library/Part3_compressed.pdf", "library/Part4_compressed.pdf"
        ]
        self.knowledge_base = self._load_library()

    def _load_library(self):
        combined_text = ""
        for file_path in self.library_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, "rb") as f:
                        reader = PyPDF2.PdfReader(f)
                        for page in reader.pages:
                            text = page.extract_text()
                            if text: combined_text += text + "\n"
                except: pass
        return combined_text

    def get_answer(self, user_query, history):
        context = self.knowledge_base[:8000] if self.knowledge_base else "Associated Industries 2026 range."
        
        system_prompt = f"""
        ROLE: You are RUBY, the warm and professional concierge for Associated Industries.
        STYLE: Use natural contractions. Be charming.
        
        BRANCHES:
        - Johannesburg: 11 Hyser Street, Heriotdale.
        - Durban: 12 Caversham Road, Pinetown.
        
        RULES:
        1. If the user says "no thanks" or "goodbye," wish them a wonderful day politely.
        2. Keep answers under 50 words. No Markdown stars or hashes.
        3. Knowledge Base: {context}
        """
        
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history[-5:]: messages.append(msg)
        messages.append({"role": "user", "content": user_query})
            
        try:
            if not self.client: raise Exception("Offline")
            completion = self.client.chat.completions.create(
                model=self.model, messages=messages, temperature=0.7, max_tokens=250
            )
            return completion.choices[0].message.content
        except:
            # --- INTELLIGENT KEYWORD FALLBACK ---
            q = user_query.lower()
            if any(x in q for x in ["no thanks", "nothing else", "goodbye", "that is all"]):
                return "You're most welcome! It was a pleasure assisting you today. Have a wonderful day further!"
            if any(x in q for x in ["jhb", "johannesburg", "durban", "branch", "where are you"]):
                return "We have our Head Office at 11 Hyser Street, Heriotdale (Joburg) and our coastal branch at 12 Caversham Road, Pinetown (Durban)."
            return "I've noted that! I'm just pulling up the latest 2026 catalog details for you. Is there a specific product like a diary or calendar you're looking for?"
