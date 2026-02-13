def get_answer(self, user_query, history):
        context = self.knowledge_base[:12000] if self.knowledge_base else "Associated Industries"
        
        system_prompt = f"""
        ROLE:
        You are RUBY, the intelligent Digital Concierge for Associated Industries (PTY) Ltd.
        
        TRUTH & ACCURACY:
        - Use ONLY the provided CATALOG DATA for product facts.
        - If a user asks for something we DON'T have (like monkeys), say: "While we don't have that specific theme this year, we have some incredible alternatives like..."
        - Pivot to our actual 2026 themes: Majestic Wonders, Africa in Action, Tranquillity, and The Big Five.

        VOICE OPTIMIZATION:
        - Keep responses short (under 80 words) to prevent voice cut-offs.
        - Speak clearly and finish every sentence.

        CATALOG DATA:
        {context}

        CONTACTS:
        - Email: sales@brabys.co.za
        - Phone: 011 621 4130
        """
        
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history[-5:]:
            messages.append(msg)
            
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.5, # Lowered for more factual accuracy
                max_tokens=350, 
                top_p=0.9
            )
            return completion.choices[0].message.content
        except Exception:
            return "I apologize, Kaveer. Let's look at our 2026 catalog together—what can I find for you?"
