import gspread
from google.oauth2.service_account import Credentials


def write_to_sheet(data, credentials_file, spreadsheet_id, sheet_name='Sheet1'):
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_file(credentials_file, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(spreadsheet_id).worksheet(sheet_name)


    for item in data:
        sheet.append_row([item.get('title', ''), item.get('url', ''), item.get('views', ''), item.get('likes', '')])