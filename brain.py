import os
import PyPDF2
from groq import Groq

class CompanyBrain:
    def __init__(self):
        # Initialize the Groq client with your API key
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        self.model = "llama-3.3-70b-versatile"
        
        # This list matches the 4 files you uploaded to your /library folder
        self.library_files = [
            "library/Part1.pdf",
            "library/Part2.pdf",
            "library/Part3.pdf",
            "library/Part4.pdf"
        ]
        
        # Ruby "reads" the library into her memory when the app starts
        self.knowledge_base = self._load_library()

    def _load_library(self):
        """Reads all 4 split PDFs and merges the text for Ruby's knowledge."""
        combined_text = ""
        for file_path in self.library_files:
            try:
                if os.path.exists(file_path):
                    with open(file_path, "rb") as f:
                        reader = PyPDF2.PdfReader(f)
                        # Extract text from every page of the current PDF part
                        for page in reader.pages:
                            text = page.extract_text()
                            if text:
                                combined_text += text + "\n"
                else:
                    print(f"Librarian Alert: {file_path} was not found in the folder.")
            except Exception as e:
                print(f"Librarian Error reading {file_path}: {e}")
        
        # If the library is found, Ruby will use it; otherwise, she'll rely on general info
        return combined_text if combined_text else "General knowledge only."

    def get_answer(self, user_query, history):
        """Generates an answer using the combined PDF knowledge and conversation history."""
        
        # This prompt tells Ruby exactly how to behave as an Associated Industries expert
        system_prompt = f"""
        You are RUBY, the Digital Concierge for Associated Industries (PTY) Ltd. 
        You are an expert on 2026 Calendars, Diaries, and Notebooks.

        KNOWLEDGE BASE FROM YOUR LIBRARY:
        {self.knowledge_base[:9000]} 

        BEHAVIOUR RULES:
        1. BE SPECIFIC: Use the details from the text (e.g., mention the M82 calendar size is 440mm x 580mm).
        2. B2B TONE: Stay professional, friendly, and helpful. You are a salesperson.
        3. LEAD CAPTURE: If they ask for pricing or a quote, confirm you've captured their details and tell them a sales rep will be in touch.
        4. NO BANK SPECS: Do not give out bank details in the chat. Tell them a pro-forma invoice will be sent to their email.
        """
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # We include the last few messages for context so Ruby remembers what was said
        for msg in history[-5:]:
            messages.append(msg)
            
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.5,
                max_tokens=600
            )
            return completion.choices[0].message.content
        except Exception as e:
            return "I apologize, but my brain is currently resetting. How else can I help you today?"
