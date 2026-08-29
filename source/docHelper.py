from dragonmapper.transcriptions import numbered_to_accented

#pip3 install python-docx
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt
from docx.shared import Mm

def cellToText(value):
    """Return a Google Sheets cell value as text."""
    if value is None:
        return ""
    return str(value)

def addWordField(paragraph, fieldName, placeholderText="1"):
    run = paragraph.add_run()
    fieldBegin = OxmlElement("w:fldChar")
    fieldBegin.set(qn("w:fldCharType"), "begin")

    fieldInstruction = OxmlElement("w:instrText")
    fieldInstruction.set(qn("xml:space"), "preserve")
    fieldInstruction.text = " " + fieldName + " "

    fieldSeparate = OxmlElement("w:fldChar")
    fieldSeparate.set(qn("w:fldCharType"), "separate")

    fieldText = OxmlElement("w:t")
    fieldText.text = placeholderText

    fieldEnd = OxmlElement("w:fldChar")
    fieldEnd.set(qn("w:fldCharType"), "end")

    run._r.append(fieldBegin)
    run._r.append(fieldInstruction)
    run._r.append(fieldSeparate)
    run._r.append(fieldText)
    run._r.append(fieldEnd)
    return run

def addPageNumberFooter(section):
    footerParagraph = section.footer.paragraphs[0]
    footerParagraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    footerParagraph.text = ""

    runs = [
        footerParagraph.add_run("Page "),
        addWordField(footerParagraph, "PAGE"),
        footerParagraph.add_run(" of "),
        addWordField(footerParagraph, "NUMPAGES"),
    ]
    for run in runs:
        run.font.name = "Arial"
        run.font.size = Pt(9)

def createNewWordDoc():
    document = Document()
    #set A4
    section = document.sections[0]
    section.page_height = Mm(297)
    section.page_width = Mm(210)
    section.left_margin = Mm(5)
    section.right_margin = Mm(5)
    section.top_margin = Mm(5)
    section.bottom_margin = Mm(5)
    section.header_distance = Mm(1)
    section.footer_distance = Mm(5)
    addPageNumberFooter(section)
    style = document.styles['Normal']
    font = style.font
    font.name = 'Arial'
    font.size = Pt(11)  #100 characters per line
    return document

#for those words that were not learned well in the last weeks
def addWordsToBeReReviewed(ChineseVocabDoc, newDoc):
    lineChinese=""
    lineTraduction=""
    isLastLine=False
    sheets = ChineseVocabDoc.worksheets()
    for sheet in sheets:
        records_data = sheet.get_all_records()
         
        records_length=len(records_data)
        for idx in range(0,records_length):
            if(records_data[idx]["ToBeReviewed"]=="x"):
                source=cellToText(records_data[idx]["Source"])
                traduction=cellToText(records_data[idx]["Traduction"])
                SourceLen=len(numbered_to_accented(source))
                traductionLen=len(traduction)

                if(idx==(records_length-1)):
                    isLastLine=True

                if ((len(lineChinese)+SourceLen > 40) or (len(lineTraduction)+traductionLen > 40)):
                    padding=" "*(90-len(lineTraduction))
                    newDoc.add_paragraph(lineTraduction+padding+lineChinese)
                    lineChinese=numbered_to_accented(source)
                    lineTraduction=traduction
                else:
                    if idx==0:
                        lineChinese=numbered_to_accented(source)
                        lineTraduction=traduction
                    if (isLastLine):
                        lineChinese=lineChinese+"/"+numbered_to_accented(source)
                        lineTraduction=lineTraduction+"/"+traduction
                    else:
                        lineChinese=lineChinese+"/"+numbered_to_accented(source)
                        lineTraduction=lineTraduction+"/"+traduction
        
                if(isLastLine):
                    padding=" "*(90-len(lineTraduction))
                    newDoc.add_paragraph(lineTraduction+padding+lineChinese)

def addNewWords(ChineseVocabDoc, newDoc, exportSheetName, exportFromLine):
    lineChinese=""
    lineTraduction=""
    isLastLine=False
    sheet_instance=ChineseVocabDoc.worksheet(exportSheetName)
    #print(sheet_instance)
    records_data = sheet_instance.get_all_records()
    records_length=len(records_data)
    for idx in range(exportFromLine,records_length):
        source=cellToText(records_data[idx]["Source"])
        traduction=cellToText(records_data[idx]["Traduction"])
        SourceLen=len(numbered_to_accented(source))
        traductionLen=len(traduction)
        #print("add new words "+traduction)
        if(idx==(records_length-1)):
            isLastLine=True

        if ((len(lineChinese)+SourceLen > 40) or (len(lineTraduction)+traductionLen > 40)):
            padding=" "*(90-len(lineTraduction))
            newDoc.add_paragraph(lineTraduction+padding+lineChinese)
            lineChinese=numbered_to_accented(source)
            lineTraduction=traduction
        else:
            if idx==0:
                lineChinese=numbered_to_accented(source)
                lineTraduction=traduction
            if (isLastLine):
                lineChinese=lineChinese+"/"+numbered_to_accented(source)
                lineTraduction=lineTraduction+"/"+traduction
            else:
                lineChinese=lineChinese+"/"+numbered_to_accented(source)
                lineTraduction=lineTraduction+"/"+traduction
        
        if(isLastLine):
            padding=" "*(90-len(lineTraduction))
            newDoc.add_paragraph(lineTraduction+padding+lineChinese)
 
