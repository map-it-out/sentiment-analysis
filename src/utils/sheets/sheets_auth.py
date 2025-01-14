import os.path
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/spreadsheets"
]

def get_credentials():
    """Gets valid service account credentials.
    
    Returns:
        Credentials, the obtained credential.
    """
    return Credentials.from_service_account_file(
        "credentials.json",
        scopes=SCOPES
    )

def get_sheets_service():
    """Creates and returns Google Sheets API service instance."""
    creds = get_credentials()
    return build("sheets", "v4", credentials=creds)
