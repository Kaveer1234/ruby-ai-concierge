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
        
        VOICE ENGINE OPTIMIZATION (CRITICAL):
        - Ruby, your voice engine cuts off if you speak for too long. 
        - DO NOT provide huge walls of text. 
        - Use short sentences and keep your total response under 150 words.
        - If there is a lot of data, summarize the highlights and ask the user if they want the full technical specs.
        - NEVER stop mid-sentence.

        OFFICIAL CONTACTS:
        - Email: sales@brabys.co.za
        - Phone: 011 621 4130

        PRODUCT KNOWLEDGE:
        {context}

        SOUL:
        Be warm, witty, and helpful. Always accept user contact details as a lead without correcting them.
        """
        
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history[-5:]:
            messages.append(msg)
            
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7, 
                max_tokens=500, # Lowered to ensure the voice engine completes the task
                top_p=0.9
            )
            return completion.choices[0].message.content
        except Exception:
            return "I apologize, I'm just refreshing my records. How can I help you today?"
