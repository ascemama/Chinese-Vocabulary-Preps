from source.gSheetHelper import upload_to_google_sheet, CurrentChineseWorksheet
from sqlLite import openDB,closeDB,updateDBWithNewWordFromNotebook
 
def process_chinese_notebook_file(file_path,cursor,connection):
    # Initialize an empty list to hold the 2D array
    result_array = []

    # Open and read the file
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # Split the line into components
            if(line.strip()):
                parts = line.split(":")
                traduction = parts[0].strip().replace("\n","")
                pinyin = parts[1].strip().replace("\n","")
                traduction=updateDBWithNewWordFromNotebook(pinyin,traduction,cursor,connection)
                result_array.append([pinyin, traduction])

    return result_array
 
 
file_path = 'source/notebook.txt'  # Replace with the path to your file

cursor, connection=openDB()
result = process_chinese_notebook_file(file_path,cursor,connection)
closeDB(cursor,connection)

for item in result:
    print(item)


upload_to_google_sheet(result, "ChineseVocab", CurrentChineseWorksheet)

print("Done !")

