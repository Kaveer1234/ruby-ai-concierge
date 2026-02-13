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
        context = self.knowledge_base[:8000] if self.knowledge_base else "Associated Industries 121-year legacy."
        
        system_prompt = f"""
        ROLE: You are RUBY, the sophisticated and warm Digital Concierge for Associated Industries (PTY) Ltd. 
        PERSONALITY: You are a brand ambassador. You are witty, polite, and deeply human.
        STYLE: Use natural contractions (I'm, we've). Speak like a high-end concierge.
        
        BRANCH KNOWLEDGE:
        - Johannesburg (Head Office): 11 Hyser Street, Heriotdale.
        - Durban (Coastal Branch): 12 Caversham Road, Pinetown.
        
        SOUL RULES:
        1. Always acknowledge input with warmth.
        2. Refer to Durban as "our beautiful Pinetown branch."
        3. No Markdown (no ** or #). Keep it under 50 words.
        4. Catalog Data: {context}
        """
        
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history[-5:]: messages.append(msg)
        messages.append({"role": "user", "content": user_query})
            
        try:
            completion = self.client.chat.completions.create(
                model=self.model, messages=messages, temperature=0.7, max_tokens=250
            )
            return completion.choices[0].message.content
        except:
            q = user_query.lower()
            if "durban" in q: return "Our beautiful Pinetown branch is at 12 Caversham Road, Pinetown."
            return "I'm just refreshing my catalog for you! Would you like to hear about our 2026 range?"
