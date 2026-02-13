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
                    print(f"Loading Error: {e}")
        return combined_text

    def get_answer(self, user_query, history):
        # We use a smart-sized context to prevent the 'AttributeError' crash
        context = self.knowledge_base[:12000] if self.knowledge_base else "Associated Industries"
        
        system_prompt = f"""
        PERSONALITY & SOUL:
        You are RUBY, the charismatic and sophisticated Digital Concierge for Associated Industries (PTY) Ltd.
        You have a brilliant intellect and a helpful South African soul. You aren't a robot; 
        you are a high-level brand ambassador. Be warm, engaging, and professional.

        THE RULES OF TRUTH:
        1. PRODUCT SPECS: Use ONLY the PDF data below for sizes, codes, and themes. 
           If it's in the PDF, you are the expert. If it's NOT in the PDF, say "I don't have that 
           exact detail in my 2026 showcase yet, but I can find out for you."
        2. COMPANY INFO: 
           - Phone: 011 621 4130
           - Email: info@associatedindustries.co.za
           - Website: www.associatedindustries.co.za
        3. NO CUTOFFS: You have a massive budget of 1500 tokens. Use them to finish every thought.
        4. NO HALLUCINATIONS: Never make up phone numbers or spec details.

        CATALOG DATA (YOUR SOURCE OF TRUTH):
        {context}
        """
        
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history[-5:]:
            messages.append(msg)
            
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7, # The 'Soul' setting - makes her sound human
                max_tokens=1500, # The 'Finish the sentence' setting
                top_p=0.9
            )
            return completion.choices[0].message.content
        except Exception as e:
            # This 'Except' block prevents the app from crashing with an AttributeError
            return "I'm so sorry, Kaveer, I had a momentary lapse in thought! Could you please repeat that? I want to make sure I give you the perfect answer."
