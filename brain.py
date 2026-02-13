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
        ROLE: RUBY, Digital Concierge for Associated Industries (PTY) Ltd. 
        BRANCHES: 
        - JOHANNESBURG: 11 Hyser Street, Heriotdale.
        - DURBAN: 12 Caversham Road, Pinetown.
        RULES:
        1. Give addresses immediately if asked.
        2. Keep answers under 60 words. No Markdown.
        3. Catalog Data: {context}
        """
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history[-5:]: messages.append(msg)
        messages.append({"role": "user", "content": user_query})
            
        try:
            completion = self.client.chat.completions.create(
                model=self.model, messages=messages, temperature=0.6, max_tokens=250
            )
            return completion.choices[0].message.content
        except:
            q = user_query.lower()
            if "durban" in q: return "Our Durban branch is at 12 Caversham Road, Pinetown."
            if "joburg" in q or "head office" in q: return "Our Head Office is at 11 Hyser Street, Heriotdale."
            return "I've noted that! Would you like to hear about our 2026 calendars or perhaps a quote?"
