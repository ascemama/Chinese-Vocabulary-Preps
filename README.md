# Chinese-Vocabulary-Preps
Tooling to prepare weekly Chinese/Arabic vocabulary study artifacts from Google Sheets and local notebook exports.

## Prerequisites
- Install `uv`: [https://docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/)
- Ensure Google service account credentials path in `source/config.py` is valid on your machine.

## Install dependencies with uv
If your system Python was removed, install one managed by uv:

```powershell
uv python install 3.12
```

From repo root, create/update the project environment and dependencies:

```powershell
uv sync
```

This creates/refreshes `.venv` and installs dependencies from `pyproject.toml`.

## Run scripts with uv
Run scripts through uv so they always use the project environment.

Worksheet destinations and Word-export progress are configured in
`source/config.py`. Update that file when a worksheet fills up or the Word
export moves to a new worksheet or starting row.

Build weekly Chinese vocabulary `.docx`:
```powershell
uv run python source\ChineseVocab.py
```

Import Chinese notebook entries to DB and Google Sheet:
```powershell
uv run python source\notebookToGsheet.py
```

Import Pleco export to DB and Google Sheet (interactive):
```powershell
uv run python source\plecoToGsheet.py
```

Import Arabic notebook entries to DB and Google Sheet:
```powershell
uv run python source\arabicToGsheet.py
```

Export a worksheet range to Anki CSV (columns B and C):
```powershell
uv run python source\exportToAnkiCSV.py ChineseVocab Sheet34 228 300 -o source\anki_export.csv
```

One-off DB maintenance script:
```powershell
uv run python source\manipulateDB.py
```

## Optional: OpenAI translation helper
`source/sqlLite.py` can call `source/openai.py` for translation suggestions.

Set a credential file at `source/openAI.cred` (ignored by git), or define:
- `OPENAI_CREDENTIAL_FILE`
- `OPENAI_API_URL` (optional override)
- `OPENAI_TRANSLATION_MODEL` (optional override)
