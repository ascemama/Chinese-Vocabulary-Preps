from gSheetHelper import upload_to_google_sheet, CurrentArabicWorksheet
from sqlLite import openDB,closeDB,updateDBWithNewWord
 
def process_arabic_notebook_file(file_path,cursor,connection):
    # Initialize an empty list to hold the 2D array
    result_array = []

    # Open and read the file
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # Split the line into components
            if(line.strip()):
                parts = line.split(":")
                traduction = parts[0].strip().replace("\n","")
                arabic = parts[1].strip().replace("\n","")
                traduction=updateDBWithNewWord(arabic,traduction,cursor,connection,"arabic")
                result_array.append([arabic, traduction])

    return result_array
 
 
file_path = 'source/arabic_vocabulary.txt'  # Replace with the path to your file

cursor, connection=openDB()
result = process_arabic_notebook_file(file_path,cursor,connection)
closeDB(cursor,connection)

for item in result:
    print(item)


upload_to_google_sheet(result, "Arabic", CurrentArabicWorksheet)

print("Done !")
