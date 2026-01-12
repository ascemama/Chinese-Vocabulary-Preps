# Chinese-Vocabulary-Preps
Tool to enable weekly creation of artifacts to study Chinese vocabulary.

## Setup
Vocabulary must be entered in a Google Sheet. [Datum, Traduction, Source]

## Scripts
Download the Google Sheet content as JSON and print words in an A4 Word document which can be folded for easier study.

Export a range from a worksheet to a CSV for Anki (columns B and C):
```powershell
python source\exportToAnkiCSV.py ChineseVocab Sheet34 228 300 -o source\anki_export.csv
```
