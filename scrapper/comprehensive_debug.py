
import os
import json
import traceback
import sys
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

def debug_connection():
    print("=== SOCIAL MEDIA SCRAPPER DIAGNOSTIC ===")
    
    # 1. VERIFY PATHS
    base_dir = os.path.dirname(os.path.abspath(__file__)) # scrapper/
    project_root = os.path.dirname(base_dir)
    creds_path = os.path.join(project_root, 'config', 'credentials.json')
    config_path = os.path.join(project_root, 'config', 'settings.json')
    
    print(f"[PATH] Credentials: {creds_path}")
    if not os.path.exists(creds_path):
        print("FAIL: credentials.json not found.")
        return

    # 2. VERIFY CREDENTIALS & API ENABLEMENT
    try:
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/service.management.readonly'
        ]
        creds = Credentials.from_service_account_file(creds_path, scopes=scope)
        print(f"[AUTH] Service Account Email: {creds.service_account_email}")
        print("[AUTH] Credentials loaded successfully.")
    except Exception as e:
        print(f"FAIL: Invalid credentials file. Error: {e}")
        return

    # 3. TEST DRIVE API (List permissions)
    try:
        service = build('drive', 'v3', credentials=creds)
        # Try to list files to check if API works
        results = service.files().list(pageSize=10, fields="nextPageToken, files(id, name)").execute()
        files = results.get('files', [])
        print(f"[DRIVE API] Success. Found {len(files)} files accessible to this service account.")
        if not files:
            print("[DRIVE API] WARNING: This account sees 0 files. Did you share the sheet?")
        for f in files:
            print(f"  - File: {f['name']} (ID: {f['id']})")
    except Exception as e:
        print(f"[DRIVE API] FAIL: Could not list files. Are Drive API/Sheets API enabled in Cloud Console? Error: {e}")
        # Don't return, try gspread anyway

    # 4. GSPREAD CONNECTION
    try:
        client = gspread.authorize(creds)
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        target_id = config['google_sheets']['spreadsheet_id']
        target_ws_name = config['google_sheets']['worksheet_name']
        
        print(f"[CONFIG] Target Spreadsheet ID: {target_id}")
        
        # Open Spreadsheet
        sheet = client.open_by_key(target_id)
        print(f"[SHEET] Success! Access to '{sheet.title}' verified.")
        
        # Check Worksheets
        print(f"[WS] Looking for worksheet: '{target_ws_name}'")
        found_ws = False
        print("[WS] Available worksheets:")
        for ws in sheet.worksheets():
            print(f"  - '{ws.title}' (ID: {ws.id})")
            if ws.title == target_ws_name:
                found_ws = True
        
        if found_ws:
            print(f"[WS] SUCCESS: Target worksheet '{target_ws_name}' exists.")
        else:
            print(f"[WS] FAIL: Worksheet '{target_ws_name}' NOT found. Please check spelling/casing exact match.")
            
    except Exception as e:
        print(f"\n[FAIL] ERROR: {type(e).__name__}")
        print(f"Message: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_connection()
