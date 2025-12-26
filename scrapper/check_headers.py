
import os
import json
from .services.sheet_service import GoogleSheetClient

def check_headers():
    print("Checking Sheet Headers...")
    client = GoogleSheetClient(os.path.join(os.path.dirname(__file__), '..', 'config', 'settings.json'))
    client.connect()
    
    rows = client.get_rows()
    if rows:
        print(f"Found {len(rows)} rows.")
        print("First row keys (HEADERS):")
        print(list(rows[0].keys()))
    else:
        print("Sheet is empty or connection failed to retrieve rows.")

if __name__ == "__main__":
    check_headers()
