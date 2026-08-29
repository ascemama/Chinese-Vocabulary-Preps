import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import Mock, patch


SOURCE_DIR = Path(__file__).resolve().parents[1] / "source"
sys.path.insert(0, str(SOURCE_DIR))

import config
import docHelper
import gSheetHelper
import plecoToGsheet


class WordExportConfigurationTests(unittest.TestCase):
    def test_add_new_words_uses_single_configured_worksheet(self):
        spreadsheet = Mock()
        worksheet = spreadsheet.worksheet.return_value
        worksheet.get_all_records.return_value = []

        docHelper.addNewWords(
            spreadsheet,
            Mock(),
            config.ChineseWorkSheetForWordExport,
            config.ChineseWordExportFromLine,
        )

        spreadsheet.worksheet.assert_called_once_with("Sheet35")


class NewWordUploadConfigurationTests(unittest.TestCase):
    def test_upload_path_uses_configured_sheet_36_destination(self):
        result = plecoToGsheet.PlecoProcessingResult(
            rows=[["ni3", "you"]],
            should_upload=True,
        )
        uploader = Mock()

        with (
            patch.object(plecoToGsheet, "openDB", return_value=(Mock(), Mock())),
            patch.object(plecoToGsheet, "closeDB"),
            patch.object(
                plecoToGsheet,
                "process_chinese_pleco_file",
                return_value=result,
            ),
            patch.object(plecoToGsheet, "print_statistics"),
            patch.object(gSheetHelper, "upload_to_google_sheet", uploader),
            redirect_stdout(io.StringIO()),
        ):
            plecoToGsheet.main()

        uploader.assert_called_once_with(
            [["ni3", "you"]],
            "ChineseVocab",
            "Sheet36",
        )


if __name__ == "__main__":
    unittest.main()
