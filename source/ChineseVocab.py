from datetime import date

from config import ChineseWorkSheetForWordExport, ChineseWordExportFromLine
from gSheetHelper import retrieveDoc
from docHelper import createNewWordDoc, addNewWords

### Main
chineseVocabDoc=retrieveDoc("ChineseVocab")
newDoc=createNewWordDoc()
#addWordsToBeReReviewed(chineseVocabDoc,newDoc)
addNewWords(
    chineseVocabDoc,
    newDoc,
    ChineseWorkSheetForWordExport,
    ChineseWordExportFromLine,
)
newDoc.save('./vocab_chinese_'+str(date.today())+'.docx')
