import os
import PyPDF2
from groq import Groq

class CompanyBrain:
    def __init__(self):
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"
        
        # EXACT matches for your library files
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
        # Using a generous slice of the library for context
        context = self.knowledge_base[:12000] if self.knowledge_base else "Associated Industries specialist."
        
        system_prompt = f"""
        You are RUBY, the Digital Concierge for Associated Industries (PTY) Ltd.
        
        OUR 2026 CATALOG DATA:
        {context}
        
        GOLD STANDARD RULES:
        1. Always finish your sentence and complete your thought.
        2. Use specific data (e.g., M82A ad copy is 100mm x 210mm).
        3. If a list is long, provide it clearly but concisely.
        4. Capture customer contact info (Email/Phone) for all leads.
        5. Tone: Professional South African Sales Executive.
        """
        
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history[-5:]:
            messages.append(msg)
            
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3, # Keeps her factual and concise
                max_tokens=1000  # Large enough to prevent cut-offs
            )
            return completion.choices[0].message.content
        except Exception as e:
            return "I am currently processing that request. May I have your email address while I pull up those specific details for you?"
