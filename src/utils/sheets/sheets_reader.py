from googleapiclient.errors import HttpError
from sheets_auth import get_sheets_service
from dotenv import load_dotenv
import os

load_dotenv()

def read_sheet_range(spreadsheet_id, range_name):
    """
    Reads data from a specified range in a Google Sheet.
    
    Args:
        spreadsheet_id: The ID of the spreadsheet to read from
        range_name: The A1 notation of the range to read
        
    Returns:
        List of rows containing the values in the specified range
    """
    try:
        service = get_sheets_service()
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        
        return result.get('values', [])
    except HttpError as err:
        print(f"An error occurred: {err}")
        return None

# Example usage
if __name__ == "__main__":
    SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
    SAMPLE_RANGE_NAME = "Sheet1!A2:K"
    
    values = read_sheet_range(SPREADSHEET_ID, SAMPLE_RANGE_NAME)
    print(values)
    if values:
        print("fear_greed_score, reddit_score:")
        for row in values:
            if len(row) >= 5:  # Ensure row has enough columns
                print(f"{row[1]}, {row[4]}")
    else:
        print("No data found.")
