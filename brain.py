import os
import PyPDF2
from groq import Groq

# Safety Check for the main script
__all__ = ['CompanyBrain']

class CompanyBrain:
    def __init__(self):
        # Initialize Groq with environment variable
        self.api_key = os.environ.get("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.model = "llama-3.3-70b-versatile"
        
        # Library setup - Ensure these files exist in your 'library' folder
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
        # Return a snippet to keep the brain fast and responsive
        return combined_text

    def get_answer(self, user_query, history):
        """Processes query using hardcoded branch facts and PDF catalog data."""
        # Use a 8000 character window for the fastest response time
        context = self.knowledge_base[:8000] if self.knowledge_base else "Associated Industries 2026 range."
        
        system_prompt = f"""
        ROLE:
        You are RUBY, the charismatic Digital Concierge for Associated Industries (PTY) Ltd.
        You represent a 121-year-old legacy. Be professional, warm, and witty.

        OFFICIAL BRANCH LOCATIONS:
        - JOHANNESBURG (Head Office): 11 Hyser Street, Heriotdale, Johannesburg.
        - DURBAN BRANCH: 12 Caversham Road, Pinetown, Durban.

        TRUTH & VOICE RULES (CRITICAL):
        1. ADDRESSES: Always use the specific Hyser Street and Caversham Road addresses for location queries.
        2. NO HALLUCINATIONS: Use ONLY the CATALOG DATA for product facts.
        3. NO MONKEYS: We do not have monkey themes. Pivot to Wildlife (The Big Five) or Nature if asked.
        4. VOICE SAVER: Keep responses under 65 words. This is vital to prevent the voice engine from cutting off.
        5. NO MARKDOWN: Do not use stars (**) or hashes (#) in your speech. Use plain text only.
        6. LEADS: Acknowledge the user's details warmly.

        OFFICIAL CONTACTS:
        - Email: sales@brabys.co.za
        - Phone: 011 621 4130

        CATALOG DATA:
        {context}
        """
        
        messages = [{"role": "system", "content": system_prompt}]
        # Keep the last 5 messages for conversation memory
        for msg in history[-5:]:
            messages.append(msg)
        
        # Add current prompt
        messages.append({"role": "user", "content": user_query})
            
        try:
            if not self.client:
                return "I've noted your request. I'm currently working without my full database, but I can tell you our head office is in Heriotdale. How can I help?"

            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7, 
                max_tokens=250, # Optimized for fast speech generation
                top_p=0.9
            )
            return completion.choices[0].message.content
        except Exception as e:
            # Smart fallback that keeps the conversation moving
            return "I've got your details! My catalog is just refreshing. Would you like to hear about our 2026 'Big Five' or 'Majestic Wonders' calendars?"
