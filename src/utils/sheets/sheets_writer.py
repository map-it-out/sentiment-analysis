from googleapiclient.errors import HttpError
from src.utils.sheets.sheets_auth import get_sheets_service
from dotenv import load_dotenv
import os
from datetime import datetime
from pytz import timezone

load_dotenv()

def append_to_sheet(spreadsheet_id, range_name, values):
    """
    Appends values to a Google Sheet.
    
    Args:
        spreadsheet_id: The ID of the spreadsheet to write to
        range_name: The A1 notation of the range to write to
        values: List of rows to append. Each row should be a list of values.
        
    Returns:
        The result of the append operation
    """
    try:
        service = get_sheets_service()
        sheet = service.spreadsheets()
        
        body = {
            'values': values
        }
        
        result = sheet.values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        
        return result
    except HttpError as err:
        print(f"An error occurred: {err}")
        return None

# Example usage
if __name__ == "__main__":
    SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
    SAMPLE_RANGE_NAME = "Sheet1!A:K"
    
    # Example data to append
    sample_values = [
        [datetime.now(tz=timezone('Asia/Singapore')).strftime('%Y-%m-%d %H:%M:%S'), 0.78, 0.8, 0.5, 0.8, 0.72, 100000, 101500, (101500 - 100000) / 100000, 103500, (103500 - 100000) / 100000]  # Timestamp and other values
    ]
    
    result = append_to_sheet(SPREADSHEET_ID, SAMPLE_RANGE_NAME, sample_values)
    if result:
        print(f"Appended {result.get('updates').get('updatedRows')} rows.")
