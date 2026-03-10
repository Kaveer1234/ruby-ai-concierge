import streamlit as st
from groq import Groq
import os
import re

class CompanyBrain:

    def __init__(self, library_path=None):

        # Load API key from Streamlit
        self.api_key = st.secrets["GROQ_API_KEY"]

        # Initialize Groq client
        self.client = Groq(api_key=self.api_key)

        # Fast chat model
        self.model = "llama-3.1-8b-instant"

        self.library_file = library_path if library_path else "library/products.txt"
        self.knowledge_base = self._load_library()


    def _load_library(self):

        if os.path.exists(self.library_file):
            try:
                with open(self.library_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    return re.sub(r'\[(?:source|cite): [\d, ]+\]', '', content)
            except:
                return "Our 2027 collection is breathtaking!"

        return "Associated Industries 2027 range."


    def get_answer(self, user_query, history):

        user_name = "there"

        if "User:" in user_query:
            try:
                user_name = user_query.split("User: ")[1].split(" from")[0]
            except:
                pass


        system_prompt = f"""
You are RUBY, the friendly digital representative for Associated Industries.

PERSONALITY
Warm, upbeat, conversational and professional.
Speak like a helpful sales assistant, not a robot.

CONVERSATION RULES
• Greet the user only once at the start of the conversation.
• Do not repeat the user's name in every reply.
• Use their name occasionally.
• Keep replies natural and conversational.

PRODUCT RULES
• When asked for themes or codes, list them clearly.
• Never invent products, themes, or codes.
• Only use information from the company knowledge base.

STYLE
• No markdown.
• Maximum 50 words per reply.
• Keep responses clear and helpful.

COMPANY KNOWLEDGE
{self.knowledge_base}
"""


        messages = [{"role": "system", "content": system_prompt}]

        for msg in history[-6:]:
            messages.append(msg)

        messages.append({"role": "user", "content": user_query})


        try:

            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=200
            )

            return completion.choices[0].message.content


        except Exception as e:
            return f"Ruby is having a small technical hiccup: {str(e)}"
