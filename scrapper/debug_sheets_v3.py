
import os
import json
import traceback
from google.oauth2.service_account import Credentials
import gspread

def test_connection():
    print("--- DEBUG V3 START ---")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(base_dir)
    config_path = os.path.join(project_root, 'config', 'settings.json')
    creds_path = os.path.join(project_root, 'config', 'credentials.json')

    # Load Config
    with open(config_path, 'r') as f:
        config = json.load(f)
    sheet_id = config['google_sheets']['spreadsheet_id']
    worksheet_name = config['google_sheets']['worksheet_name']

    # Connect
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_file(creds_path, scopes=scope)
        client = gspread.authorize(creds)
        print("Authorized.")
        
        print(f"Opening Sheet ID: {sheet_id}")
        sheet = client.open_by_key(sheet_id)
        print(f"Spreadsheet Title: '{sheet.title}'")
        
        print("Worksheets found:")
        ws_list = sheet.worksheets()
        found = False
        for ws in ws_list:
            print(f" - '{ws.title}'")
            if ws.title == worksheet_name:
                found = True
                
        if found:
            print(f"Target worksheet '{worksheet_name}' FOUND.")
        else:
            print(f"Target worksheet '{worksheet_name}' NOT FOUND.")
            
    except Exception as e:
        print(f"\nERROR TYPE: {type(e).__name__}")
        print(f"ERROR MSG: {e}")
        # print traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_connection()
