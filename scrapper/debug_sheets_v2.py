
import os
import json
import traceback
import sys
from google.oauth2.service_account import Credentials
import gspread

def test_connection():
    print("--- DEBUG START ---")
    
    # 1. Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)
    config_path = os.path.join(project_root, 'config', 'settings.json')
    creds_path = os.path.join(project_root, 'config', 'credentials.json')
    
    print(f"Credentials Path: {creds_path}")
    if not os.path.exists(creds_path):
        print("!!! CREDENTIALS FILE MISSING !!!")
        return

    # 2. Config
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        sheet_id = config['google_sheets']['spreadsheet_id']
        worksheet_name = config['google_sheets']['worksheet_name']
        print(f"Target Sheet ID: {sheet_id}")
        print(f"Target Worksheet: '{worksheet_name}'")
    except Exception as e:
        print(f"!!! Error reading config: {repr(e)}")
        return

    # 3. Connect
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        print("loading credentials...")
        creds = Credentials.from_service_account_file(creds_path, scopes=scope)
        print(f"Service Account Email: {creds.service_account_email}")
        
        client = gspread.authorize(creds)
        print("Authorized.")
        
        print(f"Attempting to open spreadsheet by key: {sheet_id}")
        sheet = client.open_by_key(sheet_id)
        print(f"Spreadsheet Title: '{sheet.title}'")
        
        print("Listing available worksheets:")
        for ws in sheet.worksheets():
            print(f" - '{ws.title}'")
            
        print(f"Attempting to select worksheet: '{worksheet_name}'")
        worksheet = sheet.worksheet(worksheet_name)
        print("SUCCESS! Worksheet selected.")
        
        print(f"Header Row: {worksheet.row_values(1)}")
        
    except gspread.exceptions.PermissionError:
        print("\n!!! PERMISSION ERROR !!!")
        print("The Service Account does NOT have access to this sheet.")
        print(f"Please ensure you shared the sheet with: {creds.service_account_email}")
        print("Note: Check that you are Editor.")
    except gspread.exceptions.WorksheetNotFound:
        print(f"\n!!! WORKSHEET NOT FOUND !!!")
        print(f"Could not find worksheet named '{worksheet_name}'.")
        print("Please check for typos (case sensitive) or leading/trailing spaces.")
    except Exception as e:
        print(f"\n!!! UNEXPECTED ERROR: {type(e).__name__} !!!")
        print(f"Message: {str(e)}")
        print(f"Repr: {repr(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    test_connection()
