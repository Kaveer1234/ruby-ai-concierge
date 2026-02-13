import os
import PyPDF2
from groq import Groq

class CompanyBrain:
    def __init__(self):
        # Initialize Groq
        self.api_key = os.environ.get("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.model = "llama-3.3-70b-versatile"
        
        # Library setup
        self.library_files = [
            "library/Part1_compressed.pdf",
            "library/Part2_compressed.pdf",
            "library/Part3_compressed.pdf",
            "library/Part4_compressed.pdf"
        ]
        self.knowledge_base = self._load_library()

    def _load_library(self):
        """Reads the PDFs for catalog knowledge."""
        combined_text = ""
        for file_path in self.library_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, "rb") as f:
                        reader = PyPDF2.PdfReader(f)
                        for page in reader.pages:
                            text = page.extract_text()
                            if text:
                                combined_text += text + "\n"
                except:
                    pass
        return combined_text

    def get_answer(self, user_query, history):
        """Processes query using PDF data and branch facts."""
        context = self.knowledge_base[:8000] if self.knowledge_base else "Associated Industries 2026 range."
        
        system_prompt = f"""
        ROLE: RUBY, charismatic Digital Concierge for Associated Industries (PTY) Ltd.
        
        OFFICIAL BRANCH LOCATIONS:
        - JOHANNESBURG (Head Office): 11 Hyser Street, Heriotdale, Johannesburg.
        - DURBAN BRANCH: 12 Caversham Road, Pinetown, Durban.

        RULES:
        1. Always provide the specific addresses above for location queries.
        2. Keep responses under 65 words. Use plain text only (no ** or #).
        3. Represent our 121-year legacy with warmth and professionalism.

        CATALOG DATA:
        {context}
        """
        
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history[-5:]:
            messages.append(msg)
        messages.append({"role": "user", "content": user_query})
            
        try:
            if not self.client:
                raise Exception("API Key Missing")

            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7, 
                max_tokens=250
            )
            return completion.choices[0].message.content
        except:
            # --- INTELLIGENT FALLBACK SAFETY NET ---
            q = user_query.lower()
            if "durban" in q:
                return "Our Durban branch is located at 12 Caversham Road, Pinetown. How can I help you with our range there?"
            if "joburg" in q or "johannesburg" in q or "hyser" in q or "head office" in q:
                return "Our Head Office is in Johannesburg at 11 Hyser Street, Heriotdale. Would you like to hear about our 2026 calendars?"
            return "I've noted your request. I am just refreshing my records of our 2026 catalog. Would you like to hear about our Big Five or Majestic Wonders ranges?"
