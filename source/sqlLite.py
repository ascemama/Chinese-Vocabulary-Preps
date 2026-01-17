import sqlite3
import datetime
import sys
#from datetime import date
#from gSheet import retrieveDoc, ExportSheetNameList

#ExportFromLine=3

# Ensure Unicode (e.g., Arabic) renders correctly on Windows consoles.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

try:
    import arabic_reshaper
except ImportError:
    arabic_reshaper = None

try:
    from bidi.algorithm import get_display
except ImportError:
    get_display = None


def format_rtl(text):
    if not text:
        return text
    if arabic_reshaper and get_display:
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    if arabic_reshaper:
        return arabic_reshaper.reshape(text)
    return text

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
    connection.commit()
    cursor.close()
    connection.close()

def addRowToDB(source, traduction,cursor,tableName):
    current_date = datetime.date.today()
    try:
        cursor.execute(f'INSERT INTO {tableName} (date, source, translation) VALUES (?, ?, ?)', (current_date, source,traduction))
    except sqlite3.IntegrityError as e:
    # Handle UNIQUE constraint violation error
        print(f'Error: {e}, source {source}, translation {traduction}')

def updateTraductionInDB(source,traduction, cursor, connection,tableName):
    
    try:
        cursor.execute(f'UPDATE {tableName} SET translation = ? WHERE source = ?',(traduction,source))
        connection.commit()
    except sqlite3.IntegrityError as e:
    # Handle UNIQUE constraint violation error
        print(f'Error: {e}, source {source}, translation {traduction}') 
        exit()  

def checkIfAlreadyExistInDB(source,cursor, tableName):
    cursor.execute(f'SELECT * FROM {tableName} WHERE source = ? LIMIT 1;', (source,))
    return bool(cursor.fetchall())

#check if traduction already exist in DB. Ask if the new traduction should be kept in DB instead
def updateDBWithNewWordFromNotebook(source,traduction, cursor,connection,tableName):
    cursor.execute(f'SELECT * FROM {tableName} WHERE source = ? LIMIT 1;', (source,))
     
    row=cursor.fetchall()
    #if already exist and with a different traduction. Need to chose which trad to keep
    if bool(row) and (traduction != row[0][3]):
        print(source+" already exist in DB. Choose which one to keep:")
        print("1- "+row[0][3])
        print("2- "+traduction)
        while (True):
            user_input = input("Enter 1 or 2, or a new traduction: ")
            if user_input =="1":
                return row[0][3]
            elif user_input == "2":
                updateTraductionInDB(source,traduction,cursor,connection,tableName)
                return traduction
            else:
                updateTraductionInDB(source,user_input,cursor,connection,tableName)
                return user_input
    #if not in DB yet
    if not bool(row):
        addRowToDB(source,traduction,cursor,tableName)
        connection.commit()
        return traduction
    #if in DB already with the same traduction
    else:
        return traduction


def updateDBWithNewWord(source,traduction, cursor,connection,tableName):
    cursor.execute(f'SELECT * FROM {tableName} WHERE source = ? LIMIT 1;', (source,))
     
    row=cursor.fetchall()
    #if already exist and with a different traduction. Need to chose which trad to keep
    if bool(row) and (traduction != row[0][3]):
        print("\n"+format_rtl(source)+" already exist in DB. Choose which one to keep:")
        print("1- "+format_rtl(row[0][3]))
        print("2- "+format_rtl(traduction))
        while (True):
            user_input = input("Enter 1,2,x to discard this word,y for finishing and updating DB, z for finishing updating DB and Gsheet, or a new traduction:\n")
            if user_input =="1":
                return row[0][3]
            elif user_input == "2":
                updateTraductionInDB(source,traduction,cursor,connection,tableName)
                return traduction
            elif user_input == "x":
                return "x"
            elif user_input == "y":
                return "y"
            elif user_input == "z":
                return "z"
            else:
                updateTraductionInDB(source,user_input,cursor,connection,tableName)
                return user_input
    #if not in DB yet, need to reformulate the traduction from pleco
    if not bool(row):
        print("\nsource: "+format_rtl(source)+ "\nTraduction: "+format_rtl(traduction))
        user_input = input("Type 1 to keep this traduction. type x to discard this word, y for finishing and updating DB,z for finishing updating DB and Gsheet\nOtherwise, what should be the traduction:\n")
        if(user_input == "1"):
            addRowToDB(source,traduction,cursor,tableName)
            connection.commit()
            return traduction
        if(user_input == "x"):
            return "x"
        elif user_input == "y":
                return "y"
        elif user_input == "z":
                return "z"
        else:
            addRowToDB(source,user_input,cursor,tableName)
            connection.commit()
            return user_input
    #if in DB already with the same traduction
    else:
        print("\nsource: "+format_rtl(source)+ "\nTraduction: "+format_rtl(traduction))
        user_input = input("Type 1 to keep this traduction. type x to discard this word,y for finishing and updating DB,z for finishing updating DB and Gsheet\nOtherwise, what should be the traduction:\n")
        if(user_input == "1"):
            return traduction
        elif user_input == "y":
                return "y"
        elif user_input == "z":
                return "z"
        elif user_input == "x":
                return "x"
        else:
            updateTraductionInDB(source,user_input,cursor,connection,tableName)
            return user_input

