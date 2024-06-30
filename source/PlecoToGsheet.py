import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

CurrentWorkSheet="Sheet25"

def process_chinese_file(file_path):
    # Initialize an empty list to hold the 2D array
    result_array = []

    # Open and read the file
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # Split the line into components
            parts = line.split()
            
            # Extract the second word
            second_word = parts[1]
            
            # Extract the rest of the line starting with the fourth word
            rest_of_line = " ".join(parts[3:])
            
            # Append the second word and rest of the line as a sublist to the result array
            result_array.append([second_word, rest_of_line])

    return result_array

def upload_to_google_sheet(data, sheet_name):
    scope = ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('C:\\Users\\ascemama\\Documents\\Private\\Chinese\\chinese-vocabulary-storage-d11d329ddf29.json', scope)
    client = gspread.authorize(creds)

    sheet = client.open('ChineseVocab').worksheet(sheet_name)
    current_date = datetime.now().strftime('%Y/%m/%d')

    for row in data:
        sheet.append_row([current_date, row[1], row[0]])

# Example usage:
file_path = 'source/pleco.txt'  # Replace with the path to your file
result = process_chinese_file(file_path)
upload_to_google_sheet(result,CurrentWorkSheet)
print("Done !")
#for row in result:
#    print(row)
