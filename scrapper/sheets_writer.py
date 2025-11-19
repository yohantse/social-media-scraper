import gspread
from google.oauth2.service_account import Credentials


def write_to_sheet(data, credentials_file, spreadsheet_id, sheet_name='Sheet1'):
    """Write scraped data to Google Sheets."""
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_file(credentials_file, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(spreadsheet_id).worksheet(sheet_name)

    # Check if sheet is empty and add headers
    if not sheet.get_all_values():
        headers = ['Platform', 'Title', 'URL', 'Views', 'Likes', 'Comments', 'Shares', 'Error']
        sheet.append_row(headers)

    # Append data rows
    for item in data:
        row = [
            item.get('platform', 'N/A'),
            item.get('title', 'N/A'),
            item.get('url', 'N/A'),
            str(item.get('views', 'N/A')),
            str(item.get('likes', 'N/A')),
            str(item.get('comments', 'N/A')),
            str(item.get('shares', 'N/A')),
            item.get('error', '')
        ]
        sheet.append_row(row)