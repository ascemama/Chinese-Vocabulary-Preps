import io
import sqlite3
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import Mock, patch


SOURCE_DIR = Path(__file__).resolve().parents[1] / "source"
sys.path.insert(0, str(SOURCE_DIR))

import plecoToGsheet


class PlecoProcessingTests(unittest.TestCase):
    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.cursor = self.connection.cursor()
        self.cursor.execute(
            "CREATE TABLE chinese (source TEXT UNIQUE, translation TEXT)"
        )

    def tearDown(self):
        self.cursor.close()
        self.connection.close()

    def _process(self, lines, responses, existing=()):
        self.cursor.executemany(
            "INSERT INTO chinese (source, translation) VALUES (?, ?)", existing
        )
        self.connection.commit()

        with tempfile.TemporaryDirectory() as temporary_directory:
            file_path = Path(temporary_directory) / "pleco.txt"
            file_path.write_text("".join(lines), encoding="utf-8")
            with patch.object(
                plecoToGsheet,
                "updateDBWithNewWordFromPleco",
                side_effect=responses,
            ):
                output = io.StringIO()
                with redirect_stdout(output):
                    result = plecoToGsheet.process_chinese_pleco_file(
                        file_path, self.cursor, self.connection, "chinese"
                    )
        return result, output.getvalue()

    def test_end_of_file_tracks_new_existing_changed_and_discarded(self):
        lines = [
            "甲 p1 noun old-one\n",
            "乙 p2 noun pleco-two\n",
            "丙 p3 noun new-three\n",
            "丁 p4 noun discarded-four\n",
        ]
        result, output = self._process(
            lines,
            ["old-one", "changed-two", "new-three", "x"],
            existing=(("p1", "old-one"), ("p2", "old-two")),
        )

        self.assertTrue(result.should_upload)
        self.assertEqual(
            result.rows,
            [["p1", "old-one"], ["p2", "changed-two"], ["p3", "new-three"]],
        )
        self.assertEqual(result.statistics.total_entries, 4)
        self.assertEqual(result.statistics.processed_entries, 4)
        self.assertEqual(result.statistics.already_in_db, 2)
        self.assertEqual(result.statistics.not_in_db, 2)
        self.assertEqual(result.statistics.changed_in_db, 1)
        self.assertEqual(
            result.statistics.already_in_db + result.statistics.not_in_db,
            result.statistics.processed_entries,
        )
        self.assertLessEqual(
            result.statistics.changed_in_db, result.statistics.already_in_db
        )
        self.assertNotIn("Pleco import statistics", output)

        report = plecoToGsheet.format_statistics(result.statistics)
        self.assertIn("Total entries in pleco.txt: 4 (100.0%)", report)
        self.assertIn("Entries processed: 4 (100.0%)", report)
        self.assertIn("Initially already in DB: 2 (50.0%)", report)
        self.assertIn("Initially not in DB: 2 (50.0%)", report)
        self.assertIn("Already in DB but changed: 1 (25.0%)", report)

    def test_y_stops_without_upload_and_counts_terminating_word(self):
        lines = [
            "甲 p1 noun discarded\n",
            "乙 p2 noun stop\n",
            "丙 p3 noun unreached\n",
        ]
        result, _ = self._process(lines, ["x", "y"], existing=(("p2", "old"),))

        self.assertFalse(result.should_upload)
        self.assertEqual(result.rows, [])
        self.assertEqual(result.statistics.total_entries, 3)
        self.assertEqual(result.statistics.processed_entries, 2)
        self.assertEqual(result.statistics.already_in_db, 1)
        self.assertEqual(result.statistics.not_in_db, 1)

    def test_z_stops_with_upload_and_counts_terminating_word(self):
        lines = ["甲 p1 noun first\n", "乙 p2 noun stop\n", "丙 p3 noun last\n"]
        result, _ = self._process(lines, ["first", "z"])

        self.assertTrue(result.should_upload)
        self.assertEqual(result.rows, [["p1", "first"]])
        self.assertEqual(result.statistics.total_entries, 3)
        self.assertEqual(result.statistics.processed_entries, 2)

    def test_empty_file_formats_zero_percentages(self):
        result, _ = self._process(["\n", "   \n"], [])

        report = plecoToGsheet.format_statistics(result.statistics)
        self.assertEqual(result.statistics.total_entries, 0)
        self.assertEqual(result.statistics.processed_entries, 0)
        self.assertEqual(report.count("(0.0%)"), 5)


class UploadBehaviorTests(unittest.TestCase):
    def test_upload_is_skipped_for_y(self):
        uploader = Mock()
        result = plecoToGsheet.PlecoProcessingResult(should_upload=False)

        uploaded = plecoToGsheet.upload_if_requested(
            result, uploader, "spreadsheet", "worksheet"
        )

        self.assertFalse(uploaded)
        uploader.assert_not_called()

    def test_upload_occurs_for_z_or_end_of_file_result(self):
        for rows in ([["p1", "one"]], []):
            with self.subTest(rows=rows):
                uploader = Mock()
                result = plecoToGsheet.PlecoProcessingResult(
                    rows=rows, should_upload=True
                )
                with redirect_stdout(io.StringIO()):
                    uploaded = plecoToGsheet.upload_if_requested(
                        result, uploader, "spreadsheet", "worksheet"
                    )

                self.assertTrue(uploaded)
                uploader.assert_called_once_with(rows, "spreadsheet", "worksheet")


if __name__ == "__main__":
    unittest.main()
