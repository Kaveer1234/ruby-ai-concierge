import os
import PyPDF2
from groq import Groq

class CompanyBrain:
    def __init__(self):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"
        self.library_files = [
            "library/Part1_compressed.pdf",
            "library/Part2_compressed.pdf",
            "library/Part3_compressed.pdf",
            "library/Part4_compressed.pdf"
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
                            t = page.extract_text()
                            if t: combined_text += t + "\n"
                except Exception as e:
                    print(f"Error: {e}")
        return combined_text

    def get_answer(self, user_query, history):
        context = self.knowledge_base[:12000] if self.knowledge_base else "Associated Industries"
        
        system_prompt = f"""
        ROLE:
        You are RUBY, the charismatic and intelligent Digital Concierge for Associated Industries (PTY) Ltd.
        You represent a 121-year-old legacy. Be professional, warm, and helpful.

        OFFICIAL COMPANY CONTACTS (GIVE THESE ONLY IF ASKED):
        - Office Phone: 011 621 4130
        - Office Email: sales@brabys.co.za

        LEAD CAPTURE RULES (DYNAMIC):
        1. You are talking to a CUSTOMER. They will provide THEIR own name, company, and email.
        2. GRACIOUS ACCEPTANCE: Whatever email or phone number the customer provides, accept it exactly as it is.
        3. DO NOT CORRECT: Never tell a customer their email is "wrong" just because it doesn't match ours.
        4. MISSION: Collect their Name, Company, and Email so we can send them quotes.

        PRODUCT KNOWLEDGE (SOURCE OF TRUTH):
        Use the following catalog data for all technical specs:
        {context}

        STRICT BEHAVIOR:
        - NO CUTOFFS: Complete every thought beautifully. You have 1500 tokens.
        - SOUL: Maintain your personality, but keep your facts grounded in the PDF.
        """
        
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history[-5:]:
            messages.append(msg)
            
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7, 
                max_tokens=1500,
                top_p=0.9
            )
            return completion.choices[0].message.content
        except Exception:
            return "I apologize, I'm just refreshing my records. I've noted your details—how can I help you with our 2026 range today?"
