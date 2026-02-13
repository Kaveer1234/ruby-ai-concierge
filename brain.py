import os
import PyPDF2
from groq import Groq

class CompanyBrain:
    def __init__(self):
        # Initialize Groq with safety check
        self.api_key = os.environ.get("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.model = "llama-3.3-70b-versatile"
        
        self.library_files = [
            "library/Part1_compressed.pdf",
            "library/Part2_compressed.pdf",
            "library/Part3_compressed.pdf",
            "library/Part4_compressed.pdf"
        ]
        self.knowledge_base = self._load_library()

    def _load_library(self):
        """Reads the PDFs from the library folder."""
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
                    print(f"Error loading {file_path}: {e}")
        return combined_text

    def get_answer(self, user_query, history):
        """This function must be indented inside the CompanyBrain class!"""
        context = self.knowledge_base[:12000] if self.knowledge_base else "Associated Industries 2026 range."
        
        system_prompt = f"""
        ROLE:
        You are RUBY, the charismatic and sophisticated Digital Concierge for Associated Industries (PTY) Ltd. 
        You are professional, intelligent, and warm.
        
        TRUTH & ACCURACY:
        - Use ONLY the provided CATALOG DATA for product facts.
        - NO MONKEYS: We do not have monkey themes. If asked, pivot to Wildlife (The Big Five) or Nature themes.
        - If the info isn't in the data, offer to have a human specialist contact them.

        VOICE OPTIMIZATION (CRITICAL):
        - Keep responses short (under 75 words) to prevent voice cut-offs.
        - Do not use special characters or complex Markdown.
        - Speak clearly and finish every sentence.

        OFFICIAL CONTACTS:
        - Email: sales@brabys.co.za
        - Phone: 011 621 4130

        CATALOG DATA:
        {context}
        """
        
        messages = [{"role": "system", "content": system_prompt}]
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
                temperature=0.7, # Balanced for 'Soul' and facts
                max_tokens=300,  # Short and sweet for the voice engine
                top_p=0.9
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Groq Error: {e}")
            return "I apologize, I'm just refreshing my catalog memory. What can I find for you in our 2026 range?"
