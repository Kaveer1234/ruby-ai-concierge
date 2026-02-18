import os
import PyPDF2
from groq import Groq

class CompanyBrain:
    def __init__(self):
        self.api_key = os.environ.get("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.model = "llama-3.3-70b-versatile"
        self.library_files = ["library/products.txt", "library/Part1_compressed.pdf", "library/Part2_compressed.pdf"]
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
                            text = page.extract_text()
                            if text: combined_text += text + "\n"
                except: pass
        return combined_text

    def get_answer(self, user_query, history):
        # Dynamically find the name from history for fallback use
        user_name = "there"
        for msg in history:
            if "pleasure to meet you, " in msg["content"]:
                user_name = msg["content"].split("pleasure to meet you, ")[1].split("!")[0]

        context = self.knowledge_base[:8000] if self.knowledge_base else "Associated Industries 2026 range."
        
        system_prompt = f"""
        ROLE: You are RUBY, a sophisticated Digital Concierge for Associated Industries.
        DYNAMIC RULES:
        1. Address the user by their name: {user_name}.
        2. If they ask for "multisheet calendars," describe the 2026 Majestic Wonders and Nature's Gallery. 
        3. Branches: Joburg (11 Hyser St, Heriotdale) and Durban (12 Caversham Rd, Pinetown). 
        4. No Markdown. Keep it under 50 words. 
        """
        
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history[-5:]: messages.append(msg)
        messages.append({"role": "user", "content": user_query})
            
        try:
            if not self.client: raise Exception("Offline")
            completion = self.client.chat.completions.create(
                model=self.model, messages=messages, temperature=0.7, max_tokens=250
            )
            return completion.choices[0].message.content
        except:
            # --- IMPROVED DYNAMIC FALLBACK ---
            q = user_query.lower()
            
            if any(x in q for x in ["no thanks", "goodbye", "nothing else"]):
                return f"It was a pleasure assisting you, {user_name}! Have a wonderful day further." 
            
            if "multisheet" in q:
                return f"We certainly do, {user_name}! Our 2026 multisheet range is breathtaking. Would you like a quote on those?" 
            
            if any(x in q for x in ["branch", "based", "located", "where are you"]):
                return "We have our Head Office in Heriotdale, Joburg, and our coastal branch in Pinetown, Durban. Which is more convenient for you?"

            return f"I've noted that, {user_name}! I'm just pulling up the latest 2026 catalog details for you. What else can I help you find?"

