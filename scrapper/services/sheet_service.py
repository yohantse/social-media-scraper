import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict, Any
import os
import json
from .logger import setup_logger

logger = setup_logger('sheet_service')

class GoogleSheetClient:
    def __init__(self, config_path: str):
        """Initialize connection to Google Sheets."""
        self.config = self._load_config(config_path)
        self.client = None
        self.sheet = None
        self.headers = {}
        
    def _load_config(self, path: str) -> dict:
        with open(path, 'r') as f:
            return json.load(f)['google_sheets']

    def connect(self):
        """Authenticate and open the spreadsheet."""
        try:
            creds_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                      'config', 'credentials.json')
            
            # Allow for absolute path in config or relative resolution
            if not os.path.exists(creds_file):
                 # Fallback to configured path if exists
                 configured_path = self.config.get('credentials_file')
                 if os.path.exists(configured_path):
                     creds_file = configured_path
            
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            creds = Credentials.from_service_account_file(creds_file, scopes=scope)
            self.client = gspread.authorize(creds)
            
            self.sheet = self.client.open_by_key(self.config['spreadsheet_id']).worksheet(self.config['worksheet_name'])
            logger.info("Successfully connected to Google Sheet")
            
            # Map headers
            header_row = self.sheet.row_values(1)
            for idx, col_name in enumerate(header_row):
                self.headers[col_name] = idx + 1 # 1-based index
                
        except Exception as e:
            logger.error(f"Failed to connect to Google Sheets: {e}")
            raise

    def get_rows(self) -> List[dict]:
        """Fetch all records from the sheet."""
        if not self.sheet:
            self.connect()
        return self.sheet.get_all_records()

    def update_row(self, row_index: int, data: Dict[str, Any]):
        """
        Update a specific row with new data.
        row_index is 2-based (header is 1).
        data keys should match the column names in settings.json.
        """
        if not self.sheet:
            self.connect()
            
        settings_cols = self.config['columns']
        updates = []
        
        for key, value in data.items():
            # Get the actual sheet header name from config
            col_header = settings_cols.get(key)
            if not col_header:
                # Try to see if key is the header itself? No, strict mapping.
                # If key is not in config, we can't map it.
                # But 'status' and 'platform' might be in config.
                continue
                
            if col_header in self.headers:
                col_idx = self.headers[col_header]
                updates.append({
                    'range': gspread.utils.rowcol_to_a1(row_index, col_idx),
                    'values': [[value]]
                })
            else:
                logger.warning(f"Column '{col_header}' (for key '{key}') not found in sheet headers")

        if updates:
            try:
                self.sheet.batch_update(updates)
                logger.info(f"Updated row {row_index} with {list(data.keys())}")
            except Exception as e:
                logger.error(f"Failed to batch update row {row_index}: {e}")
