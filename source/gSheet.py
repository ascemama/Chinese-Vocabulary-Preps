import gspread
from datetime import datetime
import time
from oauth2client.service_account import ServiceAccountCredentials
 


ExportSheetNameList=["Sheet8","Sheet9","Sheet10","Sheet12","Sheet14","Sheet15","Sheet16","Sheet17", "Sheet18", "Sheet19","Sheet20", "Sheet21","Sheet22","Sheet23","Sheet24","Sheet25", "Sheet26","Sheet27","Sheet28","Sheet29","Sheet30"] 
CurrentWorkSheet="Sheet31"

def retrieveDoc():
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('C:\\Users\\ascemama\\Documents\\Private\\Chinese\\chinese-vocabulary-storage-d11d329ddf29.json', scope)
    client = gspread.authorize(creds)
    chineseVocabDoc = client.open('ChineseVocab')
    return chineseVocabDoc



def upload_to_google_sheet(data, sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('C:\\Users\\ascemama\\Documents\\Private\\Chinese\\chinese-vocabulary-storage-d11d329ddf29.json', scope)
    client = gspread.authorize(creds)

    sheet = client.open('ChineseVocab').worksheet(sheet_name)
    current_date = datetime.now().strftime('%Y/%m/%d')

    for row in data:
        sheet.append_row([current_date, row[1], row[0]])
        #Google sheet rate limit 60 write / minute
        time.sleep(1)
