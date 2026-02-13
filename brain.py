import os
import PyPDF2
from groq import Groq

# Safety Check for the main script
__all__ = ['CompanyBrain']

class CompanyBrain:
    def __init__(self):
        # Initialize Groq with safety check
        self.api_key = os.environ.get("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.model = "llama-3.3-70b-versatile"
        
        # Library setup - matching your uploaded compressed files
        self.library_files = [
            "library/Part1_compressed.pdf",
            "library/Part2_compressed.pdf",
            "library/Part3_compressed.pdf",
            "library/Part4_compressed.pdf"
        ]
        self.knowledge_base = self._load_library()

    def _load_library(self):
        """Reads the PDFs from the library folder for catalog knowledge."""
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
                except Exception as e:
                    print(f"Librarian Error reading {file_path}: {e}")
        return combined_text

    def get_answer(self, user_query, history):
        """Processes the query using PDF context and the Official Branch details."""
        # Balanced context window to provide facts without crashing the voice engine
        context = self.knowledge_base[:10000] if self.knowledge_base else "Associated Industries 2026 range."
        
        system_prompt = f"""
        ROLE:
        You are RUBY, the charismatic and intelligent Digital Concierge for Associated Industries (PTY) Ltd.
        You represent a 121-year-old legacy. Be professional and warm.

        OFFICIAL BRANCH LOCATIONS:
        - JOHANNESBURG (Head Office): 11 Hyser Street, Heriotdale, Johannesburg.
        - DURBAN BRANCH: 12 Caversham Road, Pinetown, Durban.

        TRUTH & VOICE RULES (CRITICAL):
        1. NO HALLUCINATIONS: Use ONLY the CATALOG DATA for product facts.
        2. ADDRESSES: Use the specific addresses above for any location questions.
        3. NO MONKEYS: We do not have monkey themes. Pivot to Wildlife (The Big Five) or Nature if asked.
        4. VOICE SAVER: Keep responses under 75 words. Use short sentences so the voice engine doesn't cut off.
        5. NO MARKDOWN: Do not use stars (**) or hashes (#) in your speech.
        6. DYNAMIC LEADS: Accept whatever Name, Company, or Email the user provides. Never correct the user's email.

        OFFICIAL CONTACTS:
        - Email: sales@brabys.co.za
        - Phone: 011 621 4130

        CATALOG DATA (SOURCE OF TRUTH):
        {context}
        """
        
        messages = [{"role": "system", "content": system_prompt}]
        # Include recent history for flow
        for msg in history[-5:]:
            messages.append(msg)
        
        # Add the current user prompt
        messages.append({"role": "user", "content": user_query})
            
        try:
            if not self.client:
                return "I'm having a little trouble connecting to my database. How can I help you manually?"

            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7, 
                max_tokens=350, 
                top_p=0.9
            )
            return completion.choices[0].message.content
        except Exception as e:
            return "I apologize, I'm just refreshing my records. We have branches in Heriotdale and Pinetown—how can I help you today?"
