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
        # We give Ruby a large slice of the library to ensure she finds the right specs
        context = self.knowledge_base[:15000] if self.knowledge_base else "Associated Industries"
        
        system_prompt = f"""
        ROLE: 
        You are RUBY, the sophisticated, warm, and highly intelligent Digital Concierge for Associated Industries (PTY) Ltd. 
        You aren't just a bot; you are the soul of the company. You are helpful, witty, and professional.

        OFFICIAL IDENTITY & CONTACTS (NEVER HALLUCINATE THESE):
        - Office Phone: 011 621 4130
        - Office Email: info@associatedindustries.co.za
        - Website: www.associatedindustries.co.za

        YOUR KNOWLEDGE (THE BIBLE):
        Use the following catalog data for ALL product specs, sizes, and themes:
        {context}

        BEHAVIORAL DIRECTIVES:
        1. PERSONALITY: Be charming and intelligent. Use phrases like "I'd be delighted to help," or "Excellent choice, Kaveer." 
        2. DATA INTEGRITY: When asked about a product, consult the 'KNOWLEDGE' above. If the data is there, provide it exactly (e.g., M82 is 440mm x 580mm). 
        3. HONESTY: If a specific detail (like a price) isn't in the data, say: "I don't have that exact figure in my catalog right now, but let's get your details so a human specialist can give you a precise quote."
        4. COMPLETENESS: You have a large 'token budget.' Use it. Never stop mid-sentence. Finish every thought beautifully.
        5. LEAD CAPTURE: Always aim to gather Name, Company, and Email for the sales team.
        """
        
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history[-5:]:
            messages.append(msg)
            
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.6, # This gives her back her 'soul' and conversational intelligence
                max_tokens=1500, # This ensures she has a massive space to finish long answers
                top_p=0.9        # Helps her sound more natural and less like a robot
            )
            return completion.choices[0].message.content
        except Exception as e:
            return "My apologies, Kaveer. I'm just refreshing my records. Could you please leave your email so I can get back to you properly?"
