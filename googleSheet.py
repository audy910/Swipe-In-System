from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

# Your Google Sheet ID (from the URL)
SHEET_ID = "12OBOqkx65LgKyfARJvX0v0qAEbl1umjTV3fogmZm7pM"
RANGE = "Sheet1!A1"

def write_row_to_sheet(values):
    creds = Credentials.from_service_account_file(
        "service_account.json",
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets().values()

    result = sheet.append(
        spreadsheetId=SHEET_ID,
        range="Sheet1!A:F",
        valueInputOption="USER_ENTERED",
        body={"values": [values]}
    ).execute()

    # Google Sheets returns where it wrote the row: "Sheet1!A12"
    updated_range = result.get("updates", {}).get("updatedRange")
    # Extract row number
    row = int(updated_range.split("!A")[1])
    return row

def update_return_date(row_number, return_date):
    creds = Credentials.from_service_account_file(
        "service_account.json",
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets().values()

    # "F" is the 6th column (Date of Return)
    range_str = f"Sheet1!F{row_number}"

    sheet.update(
        spreadsheetId=SHEET_ID,
        range=range_str,
        valueInputOption="USER_ENTERED",
        body={"values": [[return_date]]}
    ).execute()

