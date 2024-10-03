import sqlite3
import datetime
#from datetime import date
#from gSheet import retrieveDoc, ExportSheetNameList

#ExportFromLine=3

# Adapter function for datetime.date
def adapt_date(date_obj):
    return date_obj.isoformat()

# Converter function for datetime.date
def convert_date(date_str):
    return datetime.date.fromisoformat(date_str.decode())
 
def openDB():
    sqlite3.register_adapter(datetime.date, adapt_date)
    sqlite3.register_converter('DATE', convert_date)
    connection = sqlite3.connect('./source/vocabulary.db',detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = connection.cursor()
    return cursor, connection

def closeDB(cursor,connection):
    cursor.close()
    connection.close()

def addRowToDB(pinyin, traduction,cursor):
    current_date = datetime.date.today()
    try:
        cursor.execute('''INSERT INTO vocabulary (date, pinyin, translation) VALUES (?, ?, ?)''', (current_date, pinyin,traduction))
    except sqlite3.IntegrityError as e:
    # Handle UNIQUE constraint violation error
        print(f'Error: {e}, Pinyin {pinyin}, translation {traduction}')

def updateTraductionInDB(pinyin,traduction, cursor, connection):
    try:
        cursor.execute("UPDATE vocabulary SET translation = ? WHERE pinyin = ?",(traduction,pinyin))
        connection.commit()
    except sqlite3.IntegrityError as e:
    # Handle UNIQUE constraint violation error
        print(f'Error: {e}, Pinyin {pinyin}, translation {traduction}') 
        exit()  

def checkIfAlreadyExistInDB(pinyin,cursor):
    cursor.execute('''SELECT * FROM vocabulary WHERE pinyin = ? LIMIT 1;''', (pinyin,))
    return bool(cursor.fetchall())

#check if traduction already exist in DB. Ask if the new traduction should be kept in DB instead
def updateDBWithNewWordFromNotebook(pinyin,traduction, cursor,connection):
    cursor.execute('''SELECT * FROM vocabulary WHERE pinyin = ? LIMIT 1;''', (pinyin,))
     
    row=cursor.fetchall()
    #if already exist and with a different traduction. Need to chose which trad to keep
    if bool(row) and (traduction != row[0][3]):
        print(pinyin+" already exist in DB. Choose which one to keep:")
        print("1- "+row[0][3])
        print("2- "+traduction)
        while (True):
            user_input = input("Enter 1 or 2, or a new traduction: ")
            if user_input =="1":
                return row[0][3]
            elif user_input == "2":
                updateTraductionInDB(pinyin,traduction,cursor,connection)
                return traduction
            else:
                updateTraductionInDB(pinyin,user_input,cursor,connection)
                return user_input
    #if not in DB yet
    if not bool(row):
        addRowToDB(pinyin,traduction,cursor)
        connection.commit()
        return traduction
    #if in DB already with the same traduction
    else:
        return traduction
        
#check if traduction already exist in DB. Ask if the new traduction should be kept in DB instead
def updateDBWithNewWordFromPleco(pinyin,traduction, cursor,connection):
    cursor.execute('''SELECT * FROM vocabulary WHERE pinyin = ? LIMIT 1;''', (pinyin,))
     
    row=cursor.fetchall()
    #if already exist and with a different traduction. Need to chose which trad to keep
    if bool(row) and (traduction != row[0][3]):
        print("\n"+pinyin+" already exist in DB. Choose which one to keep:")
        print("1- "+row[0][3])
        print("2- "+traduction)
        while (True):
            user_input = input("Enter 1 or 2, or a new traduction:\n")
            if user_input =="1":
                return row[0][3]
            elif user_input == "2":
                updateTraductionInDB(pinyin,traduction,cursor,connection)
                return traduction
            else:
                updateTraductionInDB(pinyin,user_input,cursor,connection)
                return user_input
    #if not in DB yet, need to reformulate the traduction from pleco
    if not bool(row):
        print("\nPinyin: "+pinyin+ "\nTraduction: "+traduction)
        user_input = input("Type 1 to keep this traduction. type x to discard this word.\nOtherwise, what should be the traduction:\n")
        if(user_input == "1"):
            addRowToDB(pinyin,traduction,cursor)
        if(user_input == "x"):
            return "x"
        else:
            addRowToDB(pinyin,user_input,cursor)
        connection.commit()
        return traduction
    #if in DB already with the same traduction
    else:
        return traduction

def addExcelSheetToDB(sheet,cursor,connection):
    records_data = sheet.get_all_records()
    records_length=len(records_data)
    print("length:"+ str(records_length))
    for idx in range(1,records_length):
        pinyin=records_data[idx]["Pinyin"]
        traduction=records_data[idx]["Traduction"]
        print("pinyin / translation : "+pinyin + traduction)
        addRowToDB(pinyin,traduction,cursor)
    connection.commit()


############### Main #################
if __name__ == "__main__":

    print("open DB")
    cursor,connection=openDB()
    updateTraductionInDB("Fo2zhou1","Floride",cursor,connection)
    #print(checkIfAlreadyExistInDBAndAskWhichTraductionToKeep("dai4tao4","abc",cursor))

    ''''
    print("RetrieveDoc")
    ChineseVocabDoc=retrieveDoc()
    sheet_instance=ChineseVocabDoc.worksheet(ExportSheetNameList[-2])
    print("Add rows to DB")
    addExcelSheetToDB(sheet_instance,cursor,connection)
    print("CloseDB")
    closeDB(cursor,connection)
'''


