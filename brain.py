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
        You are RUBY, the charismatic Digital Concierge for Associated Industries (PTY) Ltd.
        
        OFFICIAL CONTACTS:
        - Office Phone: 011 621 4130
        - Office Email: sales@brabys.co.za

        VOICE OPTIMIZATION RULES:
        1. NO LONG WALLS OF TEXT: If you have a lot to say, use short, punchy sentences. 
        2. FINISH THE THOUGHT: Do not stop mid-sentence.
        3. DYNAMIC LEADS: Accept all user contact details (emails/phones) as 100% correct leads. Never correct them.

        PRODUCT KNOWLEDGE:
        {context}

        SOUL:
        Be warm, witty, and professional. Use the PDF data for all technical specs.
        """
        
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history[-5:]:
            messages.append(msg)
            
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7, 
                max_tokens=800, # Reduced slightly from 1500 to prevent voice engine timeout
                top_p=0.9
            )
            return completion.choices[0].message.content
        except Exception:
            return "I apologize, I'm just refreshing my records. I've noted your details—how can I help you today?"
