from oauth2client.service_account import ServiceAccountCredentials
from gSheet import upload_to_google_sheet,CurrentWorkSheet
from sqlLite import openDB,closeDB,updateDBWithNewWordFromPleco


def process_chinese_pleco_file(file_path,cursor, connection):
    # Initialize an empty list to hold the 2D array
    result_array = []

    # Open and read the file
    with open(file_path, 'r', encoding='utf-8') as file:
        lines=file.readlines()
        nbVoc=len(lines)
        idx=0
        for line in lines:
            idx=idx+1
            
            if(line.strip()):
                parts = line.split()
                pinyin = parts[1].strip().replace("\n","")
                traduction = " ".join(parts[3:]).strip().replace("\n","")
                print("\n ----- "+str(idx)+"/"+str(nbVoc)+" ----- \n"+pinyin+" -- "+traduction)
                traduction=updateDBWithNewWordFromPleco(pinyin,traduction,cursor,connection)
                # x means we discard this word
                if(traduction != "x"):
                    result_array.append([pinyin, traduction])

    return result_array

 
file_path = 'source/pleco.txt'  # Replace with the path to your file
cursor, connection=openDB()
print(connection)
result = process_chinese_pleco_file(file_path,cursor,connection)
closeDB(cursor,connection)
print("Upload to google sheet")
upload_to_google_sheet(result,CurrentWorkSheet)
print("Done !") 
 
