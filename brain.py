import re
import os
import random
from gtts import gTTS
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

class CompanyBrain:
    def __init__(self, library_path="library.txt", creds_json="service_account.json", sheet_name="Leads"):
        # Load the knowledge base from .txt file
        self.library = self.load_library(library_path)
        self.last_lead = {}
        self.last_quote = {}

        # Setup Google Sheets
        scope = ["https://spreadsheets.google.com/feeds",
                 "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_json, scope)
        client = gspread.authorize(creds)
        self.sheet = client.open(sheet_name).sheet1

    # -----------------------------
    # Library handling
    # -----------------------------
    def load_library(self, path):
        if not os.path.exists(path):
            print(f"[Warning] Library file {path} not found.")
            return []
        with open(path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        return lines

    def search_library(self, user_input):
        """
        Return a response from the library that matches user input.
        If none found, return a default friendly response.
        """
        user_input_lower = user_input.lower()
        for line in self.library:
            if user_input_lower in line.lower():
                return line
        # fallback random friendly reply
        return random.choice([
            "Oh, that sounds exciting! Let me see how I can help you 😊",
            "I love helping with that! Can you tell me a bit more?",
            "Absolutely! I’m on it 💖"
        ])

    # -----------------------------
    # Lead capture
    # -----------------------------
    def capture_lead(self, field, value):
        """
        Capture the lead fields: name, company, phone, email
        Update Google Sheet immediately when all four are collected.
        """
        self.last_lead[field] = value

        required_fields = ["name", "company", "phone", "email"]
        missing = [f for f in required_fields if f not in self.last_lead]

        if missing:
            # Ask for next missing field casually
            next_field = missing[0]
            return f"Could you please tell me your {next_field}? 🙂"
        else:
            # All fields collected → push to Google Sheet
            self.update_sheet_lead(self.last_lead)
            # Clear last_lead for next customer
            self.last_lead = {}
            return "Thanks so much! I’ve got all your details now. How can I assist you today with our calendars? 🌟"

    def update_sheet_lead(self, lead_data):
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            lead_data.get("name", ""),
            lead_data.get("company", ""),
            lead_data.get("phone", ""),
            lead_data.get("email", "")
        ]
        self.sheet.append_row(row)

    # -----------------------------
    # Quote capture
    # -----------------------------
    def capture_quote(self, field, value):
        """
        Capture quote info: type, quantity, colors, budget
        Update Google Sheet immediately when all fields are collected.
        """
        self.last_quote[field] = value
        required_fields = ["type", "quantity", "colors", "budget"]
        missing = [f for f in required_fields if f not in self.last_quote]

        if missing:
            next_field = missing[0]
            prompt = {
                "type": "Which type of calendar are you interested in? 📅",
                "quantity": "Great! How many would you like? 📝",
                "colors": "Perfect! What colors do you want for the overprint? 🎨",
                "budget": "Got it. If possible, what’s your budget? 💰"
            }
            return prompt[next_field]
        else:
            # All fields collected → push to Google Sheet
            self.update_sheet_quote(self.last_quote)
            self.last_quote = {}
            return "Awesome! I’ve recorded your quote request. Our team will get back to you shortly. 💖"

    def update_sheet_quote(self, quote_data):
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            quote_data.get("type", ""),
            quote_data.get("quantity", ""),
            quote_data.get("colors", ""),
            quote_data.get("budget", "")
        ]
        self.sheet.append_row(row)

    # -----------------------------
    # Generate response
    # -----------------------------
    def generate_response(self, user_input):
        """
        Determine whether we are in lead capture, quote capture, or general conversation.
        """
        # simple heuristic to detect fields
        field_map = {
            "name": ["my name is", "i am", "this is"],
            "company": ["company", "business", "organisation", "organization"],
            "phone": ["phone", "tel", "call me", "number"],
            "email": ["email", "e-mail"],
            "type": ["calendar", "product type", "type of calendar"],
            "quantity": ["quantity", "how many", "amount"],
            "colors": ["colors", "colour", "overprint"],
            "budget": ["budget", "price range"]
        }

        # check lead capture first
        for field in ["name", "company", "phone", "email"]:
            if any(kw in user_input.lower() for kw in field_map[field]):
                return self.capture_lead(field, user_input)

        # check quote capture
        for field in ["type", "quantity", "colors", "budget"]:
            if any(kw in user_input.lower() for kw in field_map[field]):
                return self.capture_quote(field, user_input)

        # default to library search / personality response
        return self.search_library(user_input)
