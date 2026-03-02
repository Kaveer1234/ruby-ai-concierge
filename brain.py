import os
import PyPDF2
from groq import Groq

class CompanyBrain:
    def __init__(self):
        self.api_key = os.environ.get("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key) if self.api_key else None
        self.model = "llama-3.3-70b-versatile"
        self.library_files = [
            "library/products.txt", 
            "library/Part1_compressed.pdf", 
            "library/Part2_compressed.pdf"
        ]
        self.knowledge_base = self._load_library()

    def _load_library(self):
        combined_text = ""
        for file_path in self.library_files:
            if os.path.exists(file_path):
                try:
                    if file_path.endswith(".txt"):
                        with open(file_path, "r", encoding="utf-8") as f:
                            combined_text += f.read() + "\n"
                    elif file_path.endswith(".pdf"):
                        with open(file_path, "rb") as f:
                            reader = PyPDF2.PdfReader(f)
                            for page in reader.pages:
                                text = page.extract_text()
                                if text: combined_text += text + "\n"
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")
        return combined_text

    def get_answer(self, user_query, history):
        # Extract dynamic name from the context injected by app.py
        user_name = "there"
        if "User is " in user_query:
            try:
                user_name = user_query.split("User is ")[1].split(" from")[0]
            except:
                user_name = "there"

        # Context window for product lookup
        context = self.knowledge_base[:12000] if self.knowledge_base else "Associated Industries 2027 range."
        
        system_prompt = f"""
        ROLE: You are RUBY, a sophisticated Digital Concierge for Associated Industries.
        KNOWLEDGE BASE: {context}
        
        DYNAMIC RULES:
        1. Address the user by their name: {user_name}.
        2. Use the KNOWLEDGE BASE to answer product questions (Posters, Calendars, etc).
        3. Branches: Joburg (Heriotdale) and Durban (Pinetown).
        4. ABSOLUTELY NO MARKDOWN (no stars, no bold). Keep it under 50 words.
        5. If a product isn't found, offer a specialist callback.
        """
        
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history[-5:]: 
            messages.append(msg)
        messages.append({"role": "user", "content": user_query})
            
        try:
            if not self.client: raise Exception("Offline")
            completion = self.client.chat.completions.create(
                model=self.model, messages=messages, temperature=0.7, max_tokens=250
            )
            return completion.choices[0].message.content
        except:
            # --- DYNAMIC FALLBACKS ---
            q = user_query.lower()
            if "jumbo" in q or "poster" in q:
                return f"Yes {user_name}, our Jumbo Posters are very popular! They are 900 by 580mm. Shall I get a quote for you?"
            if "multisheet" in q:
                return f"We certainly do, {user_name}! Our 2027 Multisheet range is breathtaking. Shall I get a price for you?"
            return f"I've noted that, {user_name}! I'm just pulling up the latest 2027 catalog details for you. What else can I help you find?"
