import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class CompanyBrain:
    def __init__(self, library_path: str, creds_path: str, sheet_name: str):
        self.sheet_name = sheet_name
        self.library = ""
        self.creds_dict = None
        self.sheet = None

        # -------------------------------
        # Load personality library
        # -------------------------------
        if os.path.exists(library_path):
            with open(library_path, "r", encoding="utf-8") as f:
                self.library = f.read()
        else:
            print(f"⚠️ Library file not found: {library_path}")
            self.library = ""  # empty library fallback

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
        """
        lead_data keys: name, company, phone, email, calendar_type, quantity, colours, budget
        """
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
    # Optional: fetch response from personality library
    # -------------------------------
    def respond(self, prompt: str) -> str:
        # basic keyword match example
        if not self.library:
            return "Hello! How can I help you today?"
        for line in self.library.splitlines():
            if prompt.lower() in line.lower():
                return line
        return "Thanks for reaching out! How can I assist you further?"
