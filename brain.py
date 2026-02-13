import os
import PyPDF2
from groq import Groq

class CompanyBrain:
    def __init__(self):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"
        
        # EXACT matches for the files you just moved into /library
        self.library_files = [
            "library/Part1_compressed.pdf",
            "library/Part2_compressed.pdf",
            "library/Part3_compressed.pdf",
            "library/Part4_compressed.pdf"
        ]
        self.knowledge_base = self._load_library()

    def _load_library(self):
        """Reads the compressed PDFs and merges the text for Ruby."""
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
                    print(f"Librarian Error reading {file_path}: {e}")
        return combined_text

    def get_answer(self, user_query, history):
        # We give Ruby the first 9000 characters of catalog data for context
        context = self.knowledge_base[:9000] if self.knowledge_base else "Associated Industries specialist."
        
        system_prompt = f"""
        You are RUBY, the Digital Concierge for Associated Industries (PTY) Ltd.
        
        OUR 2026 CATALOG DATA:
        {context}
        
        RULES:
        1. If asked about product specs, use the catalog data (e.g. M82 is 440mm x 580mm).
        2. If info is missing, say 'I will confirm that with our production team'.
        3. Maintain a professional South African tone.
        4. Capture customer contact info (Email/Phone) for any quote requests.
        """
        
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history[-5:]:
            messages.append(msg)
            
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.4,
                max_tokens=500
            )
            return completion.choices[0].message.content
        except:
            return "I am currently refreshing my catalog knowledge. How can I help you in the meantime?"