#check if traduction already exist in DB. Ask if the new traduction should be kept in DB instead
def updateDBWithNewWordFromPleco(source,traduction, cursor,connection,tableName):
    cursor.execute(f'SELECT * FROM {tableName} WHERE source = ? LIMIT 1;', (source,))
     
    row=cursor.fetchall()
    #if already exist and with a different traduction. Need to chose which trad to keep
    if bool(row) and (traduction != row[0][3]):
        print("\n"+format_rtl(source)+" already exist in DB. Choose which one to keep:")
        print("1- "+format_rtl(row[0][3]))
        print("2- "+format_rtl(traduction))
        while (True):
            user_input = input("Enter 1,2,x to discard this word,y for finishing and updating DB, z for finishing updating DB and Gsheet, or a new traduction:\n")
            if user_input =="1":
                return row[0][3]
            elif user_input == "2":
                updateTraductionInDB(source,traduction,cursor,connection,tableName)
                return traduction
            elif user_input == "x":
                return "x"
            elif user_input == "y":
                return "y"
            elif user_input == "z":
                return "z"
            else:
                updateTraductionInDB(source,user_input,cursor,connection,tableName)
                return user_input
    #if not in DB yet, need to reformulate the traduction from pleco
    if not bool(row):
        print("\nsource: "+format_rtl(source)+ "\nTraduction: "+format_rtl(traduction))
        user_input = input("Type 1 to keep this traduction. type x to discard this word, y for finishing and updating DB,z for finishing updating DB and Gsheet\nOtherwise, what should be the traduction:\n")
        if(user_input == "1"):
            addRowToDB(source,traduction,cursor,tableName)
            connection.commit()
            return traduction
        if(user_input == "x"):
            return "x"
        elif user_input == "y":
                return "y"
        elif user_input == "z":
                return "z"
        else:
            addRowToDB(source,user_input,cursor,tableName)
            connection.commit()
            return user_input
    #if in DB already with the same traduction
    else:
        print("\nsource: "+format_rtl(source)+ "\nTraduction: "+format_rtl(traduction))
        user_input = input("Type 1 to keep this traduction. type x to discard this word,y for finishing and updating DB,z for finishing updating DB and Gsheet\nOtherwise, what should be the traduction:\n")
        if(user_input == "1"):
            return traduction
        elif user_input == "y":
                return "y"
        elif user_input == "z":
                return "z"
        elif user_input == "x":
                return "x"
        else:
            updateTraductionInDB(source,user_input,cursor,connection,tableName)
            return user_input

def addExcelSheetToDB(sheet,cursor,connection):
    records_data = sheet.get_all_records()
    records_length=len(records_data)
    print("length:"+ str(records_length))
    for idx in range(1,records_length):
        source=records_data[idx]["source"]
        traduction=records_data[idx]["Traduction"]
        print("source / translation : "+source + traduction)
        addRowToDB(source,traduction,cursor)
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


