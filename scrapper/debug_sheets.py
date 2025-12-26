
import os
import json
import traceback
from google.oauth2.service_account import Credentials
import gspread

def test_connection():
    print("Testing Google Sheets Connection...")
    
    # 1. Resolve Paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir) # assumes scrapper/debug.py -> project_root
    config_path = os.path.join(project_root, 'config', 'settings.json')
    creds_path = os.path.join(project_root, 'config', 'credentials.json')
    
    print(f"Config Path: {config_path}")
    print(f"Creds Path: {creds_path}")
    
    if not os.path.exists(creds_path):
        print("ERROR: credentials.json NOT FOUND!")
        return

    # 2. Load Config
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        print("Settings loaded.")
    except Exception as e:
        print(f"ERROR Loading Settings: {e}")
        return

    # 3. Connect
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_file(creds_path, scopes=scope)
        client = gspread.authorize(creds)
        print("Authenticated with Google.")
        
        spreadsheet_id = config['google_sheets']['spreadsheet_id']
        worksheet_name = config['google_sheets']['worksheet_name']
        print(f"Opening Spreadsheet ID: {spreadsheet_id}")
        
        sheet = client.open_by_key(spreadsheet_id)
        print(f"Spreadsheet Title: {sheet.title}")
        
        print(f"Opening Worksheet: {worksheet_name}")
        worksheet = sheet.worksheet(worksheet_name)
        print("SUCCESS! Worksheet accessed.")
        
    except Exception:
        print("\n--- FAILURE TRACEBACK ---")
        traceback.print_exc()
        print("-------------------------")

if __name__ == "__main__":
    test_connection()
