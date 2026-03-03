import json
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class CompanyBrain:
    def __init__(self, library_path, creds_path, sheet_name):
        self.sheet_name = sheet_name

        # Load personality library
        with open(library_path, "r", encoding="utf-8") as f:
            self.library_lines = [line.strip() for line in f if line.strip()]

        # Load Google Sheets credentials
        with open(creds_path, "r") as f:
            creds_dict = json.load(f)

        scope = ["https://spreadsheets.google.com/feeds",
                 "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open(sheet_name).sheet1

    def add_lead(self, name, company, tel, email):
        """Add a new lead to the Google Sheet"""
        self.sheet.append_row([name, company, tel, email])
        print(f"Lead added: {name}, {company}, {tel}, {email}")

    def add_quote(self, lead_info, calendar_type, quantity, colours, budget):
        """Add a quote request to the sheet, appended to lead row"""
        # lead_info: dict with name, company, tel, email
        row = [lead_info.get("name"), lead_info.get("company"),
               lead_info.get("tel"), lead_info.get("email"),
               calendar_type, quantity, colours, budget]
        self.sheet.append_row(row)
        print(f"Quote added for: {lead_info.get('name')}")

    def respond(self, user_input):
        """Return a response based on the library (simple keyword/random match)"""
        # Check for a keyword in the library lines
        for line in self.library_lines:
            if line.lower() in user_input.lower():
                return line
        # Otherwise, return a random friendly line
        return random.choice(self.library_lines)
