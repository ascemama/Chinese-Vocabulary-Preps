from datetime import date
from gSheetHelper import retrieveDoc
from config import CREDS_PATH
from docHelper import createNewWordDoc, addNewWords
#which sheet and from which line should we start exporting
ExportSheetNameList=["Sheet8","Sheet9","Sheet10","Sheet12","Sheet14","Sheet15","Sheet16","Sheet17", "Sheet18", "Sheet19","Sheet20", "Sheet21","Sheet22","Sheet23","Sheet24","Sheet25", "Sheet26","Sheet27","Sheet28","Sheet29","Sheet30","Sheet31","Sheet32","Sheet33","Sheet34","Sheet35"]
ExportFromLine=3737

### Main
chineseVocabDoc=retrieveDoc("ChineseVocab")
newDoc=createNewWordDoc()
#addWordsToBeReReviewed(chineseVocabDoc,newDoc)
addNewWords(chineseVocabDoc,newDoc,ExportSheetNameList,ExportFromLine)
newDoc.save('./vocab_chinese_'+str(date.today())+'.docx')
