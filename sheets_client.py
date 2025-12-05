import gspread
from google.oauth2.service_account import Credentials
import config
import os
import streamlit as st
import json

class SheetsClient:
    def __init__(self):
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds_file = config.GOOGLE_SHEETS_CREDENTIALS_FILE
        
        if os.path.exists(creds_file):
            credentials = Credentials.from_service_account_file(
                creds_file,
                scopes=scopes
            )
        elif hasattr(st, "secrets") and "google_credentials" in st.secrets:
            # Load from secrets
            creds_dict = st.secrets["google_credentials"]
            # If it's a string (JSON), parse it. If it's already a dict (TOML), use it.
            if isinstance(creds_dict, str):
                 creds_dict = json.loads(creds_dict)
            
            credentials = Credentials.from_service_account_info(
                creds_dict,
                scopes=scopes
            )
        else:
            raise FileNotFoundError(f"Could not find credentials file '{creds_file}' or 'google_credentials' in secrets.")

        self.gc = gspread.authorize(credentials)
        print(f"DEBUG: Service Account Email: {credentials.service_account_email}")
        self.sheet_id = config.GOOGLE_SHEET_ID
        self.tab_name = config.GOOGLE_SHEET_TAB_NAME

    def append_lead(self, lead_data):
        """
        Appends a lead row to the Google Sheet.
        """
        try:
            sh = self.gc.open_by_key(self.sheet_id)
            try:
                worksheet = sh.worksheet(self.tab_name)
            except gspread.exceptions.WorksheetNotFound:
                # Create worksheet if it doesn't exist
                worksheet = sh.add_worksheet(title=self.tab_name, rows=1000, cols=25)
                # Add headers
            # Map lead_data to columns based on config.INSTANTLY_HEADERS
            # Headers: name, email, YouTube handle, about link, transcript, channel name, channel ID, product, product name
            
            # If worksheet is empty, add headers
            if worksheet.row_count == 0 or not worksheet.row_values(1):
                 worksheet.append_row(config.INSTANTLY_HEADERS)

            row = []
            for header in config.INSTANTLY_HEADERS:
                if header == "name":
                    row.append(lead_data.get('contact_name', ''))
                elif header == "email":
                    row.append(lead_data.get('email', ''))
                elif header == "YouTube handle":
                    row.append(lead_data.get('channel_url', ''))
                elif header == "about link":
                    row.append("") # Placeholder as requested
                elif header == "transcript":
                    row.append(lead_data.get('last_video_paraphrase', ''))
                elif header == "Loom code":
                    row.append("") # Placeholder for manual entry
                elif header == "Loom URL":
                    row.append("") # Placeholder for manual entry
                elif header == "Spacer H":
                    row.append("") # Spacer
                elif header == "channel name":
                    row.append(lead_data.get('channel_title', ''))
                elif header == "Spacer J":
                    row.append("") # Spacer
                elif header == "channel ID":
                    row.append(lead_data.get('channel_id', ''))
                elif header == "product":
                    # Use description as requested, fallback to type
                    desc = lead_data.get('product_description', '')
                    ptype = lead_data.get('product_type', '')
                    if desc:
                        row.append(desc)
                    else:
                        row.append(ptype)
                elif header == "product name":
                    row.append(lead_data.get('product_name', ''))
                else:
                    row.append("")

            
            worksheet.append_row(row)
            return True
        except Exception as e:
            print(f"Google Sheets error: {repr(e)}")
            import traceback
            traceback.print_exc()
            return False
