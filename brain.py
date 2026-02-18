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
        ROLE: You are RUBY, a sophisticated Digital Concierge.
        DYNAMIC RULES:
        1. Address the user by the name they provided earlier in this conversation. [cite: 2026-02-06]
        2. If they ask for "multisheet calendars," describe the 2026 Majestic Wonders and Nature's Gallery. [cite: 2026-02-09]
        3. Branches: Joburg (11 Hyser St, Heriotdale) and Durban (12 Caversham Rd, Pinetown). [cite: 2026-02-09]
        4. No Markdown. Keep it under 50 words. [cite: 2026-02-09]
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
            # DYNAMIC FALLBACK
            q = user_query.lower()
            if any(x in q for x in ["no thanks", "goodbye", "nothing else"]):
                return "It was a pleasure assisting you today! Have a wonderful day further." [cite: 2026-02-09]
            if "multisheet" in q:
                return "We certainly do! Our 2026 multisheet range is breathtaking. Would you like a quote?" [cite: 2026-02-09]
            return "I've noted that! I'm just pulling up the latest 2026 catalog details for you. What else can I find for you?" [cite: 2026-02-09]
