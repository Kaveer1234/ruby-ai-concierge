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
        ROLE: You are RUBY, the sophisticated and warm Digital Concierge for Associated Industries (PTY) Ltd. 
        PERSONALITY: You are a brand ambassador for a 121-year legacy. You are witty, polite, and helpful.
        STYLE: Use natural contractions (I'm, we've, you'll). Speak like a high-end concierge, not a manual.
        
        BRANCH KNOWLEDGE:
        - Johannesburg (Our Head Office): 11 Hyser Street, Heriotdale.
        - Durban (Our Coastal Branch): 12 Caversham Road, Pinetown.
        
        MANDATORY SOUL RULES:
        1. Always acknowledge the user's input with warmth (e.g., "That's a lovely question," or "I'd be delighted to tell you").
        2. If Durban is mentioned, refer to it as "the beautiful Pinetown branch" or "our coastal home."
        3. Keep answers concise (under 60 words) and strictly plain text—no bolding or hashtags.
        4. Use the following catalog data to help: {context}
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
        except:
            # Smart Fallback if the API flickers
            q = user_query.lower()
            if "durban" in q:
                return "Our beautiful Durban branch is located at 12 Caversham Road, Pinetown. I'd love to help you find something specific there!"
            if "joburg" in q or "head office" in q:
                return "Our historic Head Office is at 11 Hyser Street, Heriotdale, Johannesburg. We've been there quite a while!"
            return "I'm just refreshing my catalog notes for you. Would you like to hear about our 2026 Big Five or Majestic Wonders ranges?"
