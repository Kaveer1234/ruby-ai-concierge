import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random

class CompanyBrain:
    def __init__(self, library_path: str, creds_path: str, sheet_name: str):
        self.sheet_name = sheet_name
        self.library_lines = []
        self.creds_dict = None
        self.sheet = None

        # -------------------------------
        # Load personality library
        # -------------------------------
        if os.path.exists(library_path):
            with open(library_path, "r", encoding="utf-8") as f:
                self.library_lines = [line.strip() for line in f if line.strip()]
        else:
            print(f"⚠️ Library file not found: {library_path}")

        # -------------------------------
        # Load Google Sheets credentials
        # -------------------------------
        if os.path.exists(creds_path):
            with open(creds_path, "r", encoding="utf-8") as f:
                self.creds_dict = json.load(f)
            self._init_sheet()
        else:
            print(f"⚠️ Credentials file not found: {creds_path}")

    # -------------------------------
    # Initialize Google Sheet
    # -------------------------------
    def _init_sheet(self):
        try:
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"
            ]
            creds = ServiceAccountCredentials.from_json_keyfile_dict(
                self.creds_dict, scopes=scope
            )
            client = gspread.authorize(creds)
            self.sheet = client.open(self.sheet_name).sheet1
        except Exception as e:
            print(f"⚠️ Failed to initialize Google Sheet: {e}")
            self.sheet = None

    # -------------------------------
    # Add lead to sheet
    # -------------------------------
    def add_lead(self, name: str, company: str, phone: str, email: str):
        if self.sheet:
            self.sheet.append_row([name, company, phone, email])
        else:
            print("⚠️ Sheet not initialized, cannot add lead.")

    # -------------------------------
    # Add quote request to sheet
    # -------------------------------
    def add_quote(self, lead_data: dict):
        if self.sheet:
            row = [
                lead_data.get("name", ""),
                lead_data.get("company", ""),
                lead_data.get("phone", ""),
                lead_data.get("email", ""),
                lead_data.get("calendar_type", ""),
                lead_data.get("quantity", ""),
                lead_data.get("colours", ""),
                lead_data.get("budget", "")
            ]
            self.sheet.append_row(row)
        else:
            print("⚠️ Sheet not initialized, cannot add quote.")

    # -------------------------------
    # Dynamic response from library
    # -------------------------------
    def respond(self, prompt: str) -> str:
        """
        Returns a line from the personality library that matches the prompt keywords.
        If no match, returns a random line from the library or a fallback greeting.
        """
        if not self.library_lines:
            return "Hello! How can I help you today?"

        # simple keyword matching
        matches = [line for line in self.library_lines if any(word.lower() in line.lower() for word in prompt.split())]

        if matches:
            return random.choice(matches)
        else:
            # fallback: random line from library
            return random.choice(self.library_lines)
