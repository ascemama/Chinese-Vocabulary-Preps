import gspread
from datetime import datetime
import time
from oauth2client.service_account import ServiceAccountCredentials

from config import CREDS_PATH

def retrieveDoc(fileName):
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_PATH, scope)
    client = gspread.authorize(creds)
    chineseVocabDoc = client.open(fileName)
    return chineseVocabDoc




def open_spreadsheet(spreadsheet_name):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_PATH, scope)
    client = gspread.authorize(creds)
    return client.open(spreadsheet_name)

def upload_to_google_sheet(data, fileName, sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_PATH, scope)
    client = gspread.authorize(creds)

    sheet = client.open(fileName).worksheet(sheet_name)
    current_date = datetime.now().strftime('%Y/%m/%d')

    for row in data:
        sheet.append_row([current_date, row[1], row[0]])
        #Google sheet rate limit 60 write / minute
        time.sleep(1)
